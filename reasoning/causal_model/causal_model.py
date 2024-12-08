import torch
import torch.nn.functional as F
from torch import nn
import lightning as L
from torch_geometric.nn import GATv2Conv, MLP
from torch_geometric.loader import DataLoader
from matplotlib import pyplot as plt

from parameters import *
from utils import h_A


class NodeEncoder(nn.Module):
    def __init__(self, node_feature_dim):
        super(NodeEncoder, self).__init__()
        self.node_feature_dim = node_feature_dim
        self.node_emb = nn.ModuleDict()
        for k, v in NODE_DIM.items():
            self.node_emb[k] = nn.Sequential(
                nn.Linear(v, node_feature_dim),
                nn.Dropout(DROPOUT)
            ).to(DEVICE)

    def forward(self, batch_graph):
        node_feature = torch.zeros((batch_graph.num_nodes, self.node_feature_dim), dtype=torch.float, device=DEVICE)

        for k, f in self.node_emb.items():
            index = []
            for b in range(batch_graph.batch_size):
                node_name = batch_graph.node_name[b]
                try:
                    i = node_name.index(k)
                    index.append(batch_graph.ptr[b] + i)
                except ValueError:
                    continue
            x = batch_graph.x[index, :NODE_DIM[k]]
            y = f(x)
            node_feature[index, :] = y

        return node_feature


class GraphEncoder(nn.Module):
    def __init__(self, node_dim, head=2):
        super(GraphEncoder, self).__init__()
        self.node_dim = node_dim

        self.conv = GATv2Conv(self.node_dim, self.node_dim, heads=head, dropout=DROPOUT, add_self_loops=False)
        self.mu_encoder = GATv2Conv(self.node_dim * head, self.node_dim, heads=head, dropout=DROPOUT,
                                    add_self_loops=False)
        self.mu_fc = nn.Linear(self.node_dim * head, self.node_dim)
        self.logstd_encoder = GATv2Conv(self.node_dim * head, self.node_dim, heads=head, dropout=DROPOUT,
                                        add_self_loops=False)
        self.logstd_fc = nn.Linear(self.node_dim * head, self.node_dim)

    def forward(self, batch_graph, node_feature):
        edge_index = batch_graph.edge_index
        x = self.conv(node_feature, edge_index)

        mu = self.mu_fc(self.mu_encoder(x, edge_index))
        logstd = self.logstd_fc(self.logstd_encoder(x, edge_index))
        logstd = torch.clamp(logstd, max=MAX_LOGSTD)
        return mu, logstd


class CausalLayer(nn.Module):
    def __init__(self, sample_mode=False):
        super(CausalLayer, self).__init__()
        self.sample_mode = sample_mode

    def forward(self, batch_graph, A, mu, logstd):
        sigma = self.reparametrize(mu, logstd)
        I = torch.eye(A.shape[0], device=DEVICE)
        matrix = torch.pinverse(I - A.t())
        z = torch.zeros_like(sigma, device=DEVICE)

        for b in range(batch_graph.batch_size):
            node_name = batch_graph.node_name[b]
            node_index = [NODE_LST.index(n) for n in node_name]
            matrix_index = torch.meshgrid(torch.tensor(node_index), torch.tensor(node_index), indexing='ij')
            z[batch_graph.batch == b] = matrix[matrix_index] @ sigma[batch_graph.batch == b]

        return sigma, z

    def reparametrize(self, mu, logstd):
        if self.training or self.sample_mode:
            return mu + torch.randn_like(logstd) * torch.exp(logstd)
        else:
            return mu


class Mixer(nn.Module):
    def __init__(self, node_dim):
        super(Mixer, self).__init__()
        self.node_dim = node_dim

        self.norm = nn.LayerNorm(node_dim)
        self.mix_net = nn.ModuleDict()
        for k, v in NODE_DIM.items():
            self.mix_net[k] = MLP(
                in_channels=self.node_dim,
                hidden_channels=self.node_dim * 2,
                out_channels=self.node_dim,
                num_layers=2, dropout=DROPOUT, act=nn.ELU(), norm=None
            ).to(DEVICE)

    def forward(self, batch_graph, A, z):
        Az = self.A_z(batch_graph, A, z)
        Az = self.norm(Az)

        mix_feature = torch.zeros_like(Az, dtype=torch.float, device=DEVICE)
        for k, f in self.mix_net.items():
            index = []
            for b in range(batch_graph.batch_size):
                node_name = batch_graph.node_name[b]
                try:
                    i = node_name.index(k)
                    index.append(batch_graph.ptr[b] + i)
                except ValueError:
                    continue
            x = Az[index, :]
            y = f(x)
            mix_feature[index, :] = y
        return mix_feature + Az

    def A_z(self, batch_graph, A, z):
        Az = torch.zeros_like(z, device=DEVICE)

        for b in range(batch_graph.batch_size):
            node_name = batch_graph.node_name[b]
            node_index = [NODE_LST.index(n) for n in node_name]
            matrix_index = torch.meshgrid(torch.tensor(node_index), torch.tensor(node_index), indexing='ij')
            Az[batch_graph.batch == b] = A[matrix_index].t() @ z[batch_graph.batch == b]

        return Az


class NodeDecoder(nn.Module):
    def __init__(self, node_dim):
        super(NodeDecoder, self).__init__()
        self.node_dim = node_dim

        self.decoders = nn.ModuleDict()
        for k, v in NODE_DIM.items():
            self.decoders[k] = nn.Sequential(
                nn.Linear(node_dim, v),
                nn.Dropout(DROPOUT)
            ).to(DEVICE)

    def forward(self, batch_graph, embedding):
        x_recon = torch.zeros((batch_graph.num_nodes, MAX_DIM), dtype=torch.float, device=DEVICE)
        for k, f in self.decoders.items():
            index = []
            for b in range(batch_graph.batch_size):
                node_name = batch_graph.node_name[b]
                try:
                    i = node_name.index(k)
                    index.append(batch_graph.ptr[b] + i)
                except ValueError:
                    continue
            y = f(embedding[index, :])
            x_recon[index, :NODE_DIM[k]] = y

        return x_recon


class Model(L.LightningModule):
    def __init__(self, adj_matrix, node_feature_dim=8):
        super(Model, self).__init__()
        self.save_hyperparameters()

        self.adj_matrix = nn.Parameter(adj_matrix, requires_grad=True)
        self.node_feature_dim = node_feature_dim

        self.node_encoder = NodeEncoder(self.node_feature_dim)
        self.graph_encoder = GraphEncoder(self.node_feature_dim)
        self.causal_layer = CausalLayer()
        self.mix_layer = Mixer(self.node_feature_dim)

        self.skip_connect = MLP(
            in_channels=self.node_feature_dim,
            hidden_channels=self.node_feature_dim * 2,
            out_channels=self.node_feature_dim,
            num_layers=2, dropout=DROPOUT, act=nn.Mish()
        )

        self.node_decoder = NodeDecoder(self.node_feature_dim)

    def forward(self, batch_graph):
        node_feature = self.node_encoder(batch_graph)
        mu, logstd = self.graph_encoder(batch_graph, node_feature)
        sigma, z = self.causal_layer(batch_graph, self.adj_matrix, mu, logstd)
        f_z = self.mix_layer(batch_graph, self.adj_matrix, z)
        f_u = self.mix_layer(batch_graph, self.adj_matrix, node_feature)
        leak_information = self.skip_connect(sigma)
        encode = f_z + leak_information

        x_recon = self.node_decoder(batch_graph, encode)
        return x_recon, f_u, f_z, z, node_feature

    def recon_loss(self, batch_graph, x_recon):
        loss = 0
        x = batch_graph.x
        for b in range(batch_graph.batch_size):
            node_name = batch_graph.node_name[b]
            graph_loss = 0
            for i in range(len(node_name)):
                n = node_name[i]
                y = x[batch_graph.ptr[b] + i, :NODE_DIM[n]]
                y_pred = x_recon[batch_graph.ptr[b] + i, :NODE_DIM[n]]
                if n in CLASSIFY_NODE_LST:
                    graph_loss += F.cross_entropy(y_pred, y)
                elif n in REGRESSION_NODE_LST:
                    graph_loss += F.mse_loss(y_pred, y)
            loss += graph_loss / len(node_name)
        return loss / batch_graph.batch_size

    def cal_loss(self, batch_graph, x_recon, f_u, f_z, z, node_feature):
        rec_loss = self.recon_loss(batch_graph, x_recon)
        h_a = h_A(self.adj_matrix)
        kl_loss = F.kl_div((z.softmax(-1) + 1e-8).log(), node_feature.softmax(-1), reduction='batchmean')

        total_loss = rec_loss + kl_loss + 1 * h_a

        return total_loss, rec_loss, h_a, kl_loss

    def predict(self, batch_graph):
        test_data_lst = []
        r_lst = []
        error = []
        for b in range(batch_graph.batch_size):
            node_name = batch_graph.node_name[b]
            if 'roughness' in node_name:
                index = node_name.index('roughness')
                data = batch_graph[b].clone()
                r = batch_graph[b].x[index, :NODE_DIM['roughness']]
                data.x[index] = 0
                test_data_lst.append(data)
                r_lst.append(r.item())
        loader = DataLoader(test_data_lst, batch_size=1, shuffle=False)
        for idx, data in enumerate(loader):
            index = data.node_name[0].index('roughness')
            with torch.no_grad():
                data_recon, f_u, f_z, z, node_feature = self.forward(data)
            r_pred = data_recon[index, :NODE_DIM['roughness']]
            r_label = r_lst[idx]
            error.append(torch.abs(r_pred - r_label))

        if len(error) > 0:
            return torch.mean(torch.tensor(error))
        else:
            return 0

    def training_step(self, batch_graph, batch_idx):
        x_recon, f_u, f_z, z, node_feature = self.forward(batch_graph)

        loss, rec_loss, h_a, kl_loss = self.cal_loss(batch_graph, x_recon, f_u, f_z, z, node_feature)
        self.log('train_loss', loss, prog_bar=True, on_step=False, on_epoch=True, batch_size=batch_graph.batch_size)
        self.log('rec_loss', rec_loss, prog_bar=False, on_step=False, on_epoch=True, batch_size=batch_graph.batch_size)
        self.log('hA', h_a, prog_bar=False, on_step=False, on_epoch=True, batch_size=batch_graph.batch_size)
        self.log('kl_loss', kl_loss, on_step=False, on_epoch=True, batch_size=batch_graph.batch_size)

        pred_err = self.predict(batch_graph)
        self.log('train_error', pred_err, prog_bar=True, on_step=False, on_epoch=True,
                 batch_size=batch_graph.batch_size)
        return loss

    def validation_step(self, batch_graph, batch_idx):
        x_recon, f_u, f_z, z, node_feature = self.forward(batch_graph)

        loss, rec_loss, h_a, kl_loss = self.cal_loss(batch_graph, x_recon, f_u, f_z, z, node_feature)
        self.log('val_loss', loss, prog_bar=True, on_step=False, on_epoch=True, batch_size=batch_graph.batch_size)

        pred_err = self.predict(batch_graph)
        self.log('val_error', pred_err, prog_bar=True, on_step=False, on_epoch=True,
                 batch_size=batch_graph.batch_size)

    def test_step(self, batch_graph, batch_idx):
        x_recon, f_u, f_z, z, node_feature = self.forward(batch_graph)

        loss, rec_loss, h_a, kl_loss = self.cal_loss(batch_graph, x_recon, f_u, f_z, z, node_feature)
        self.log('test_loss', loss, prog_bar=True, on_step=False, on_epoch=True, batch_size=batch_graph.batch_size)

        pred_err = self.predict(batch_graph)
        self.log('test_error', pred_err, prog_bar=True, on_step=False, on_epoch=True,
                 batch_size=batch_graph.batch_size)

    def on_train_epoch_start(self):
        self.plot_heatmap('heatmap', self.adj_matrix)

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=1e-3, weight_decay=1e-2)
        return optimizer

    def plot_heatmap(self, name, matrix):
        heatmap = matrix.detach().cpu().numpy()
        fig, ax = plt.subplots()
        img = ax.imshow(heatmap)
        fig.colorbar(img, ax=ax)
        self.logger.experiment.add_figure(name, fig, self.current_epoch)

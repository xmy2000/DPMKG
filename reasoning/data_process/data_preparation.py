import torch
import numpy as np
import pandas as pd
import networkx as nx
from torch_geometric.data import Data
from torch_geometric.utils import to_undirected
from dowhy.utils.networkx_plotting import plot_causal_graph_networkx

# data read
data = pd.read_csv("../data/norm_data.csv")
print(f"Original data shape: {data.shape}")

# graph create
layer1 = ['machine', 'tool', 'material', 'feature', 'process']
layer2 = ['wear', 'breakage']
layer3 = ['roughness']
edge_lst = []
for l1 in layer1:
    for l2 in layer2:
        edge_lst.append((l1, l2))
    for l3 in layer3:
        edge_lst.append((l1, l3))
for l2 in layer2:
    for l3 in layer3:
        edge_lst.append((l2, l3))
edge_lst.append(('machine', 'tool'))
edge_lst.append(('feature', 'tool'))
edge_lst.append(('feature', 'machine'))
edge_lst.append(('feature', 'process'))
edge_lst.append(('material', 'process'))
edge_lst.append(('tool', 'process'))
edge_lst.append(('wear', 'breakage'))

# data assignment
machine = pd.get_dummies(data['machine']).astype(float).to_numpy()
tool = pd.get_dummies(data['tool_type']).astype(float).to_numpy()
material = pd.get_dummies(data['material']).astype(float).to_numpy()
feature = pd.get_dummies(data['feature_type']).astype(float).to_numpy()
process = pd.get_dummies(data['process_type'])
process = pd.concat([process, data[['rotate', 'feed', 'depth']]], axis=1).astype(float).to_numpy()
wear = data['wear'].astype(float).to_numpy()
wear = np.expand_dims(wear, axis=1)
breakage = pd.get_dummies(data['breakage_type']).astype(float).to_numpy()
roughness = data['roughness'].astype(float).to_numpy()
roughness = np.expand_dims(roughness, axis=1)

df_lst = [machine, tool, material, feature, process, wear, breakage, roughness]
df_name = ['machine', 'tool', 'material', 'feature', 'process', 'wear', 'breakage', 'roughness']

adj_matrix = torch.zeros((len(df_name), len(df_name)), dtype=torch.float)
for i, j in edge_lst:
    row = df_name.index(i)
    col = df_name.index(j)
    adj_matrix[row, col] = 1.
torch.save(adj_matrix, '../data/adj_matrix.pt')

graph_lst = []
for row in range(data.shape[0]):
    part_id = data.loc[row, '图号'].split('.')[-1] + '_' + str(data.loc[row, '工序']) + '_' + data.loc[row, '零件ID']
    node_name = df_name.copy()
    graph_edge_lst = edge_lst.copy()

    if np.isnan(df_lst[df_name.index('wear')][row]):
        node_name.remove('wear')
        graph_edge_lst = [(s, t) for s, t in graph_edge_lst if s != "wear" and t != "wear"]
    if np.isnan(df_lst[df_name.index('roughness')][row]):
        node_name.remove('roughness')
        graph_edge_lst = [(s, t) for s, t in graph_edge_lst if s != "roughness" and t != "roughness"]

    num_nodes = len(node_name)
    edge_index = [[node_name.index(s), node_name.index(t)] for s, t in graph_edge_lst]
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    edge_index = to_undirected(edge_index)

    x = torch.zeros((num_nodes, 12), dtype=torch.float)
    for i in range(num_nodes):
        value_name = node_name[i]
        value = df_lst[df_name.index(value_name)][row]
        value = torch.tensor(value, dtype=torch.float)
        x[i, :value.numel()] = value

    pyg_data = Data(
        x=x,
        name=part_id,
        num_nodes=num_nodes,
        node_name=node_name,
        edge_index=edge_index
    )

    graph_lst.append(pyg_data)

torch.save(graph_lst, '../data/dataset/dataset.pt')

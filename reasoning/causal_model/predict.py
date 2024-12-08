import torch
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from copy import deepcopy
from torch_geometric.loader import DataLoader

from parameters import *
from causal_model import Model

plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

experiment = "experiment4"
model_name = "causal_structure_mining"
version = "version_8"
file_name = "epoch=56-val_loss=0.1652-val_error=0.2519.ckpt"

experiment_path = f"../checkpoints/{experiment}/{model_name}"
model_path = f"{experiment_path}/lightning_logs/{version}/checkpoints/{file_name}"

with open(f'../data/{experiment}/train_part.txt', 'r') as file:
    lines = file.readlines()
train_part_lst = [str(line.strip()) for line in lines]
with open(f'../data/{experiment}/test_part.txt', 'r') as file:
    lines = file.readlines()
test_part_lst = [str(line.strip()) for line in lines]

model = Model.load_from_checkpoint(model_path)
model.eval()


def inference(model, batch_graph, target_node):
    node_name = batch_graph.node_name[0]
    if target_node in node_name:
        index = node_name.index(target_node)
        y = batch_graph[0].x[index, :NODE_DIM[target_node]].to(DEVICE)
        batch_graph[0].x[index] = 0
        with torch.no_grad():
            graph_recon, f_u, f_z, z, node_feature = model(batch_graph.to(DEVICE))
        y_pred = graph_recon[index, :NODE_DIM[target_node]]
        mae = torch.abs(y_pred - y)
        err = 2 * mae / (torch.abs(y_pred) + torch.abs(y))
        return {"mae": mae.item(), "err": err.item()}
    else:
        return None


def predict(part_id):
    part_data = torch.load(f"../data/part_dataset/{part_id}.pt")
    loader = DataLoader(part_data, batch_size=1, shuffle=False)
    wear_mae = 0
    wear_err = 0
    wear_count = 0
    roughness_mae = 0
    roughness_err = 0
    roughness_count = 0
    for batch_graph in loader:
        result_wear = inference(model, deepcopy(batch_graph), "wear")
        if result_wear is not None:
            wear_mae += result_wear["mae"]
            wear_err += result_wear["err"]
            wear_count += 1

        result_roughness = inference(model, deepcopy(batch_graph), "roughness")
        if result_roughness is not None:
            roughness_mae += result_roughness["mae"]
            roughness_err += result_roughness["err"]
            roughness_count += 1

    if wear_count != 0:
        wear_mae_avg = wear_mae / wear_count
        wear_err_avg = wear_err / wear_count
    else:
        wear_mae_avg = 0
        wear_err_avg = 0
    if roughness_count != 0:
        roughness_mae_avg = roughness_mae / roughness_count
        roughness_err_avg = roughness_err / roughness_count
    else:
        roughness_mae_avg = 0
        roughness_err_avg = 0

    return wear_mae_avg, wear_err_avg, roughness_mae_avg, roughness_err_avg


df = pd.DataFrame(columns=['type', 'part_id', 'wear_mae', 'wear_err', 'roughness_mae', 'roughness_err'])
for part_id in tqdm(train_part_lst):
    wear_mae, wear_err, roughness_mae, roughness_err = predict(part_id)
    df = df._append({'type': 'train', 'part_id': part_id, 'wear_mae': wear_mae, 'wear_err': wear_err,
                     'roughness_mae': roughness_mae, 'roughness_err': roughness_err}, ignore_index=True)

for part_id in tqdm(test_part_lst):
    wear_mae, wear_err, roughness_mae, roughness_err = predict(part_id)
    df = df._append({'type': 'test', 'part_id': part_id, 'wear_mae': wear_mae, 'wear_err': wear_err,
                     'roughness_mae': roughness_mae, 'roughness_err': roughness_err}, ignore_index=True)

df.to_csv(f"{experiment_path}/{version}_results.csv", index=False)

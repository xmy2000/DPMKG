import torch

dataset = torch.load("../data/dataset.pt")

with open('../data/part_id.txt', 'r') as file:
    lines = file.readlines()
part_lst = [str(line.strip()) for line in lines]

data_dict = {}
for part_id in part_lst:
    data_dict[part_id] = []

for data in dataset:
    data_id = data['name'].split('_')[-1]
    data_dict[data_id].append(data)

for part_id, part_data in data_dict.items():
    print(f"{part_id}: {len(part_data)}")
    torch.save(part_data, f'../data/part_dataset/{part_id}.pt')

import torch

experiment_folder = "../data/experiment4"
with open(f'{experiment_folder}/train_part.txt', 'r') as file:
    lines = file.readlines()
train_part_lst = [str(line.strip()) for line in lines]
with open(f'{experiment_folder}/test_part.txt', 'r') as file:
    lines = file.readlines()
test_part_lst = [str(line.strip()) for line in lines]

dataset = torch.load("../data/dataset.pt")
train_data = []
test_data = []
for data in dataset:
    data_id = data['name'].split('_')[-1]
    if data_id in train_part_lst:
        train_data.append(data)
    elif data_id in test_part_lst:
        test_data.append(data)
    else:
        raise Exception("Data not found.")
assert len(dataset) == len(train_data) + len(test_data)

torch.save(train_data, f'{experiment_folder}/train_dataset.pt')
torch.save(test_data, f'{experiment_folder}/test_dataset.pt')

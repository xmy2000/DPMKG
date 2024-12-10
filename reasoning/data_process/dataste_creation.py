import os
import glob
import numpy as np
import pandas as pd
import torch

if __name__ == '__main__':
    TRAIN_DATA = []
    VAL_DATA = []
    TEST_DATA = []
    train_ids = []
    val_ids = []
    test_ids = []

    folder_path = "../data/split_data"
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    for file_path in csv_files:
        df = pd.read_csv(file_path)
        ids = df['零件ID'].unique().tolist()
        if len(ids) <= 3:
            train_ids.extend(ids)
        else:
            data_size = len(ids)
            train_size = int(data_size * 0.7)
            val_size = int(data_size * 0.15 + 1)
            test_size = data_size - train_size - val_size
            train_ids.extend(ids[:train_size])
            val_ids.extend(ids[train_size:train_size + val_size])
            test_ids.extend(ids[train_size + val_size:])

    dataset = torch.load("../data/dataset/dataset.pt")
    for data in dataset:
        data_id = data['name']
        if data_id in train_ids:
            TRAIN_DATA.append(data)
        elif data_id in val_ids:
            VAL_DATA.append(data)
        elif data_id in test_ids:
            TEST_DATA.append(data)
        else:
            raise Exception("Data not found.")
    torch.save(TRAIN_DATA, "../data/dataset/train_dataset.pt")
    torch.save(VAL_DATA, "../data/dataset/val_dataset.pt")
    torch.save(TEST_DATA, "../data/dataset/test_dataset.pt")

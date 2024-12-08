import torch
import lightning as L
from lightning.pytorch import seed_everything
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping, StochasticWeightAveraging
from torch_geometric.loader import DataLoader

from causal_model import Model

seed_everything(3407, workers=True)

experiment_folder = "../data/experiment1"
train_data = torch.load(f"{experiment_folder}/train_dataset.pt")
test_data = torch.load(f"{experiment_folder}/test_dataset.pt")

batch_size = 16
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

adj_matrix = torch.load("../data/adj_matrix.pt")

model = Model(
    adj_matrix=adj_matrix,
    node_feature_dim=8
)

checkpoint_callback = ModelCheckpoint(
    save_top_k=3,
    monitor="val_loss",
    mode="min",
    filename='{epoch}-{val_loss:.4f}-{val_error:.4f}'
)
early_stopping_callback = EarlyStopping(
    monitor="val_loss",
    mode="min",
    patience=20,
    check_on_train_epoch_end=False
)
swa_callback = StochasticWeightAveraging(swa_lrs=1e-4, swa_epoch_start=80, annealing_epochs=20)

trainer = L.Trainer(
    deterministic=True,
    # min_epochs=100,
    max_epochs=10000,
    default_root_dir="../checkpoints/experiment1/causal_structure_mining/",
    log_every_n_steps=1,
    callbacks=[
        checkpoint_callback,
        early_stopping_callback,
        swa_callback
    ],
)
trainer.fit(model=model, train_dataloaders=train_loader, val_dataloaders=test_loader)
trainer.test(model, dataloaders=test_loader, ckpt_path="best")

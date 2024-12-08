import torch
from parameters import *


def kl_loss(mu, logstd):
    return -0.5 * torch.mean(torch.sum(1 + 2 * logstd - mu ** 2 - logstd.exp() ** 2, dim=1))


def kl_loss_data(pred, label):
    eps = 1e-8
    mu_pred = torch.mean(pred, dim=0)
    std_pred = torch.std(pred, dim=0) + eps
    mu_label = torch.mean(label, dim=0)
    std_label = torch.std(label, dim=0) + eps

    kl_loss = 0.5 * (torch.log(std_label) - torch.log(std_pred) +
                     std_pred / std_label +
                     (mu_pred - mu_label).pow(2) / std_label - 1)
    return torch.mean(kl_loss)


def matrix_poly(matrix, n):
    x = torch.eye(n, device=DEVICE) + torch.div(matrix, 1)
    return torch.matrix_power(x, n)


def h_A(A):
    m = A.shape[0]
    expm_A = matrix_poly(A * A, m)
    h_A = torch.trace(expm_A) - m
    return h_A


def to_one_hot(prob_scores):
    index = prob_scores.index(max(prob_scores))
    one_hot_encoded = [0] * len(prob_scores)
    one_hot_encoded[index] = 1
    return one_hot_encoded


def get_key_by_value(my_dict, value_to_find):
    key_with_value = next((key for key, value in my_dict.items() if value == value_to_find), None)
    return key_with_value

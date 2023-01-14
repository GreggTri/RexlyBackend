import torch
import torch.nn as nn


class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_dim, output_dim):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_dim)
        self.l2 = nn.Linear(hidden_dim, hidden_dim) 
        self.l3 = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.l1(x)
        x = self.relu(x)
        x = self.l2(x)
        x = self.relu(x)
        out = self.l3(x)
        # no activation and no softmax at the end
        return out

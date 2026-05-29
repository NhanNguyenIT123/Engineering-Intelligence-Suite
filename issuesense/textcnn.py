import torch
from torch import nn


class TextCNN(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embedding_dim: int = 96,
        num_filters: int = 64,
        kernel_sizes: tuple[int, ...] = (3, 4, 5),
        dropout: float = 0.25,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.convs = nn.ModuleList(
            nn.Conv1d(embedding_dim, num_filters, kernel_size) for kernel_size in kernel_sizes
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(num_filters * len(kernel_sizes), num_classes)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids).transpose(1, 2)
        pooled = []
        for conv in self.convs:
            features = torch.relu(conv(embedded))
            pooled.append(torch.max(features, dim=2).values)
        combined = torch.cat(pooled, dim=1)
        return self.fc(self.dropout(combined))

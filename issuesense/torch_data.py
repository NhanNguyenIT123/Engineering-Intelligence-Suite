from collections import Counter

import torch
from torch.utils.data import Dataset

from issuesense.preprocessing import tokenize

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"


def build_vocab(texts: list[str], min_freq: int = 1) -> dict[str, int]:
    counter = Counter()
    for text in texts:
        counter.update(tokenize(text))

    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for token, count in sorted(counter.items()):
        if count >= min_freq:
            vocab[token] = len(vocab)
    return vocab


def encode_text(text: str, vocab: dict[str, int], max_length: int = 64) -> list[int]:
    ids = [vocab.get(token, vocab[UNK_TOKEN]) for token in tokenize(text)]
    ids = ids[:max_length]
    if len(ids) < max_length:
        ids.extend([vocab[PAD_TOKEN]] * (max_length - len(ids)))
    return ids


class IssueDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], vocab: dict[str, int], max_length: int = 64) -> None:
        self.input_ids = [encode_text(text, vocab, max_length) for text in texts]
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int):
        return (
            torch.tensor(self.input_ids[index], dtype=torch.long),
            torch.tensor(self.labels[index], dtype=torch.long),
        )

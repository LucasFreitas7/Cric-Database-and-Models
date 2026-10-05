"""Predição em lote de um conjunto de linhas do índice."""
import numpy as np
import torch
from torch.utils.data import DataLoader

from .datasets import PatchDataset


@torch.no_grad()
def predict(model, rows, data_cfg, jitter=0, batch_size=256, num_workers=0, device="cuda"):
    """Retorna probabilidades (N, C) na ordem de `rows`. rows precisa de 'target'
    (use 0 quando o rótulo não importar)."""
    ds = PatchDataset(rows, data_cfg["patch_size"], data_cfg["crop_size"], data_cfg["img_size"],
                      train=False, jitter=jitter)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=num_workers,
                        pin_memory=True)
    model.eval()
    out = []
    for x, _ in loader:
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device == "cuda"):
            logits = model(x.to(device, non_blocking=True))
        out.append(torch.softmax(logits.float(), dim=1).cpu().numpy())
    return np.concatenate(out) if out else np.zeros((0, 0))

"""Dataset PyTorch que recorta na hora a partir do cache de patches."""
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2

from .config import CACHE_DIR, IMAGENET_MEAN, IMAGENET_STD
from .tasks import Task


def select_task_rows(index: pd.DataFrame, task: Task) -> pd.DataFrame:
    """Filtra as linhas que pertencem à tarefa e cria a coluna 'target'."""
    rows = index[index["label"].isin(task.mapping)].copy()
    rows["target"] = rows["label"].map(task.mapping).astype(int)
    return rows.reset_index(drop=True)


def build_transform(train: bool, img_size: int, crop_size: int):
    ops = [v2.ToDtype(torch.float32, scale=True)]
    if train:
        ops = [
            v2.RandomHorizontalFlip(),
            v2.RandomVerticalFlip(),
            v2.RandomChoice([v2.RandomRotation((a, a)) for a in (0, 90, 180, 270)]),
            v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.15, hue=0.03),
        ] + ops
    if img_size != crop_size:
        ops.append(v2.Resize((img_size, img_size), antialias=True))
    ops.append(v2.Normalize(IMAGENET_MEAN, IMAGENET_STD))
    return v2.Compose(ops)


class PatchDataset(Dataset):
    """Recorta `crop_size` px do patch, com deslocamento aleatório do centro.

    jitter = deslocamento máximo (px) do núcleo em relação ao centro. Para o C1
    reproduz as imagens "descentralizadas" da dissertação: com recorte 70 e
    jitter 25, o núcleo fica sempre a pelo menos 10 px da borda.
    Na validação o deslocamento é fixo por amostra (reprodutível).
    """

    def __init__(self, rows: pd.DataFrame, patch_size: int, crop_size: int, img_size: int,
                 train: bool, jitter: int = 0, seed: int = 0):
        assert crop_size + 2 * jitter <= patch_size, "patch_size pequeno para crop_size + jitter"
        self.rows = rows.reset_index(drop=True)
        self.patch_size, self.crop_size, self.jitter = patch_size, crop_size, jitter
        self.train, self.seed = train, seed
        self.transform = build_transform(train, img_size, crop_size)
        self._patches = None  # aberto sob demanda (cada worker abre o seu mmap)

    @property
    def patches(self):
        if self._patches is None:
            self._patches = np.load(CACHE_DIR / f"patches_{self.patch_size}.npy", mmap_mode="r")
        return self._patches

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        row = self.rows.iloc[i]
        if self.jitter:
            rng = np.random.default_rng() if self.train else np.random.default_rng(self.seed + int(row.patch_idx))
            dx, dy = rng.integers(-self.jitter, self.jitter + 1, size=2)
        else:
            dx = dy = 0
        top = (self.patch_size - self.crop_size) // 2 + int(dy)
        left = (self.patch_size - self.crop_size) // 2 + int(dx)
        crop = np.ascontiguousarray(self.patches[row.patch_idx, top:top + self.crop_size, left:left + self.crop_size])
        x = self.transform(torch.from_numpy(crop).permute(2, 0, 1))
        return x, int(row.target)

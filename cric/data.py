"""Leitura das anotações CRIC e construção do cache de patches.

Em vez de milhares de PNGs em pastas (que facilitavam vazamento entre treino e
validação), extraímos UMA vez um patch maior (ex. 128×128) em volta de cada
núcleo anotado e de pontos de fundo sem núcleo. O recorte final (ex. 70×70,
centrado ou deslocado) é feito na hora pelo Dataset.

Saída em data/cache/:
  patches_<P>.npy  -> array uint8 (N, P, P, 3), lido com mmap
  index_<P>.csv    -> uma linha por patch: image, x, y, label (7 classes), kind
"""
import json

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

from .config import ANNOTATIONS_JSON, BACKGROUND, BETHESDA, CACHE_DIR, IMAGES_DIR


def load_annotations(path=ANNOTATIONS_JSON) -> pd.DataFrame:
    """Uma linha por célula anotada: image, image_id, cell_id, x, y, label."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for item in data:
        for cell in item["classifications"]:
            rows.append({
                "image": item["image_name"],
                "image_id": item["image_id"],
                "cell_id": cell["cell_id"],
                "x": int(cell["nucleus_x"]),
                "y": int(cell["nucleus_y"]),
                "label": BETHESDA[cell["bethesda_system"]],
            })
    return pd.DataFrame(rows)


def _sample_background(img: np.ndarray, nuclei: np.ndarray, n: int, min_dist: float,
                       content_frac: float, rng: np.random.Generator, half: int):
    """Sorteia n pontos sem núcleo anotado num raio de `min_dist`.

    Uma fração `content_frac` precisa ter "conteúdo" (desvio-padrão de cinza alto:
    bordas de célula, leucócitos, debris) — são os negativos difíceis.
    """
    h, w = img.shape[:2]
    gray = img.mean(axis=2)
    points, n_content = [], int(round(n * content_frac))
    for _ in range(n * 200):
        if len(points) >= n:
            break
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        if len(nuclei) and np.min(np.hypot(nuclei[:, 0] - x, nuclei[:, 1] - y)) < min_dist:
            continue
        if len(points) < n_content:
            win = gray[max(y - half, 0):y + half, max(x - half, 0):x + half]
            if win.std() < 12:
                continue
        points.append((x, y))
    return points


def build_cache(patch_size=128, bg_per_image=30, bg_min_dist=50, bg_content_frac=0.5, seed=42):
    """Gera patches de células anotadas + fundo e salva em data/cache/."""
    rng = np.random.default_rng(seed)
    cells = load_annotations()
    half = patch_size // 2

    records = []
    for image, group in cells.groupby("image", sort=True):
        nuclei = group[["x", "y"]].to_numpy()
        for r in group.itertuples():
            records.append((image, r.image_id, r.cell_id, r.x, r.y, r.label, "cell"))
        img = np.asarray(Image.open(IMAGES_DIR / image).convert("RGB"))
        for x, y in _sample_background(img, nuclei, bg_per_image, bg_min_dist,
                                       bg_content_frac, rng, half=35):
            records.append((image, group.image_id.iloc[0], -1, x, y, BACKGROUND, "background"))

    index = pd.DataFrame(records, columns=["image", "image_id", "cell_id", "x", "y", "label", "kind"])
    index.insert(0, "patch_idx", np.arange(len(index)))

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = np.lib.format.open_memmap(CACHE_DIR / f"patches_{patch_size}.npy", mode="w+",
                                    dtype=np.uint8, shape=(len(index), patch_size, patch_size, 3))
    for image, group in tqdm(index.groupby("image", sort=True), desc="Extraindo patches"):
        img = np.asarray(Image.open(IMAGES_DIR / image).convert("RGB"))
        img = np.pad(img, ((half, half), (half, half), (0, 0)), mode="reflect")
        for r in group.itertuples():
            # +half pelo padding: o ponto (x, y) fica no centro do patch
            out[r.patch_idx] = img[r.y:r.y + patch_size, r.x:r.x + patch_size]
    out.flush()
    index.to_csv(CACHE_DIR / f"index_{patch_size}.csv", index=False)
    return index


def load_index(patch_size=128) -> pd.DataFrame:
    path = CACHE_DIR / f"index_{patch_size}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} não existe. Rode antes: python scripts/build_cache.py")
    return pd.read_csv(path)

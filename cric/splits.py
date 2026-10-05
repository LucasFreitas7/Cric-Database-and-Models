"""Divisão por IMAGEM (nunca por recorte) em teste + k folds.

Todas as células e fundos de uma mesma imagem ficam sempre no mesmo lado, o que
elimina o vazamento entre treino e validação. O conjunto de teste é separado
uma única vez e só deve ser usado na avaliação final.
"""
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from .config import SPLITS_DIR

TEST = -1  # valor da coluna 'fold' para imagens de teste


def make_splits(index: pd.DataFrame, n_folds=5, test_parts=5, seed=42) -> pd.DataFrame:
    """Retorna DataFrame image -> fold (0..n_folds-1, ou -1 = teste).

    test_parts=5 separa ~1/5 (20%) das imagens para teste. A estratificação usa
    o rótulo das células, para cada parte ter proporções parecidas de classes.
    """
    cells = index[index["kind"] == "cell"]
    outer = StratifiedGroupKFold(n_splits=test_parts, shuffle=True, random_state=seed)
    _, test_idx = next(outer.split(cells, cells["label"], groups=cells["image"]))
    test_images = set(cells.iloc[test_idx]["image"])

    dev = cells[~cells["image"].isin(test_images)]
    inner = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    fold_of = {img: TEST for img in test_images}
    for k, (_, val_idx) in enumerate(inner.split(dev, dev["label"], groups=dev["image"])):
        for img in dev.iloc[val_idx]["image"].unique():
            fold_of[img] = k

    images = sorted(index["image"].unique())
    return pd.DataFrame({"image": images, "fold": [fold_of[i] for i in images]})


def splits_path(seed=42) -> "Path":
    return SPLITS_DIR / f"splits_seed{seed}.csv"


def save_splits(splits: pd.DataFrame, seed=42):
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    splits.to_csv(splits_path(seed), index=False)


def load_splits(seed=42) -> pd.DataFrame:
    path = splits_path(seed)
    if not path.exists():
        raise FileNotFoundError(f"{path} não existe. Rode antes: python scripts/make_splits.py")
    return pd.read_csv(path)


def summarize(index: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    """Tabela: nº de patches por classe em cada fold/teste (útil para a dissertação)."""
    df = index.merge(splits, on="image")
    df["parte"] = df["fold"].map(lambda f: "teste" if f == TEST else f"fold {f}")
    table = pd.crosstab(df["label"], df["parte"], margins=True, margins_name="total")
    n_img = splits.assign(parte=splits["fold"].map(lambda f: "teste" if f == TEST else f"fold {f}"))
    table.loc["(imagens)"] = n_img["parte"].value_counts().reindex(table.columns[:-1]).tolist() + [len(splits)]
    return table

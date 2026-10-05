"""Passo 2 — divide as IMAGENS em teste (~20%) + k folds e salva em data/splits/.

    python scripts/make_splits.py
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from cric.data import load_index  # noqa: E402
from cric.splits import make_splits, save_splits, splits_path, summarize  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--patch-size", type=int, default=128)
    ap.add_argument("--force", action="store_true", help="sobrescreve um split existente")
    a = ap.parse_args()
    if splits_path(a.seed).exists() and not a.force:
        sys.exit(f"{splits_path(a.seed)} já existe (use --force para refazer — isso muda todos os resultados).")
    index = load_index(a.patch_size)
    splits = make_splits(index, a.n_folds, seed=a.seed)
    save_splits(splits, a.seed)
    print(summarize(index, splits).to_string())
    print(f"\nSalvo em {splits_path(a.seed)}")

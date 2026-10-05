"""Passo 1 — extrai os patches de células e de fundo para data/cache/.

    python scripts/build_cache.py
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from cric.data import build_cache  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--patch-size", type=int, default=128)
    ap.add_argument("--bg-per-image", type=int, default=30, help="pontos de fundo (não-célula) por imagem")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    index = build_cache(a.patch_size, a.bg_per_image, seed=a.seed)
    print(index["label"].value_counts().to_string())
    print(f"Total: {len(index)} patches")

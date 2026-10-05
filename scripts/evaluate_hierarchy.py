"""Passo 4 — avalia a hierarquia completa (hard e soft) contra o flat7.

    python scripts/evaluate_hierarchy.py               # validação cruzada (cada fold)
    python scripts/evaluate_hierarchy.py --split test  # teste final (ensemble dos folds) — usar UMA vez

Precisa dos modelos c1..c5 e flat7 treinados no mesmo experimento.
Saída: runs/<experiment>/hierarchy/<split>/summary.json + matrizes de confusão.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import torch  # noqa: E402

from cric.config import load_config  # noqa: E402
from cric.hierarchy import evaluate  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", choices=["val", "test"], default="val")
    ap.add_argument("--config", default=None)
    ap.add_argument("--set", nargs="*", default=[], metavar="CHAVE=VALOR")
    a = ap.parse_args()
    cfg = load_config(a.config, a.set)
    summary = evaluate(cfg, a.split, "cuda" if torch.cuda.is_available() else "cpu")
    print(json.dumps({m: s["7_classes"] for m, s in summary.items()}, indent=2))

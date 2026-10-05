"""Passo 3 — treina uma ou mais tarefas com validação cruzada por imagem.

    python scripts/train.py --task c2                    # todos os folds
    python scripts/train.py --task c1 c2 c3 c4 c5 flat7  # hierarquia + baseline
    python scripts/train.py --task c2 --folds 0          # só o fold 0
    python scripts/train.py --task c5 --config configs/convnext.yaml --set train.lr=1e-4
    python scripts/train.py --task c2 --set train.limit=500 train.epochs=1   # teste rápido

Tarefas: c1 (célula×não), c2 (lesão), c3 (baixo×alto), c4 (ASC-US×LSIL),
         c5 (ASC-H×HSIL×SCC), flat7, flat6.
Saída: runs/<experiment>/<tarefa>/fold<k>/{best.pt, metrics.json, confusion.png, ...}
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import torch  # noqa: E402

from cric.config import load_config  # noqa: E402
from cric.train import train_task  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", nargs="+", required=True)
    ap.add_argument("--folds", nargs="+", type=int, default=None)
    ap.add_argument("--config", default=None, help="YAML com o que muda em relação a configs/default.yaml")
    ap.add_argument("--set", nargs="*", default=[], metavar="CHAVE=VALOR")
    a = ap.parse_args()
    cfg = load_config(a.config, a.set)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        cfg["train"]["amp"] = False
        print("AVISO: GPU não encontrada, treinando na CPU (lento).")
    for task in a.task:
        summary = train_task(cfg, task, a.folds, device)
        print(json.dumps(summary["summary"], indent=2))

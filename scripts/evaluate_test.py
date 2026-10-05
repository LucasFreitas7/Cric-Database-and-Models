"""Avalia tarefas no conjunto de TESTE (ensemble dos 5 folds).

    python scripts/evaluate_test.py --task c2 c3 c4 c5
    python scripts/evaluate_test.py --task c5 --config configs/leakage_v1.yaml

O teste serve para RELATAR resultados — nunca para escolher configuração.
Saída: runs/<experiment>/<tarefa>/test_metrics.json e test_confusion.png
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import torch  # noqa: E402

from cric.config import load_config  # noqa: E402
from cric.train import evaluate_task_on_test  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", nargs="+", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--set", nargs="*", default=[], metavar="CHAVE=VALOR")
    a = ap.parse_args()
    cfg = load_config(a.config, a.set)
    for task in a.task:
        evaluate_task_on_test(cfg, task, "cuda" if torch.cuda.is_available() else "cpu")

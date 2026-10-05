"""Composição da hierarquia C1→C5 em 7 classes e comparação com o flat.

Duas formas de combinar:
- hard: cada nível decide (argmax) e encaminha para o próximo — como a interface faz;
- soft: probabilidade de cada folha = produto das probabilidades do caminho,
  ex. P(HSIL) = P(célula)·P(lesão|célula)·P(alto|lesão)·P(HSIL|alto).
"""
import json

import numpy as np
import pandas as pd

from .config import CLASSES7
from .data import load_index
from .inference import predict
from .metrics import compute_metrics, plot_confusion, summarize_folds
from .models import load_checkpoint
from .splits import TEST, load_splits
from .train import run_dir
from .tasks import HIERARCHY

# Agrupamentos usados na literatura da CRIC (índices de CLASSES7 -> grupo)
GROUPINGS = {
    "7_classes": (list(CLASSES7), list(range(7))),
    "3_classes": (["nao_celula", "NILM", "baixo_grau", "alto_grau"], [0, 1, 2, 2, 3, 3, 3]),
    "2_classes": (["nao_celula", "normal", "anormal"], [0, 1, 2, 2, 2, 2, 2]),
}


def compose_soft(p):
    """p: dict tarefa -> (N, C) probabilidades. Retorna (N, 7) na ordem de CLASSES7."""
    cell, les, high = p["c1"][:, 1], p["c2"][:, 1], p["c3"][:, 1]
    return np.stack([
        p["c1"][:, 0],
        cell * p["c2"][:, 0],
        cell * les * (1 - high) * p["c4"][:, 0],
        cell * les * (1 - high) * p["c4"][:, 1],
        cell * les * high * p["c5"][:, 0],
        cell * les * high * p["c5"][:, 1],
        cell * les * high * p["c5"][:, 2],
    ], axis=1)


def compose_hard(p):
    """Roteamento por argmax em cada nível; retorna (N, 7) one-hot."""
    n = len(p["c1"])
    pred = np.where(p["c1"].argmax(1) == 0, 0,
           np.where(p["c2"].argmax(1) == 0, 1,
           np.where(p["c3"].argmax(1) == 0, 2 + p["c4"].argmax(1), 4 + p["c5"].argmax(1))))
    out = np.zeros((n, 7))
    out[np.arange(n), pred] = 1.0
    return out


def regroup(y7, probs7, grouping):
    names, mapping = GROUPINGS[grouping]
    mapping = np.asarray(mapping)
    probs = np.zeros((len(probs7), len(names)))
    for src, dst in enumerate(mapping):
        probs[:, dst] += probs7[:, src]
    return mapping[np.asarray(y7)], probs, names


def _fold_models(cfg, fold, device):
    models = {}
    for t in HIERARCHY + ("flat7",):
        path = run_dir(cfg, t) / f"fold{fold}" / "best.pt"
        if not path.exists():
            raise FileNotFoundError(f"Falta {path}. Treine antes: python scripts/train.py --task {t}")
        models[t] = load_checkpoint(path, device)[0]
    return models


def evaluate(cfg, split="val", device="cuda", log=print):
    """split='val': cada fold com seus modelos; split='test': ensemble dos folds no teste."""
    index = load_index(cfg["data"]["patch_size"]).merge(load_splits(cfg["seed"]), on="image")
    index["target"] = index["label"].map({c: i for i, c in enumerate(CLASSES7)})
    dc = cfg["data"]
    out_dir = run_dir(cfg, "hierarchy") / split
    out_dir.mkdir(parents=True, exist_ok=True)

    def run_models(models, rows):
        return {t: predict(m, rows, dc, jitter=0, device=device) for t, m in models.items()}

    evaluations = []  # (nome, rows, probs por tarefa)
    if split == "val":
        for k in range(cfg["n_folds"]):
            rows = index[index["fold"] == k].reset_index(drop=True)
            evaluations.append((f"fold{k}", rows, run_models(_fold_models(cfg, k, device), rows)))
    else:
        rows = index[index["fold"] == TEST].reset_index(drop=True)
        acc = None
        for k in range(cfg["n_folds"]):
            p = run_models(_fold_models(cfg, k, device), rows)
            acc = p if acc is None else {t: acc[t] + p[t] for t in p}
        evaluations.append(("test", rows, {t: v / cfg["n_folds"] for t, v in acc.items()}))

    results = {}
    for name, rows, p in evaluations:
        methods = {"hierarquico_hard": compose_hard(p), "hierarquico_soft": compose_soft(p), "flat7": p["flat7"]}
        for method, probs7 in methods.items():
            for grouping in GROUPINGS:
                y, probs, names = regroup(rows["target"], probs7, grouping)
                m = compute_metrics(y, probs, names)
                results.setdefault(method, {}).setdefault(grouping, []).append(m)
                if grouping == "7_classes":
                    plot_confusion(m["confusion_matrix"], names, out_dir / f"{method}_{name}.png", f"{method} — {name}")
            log(f"[{name}] {method:17s} 7 classes: f1_macro={results[method]['7_classes'][-1]['f1_macro']:.4f} "
                f"bal_acc={results[method]['7_classes'][-1]['balanced_accuracy']:.4f}")
        pd.DataFrame({f"p_{t}_{i}": v[:, i] for t, v in p.items() for i in range(v.shape[1])}) \
            .assign(patch_idx=rows["patch_idx"], label=rows["label"]).to_csv(out_dir / f"probs_{name}.csv", index=False)

    summary = {method: {g: summarize_folds(ms) for g, ms in by_group.items()} for method, by_group in results.items()}
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return summary

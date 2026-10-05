"""Métricas de avaliação (classe clínica como positiva nas tarefas binárias)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             confusion_matrix, f1_score, precision_recall_fscore_support,
                             roc_auc_score)


def compute_metrics(y_true, probs, classes) -> dict:
    """y_true: (N,) índices; probs: (N, C) probabilidades."""
    y_true = np.asarray(y_true)
    probs = np.asarray(probs)
    y_pred = probs.argmax(1)
    labels = list(range(len(classes)))
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    m = {
        "n": int(len(y_true)),
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0),
        "per_class": {c: {"precision": p[i], "recall": r[i], "f1": f[i], "support": int(s[i])}
                      for i, c in enumerate(classes)},
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }
    if len(classes) == 2:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        m.update({
            "positive_class": classes[1],
            "sensitivity": tp / (tp + fn) if tp + fn else 0.0,
            "specificity": tn / (tn + fp) if tn + fp else 0.0,
            "ppv": tp / (tp + fp) if tp + fp else 0.0,
            "npv": tn / (tn + fn) if tn + fn else 0.0,
            "f1_positive": f[1],
        })
        if len(np.unique(y_true)) == 2:
            m["roc_auc"] = roc_auc_score(y_true, probs[:, 1])
            m["pr_auc"] = average_precision_score(y_true, probs[:, 1])
    elif len(np.unique(y_true)) == len(classes):
        m["roc_auc_ovr_macro"] = roc_auc_score(y_true, probs, multi_class="ovr", average="macro")
    return _to_builtin(m)


def _to_builtin(obj):
    if isinstance(obj, dict):
        return {k: _to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_builtin(v) for v in obj]
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def plot_confusion(cm, classes, path, title=""):
    cm = np.asarray(cm)
    norm = cm / np.maximum(cm.sum(1, keepdims=True), 1)
    fig, ax = plt.subplots(figsize=(1.1 * len(classes) + 2.5, 1.0 * len(classes) + 2))
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, f"{cm[i, j]}\n{norm[i, j]:.0%}", ha="center", va="center", fontsize=8,
                    color="white" if norm[i, j] > 0.5 else "black")
    ax.set_xticks(range(len(classes)), classes, rotation=45, ha="right")
    ax.set_yticks(range(len(classes)), classes)
    ax.set_xlabel("Predito")
    ax.set_ylabel("Real")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


SUMMARY_KEYS = ("accuracy", "balanced_accuracy", "f1_macro", "sensitivity", "specificity",
                "ppv", "npv", "roc_auc", "pr_auc", "roc_auc_ovr_macro")


def summarize_folds(metrics_list) -> dict:
    """Média ± desvio-padrão entre folds para as métricas escalares."""
    out = {}
    for k in SUMMARY_KEYS:
        vals = [m[k] for m in metrics_list if k in m]
        if vals:
            out[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0}
    return out

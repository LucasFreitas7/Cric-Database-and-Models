"""Treino de uma tarefa em um fold, com early stopping e registro completo."""
import json
import random
import time

import numpy as np
import pandas as pd
import torch
import yaml
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler

from .config import RUNS_DIR
from .data import load_index
from .datasets import PatchDataset, select_task_rows
from .inference import predict
from .metrics import compute_metrics, plot_confusion, summarize_folds
from .models import build_model, save_checkpoint
from .splits import TEST, load_splits
from .tasks import get_task


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def task_jitter(cfg, task_name):
    j = cfg["data"]["jitter"]
    return j.get(task_name, j["default"])


def run_dir(cfg, task_name):
    return RUNS_DIR / cfg["experiment"] / task_name


def load_task_rows(cfg, task):
    """Linhas da tarefa já com a coluna 'fold' (por imagem)."""
    index = load_index(cfg["data"]["patch_size"])
    splits = load_splits(cfg["seed"])
    return select_task_rows(index, task).merge(splits, on="image")


def train_fold(cfg, task_name, fold, device="cuda", log=print):
    task = get_task(task_name)
    tc, dc = cfg["train"], cfg["data"]
    set_seed(cfg["seed"] + fold)
    out = run_dir(cfg, task_name) / f"fold{fold}"
    out.mkdir(parents=True, exist_ok=True)

    rows = load_task_rows(cfg, task)
    train_rows = rows[(rows["fold"] != fold) & (rows["fold"] != TEST)]
    val_rows = rows[rows["fold"] == fold]
    if tc.get("limit"):  # modo rápido para teste do código
        train_rows = train_rows.sample(min(tc["limit"], len(train_rows)), random_state=0)
        val_rows = val_rows.sample(min(tc["limit"], len(val_rows)), random_state=0)
    jitter = task_jitter(cfg, task_name)

    train_ds = PatchDataset(train_rows, dc["patch_size"], dc["crop_size"], dc["img_size"], True, jitter)
    counts = np.bincount(train_rows["target"], minlength=task.num_classes)
    log(f"[{task_name} fold {fold}] treino={len(train_rows)} val={len(val_rows)} "
        f"classes={dict(zip(task.classes, counts.tolist()))}")

    sampler, class_weights = None, None
    if tc["balance"] == "sampler":
        w = 1.0 / np.maximum(counts, 1)
        sampler = WeightedRandomSampler(w[train_rows["target"].to_numpy()], len(train_rows), replacement=True)
    elif tc["balance"] == "loss":
        class_weights = torch.tensor(len(train_rows) / (task.num_classes * np.maximum(counts, 1)),
                                     dtype=torch.float32, device=device)

    loader = DataLoader(train_ds, batch_size=tc["batch_size"], shuffle=sampler is None, sampler=sampler,
                        num_workers=tc["num_workers"], pin_memory=True, drop_last=True,
                        persistent_workers=tc["num_workers"] > 0)

    model = build_model(cfg["model"]["name"], task.num_classes, cfg["model"]["pretrained"]).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=tc["label_smoothing"])
    optimizer = torch.optim.AdamW(model.parameters(), lr=tc["lr"], weight_decay=tc["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=tc["epochs"])
    scaler = torch.amp.GradScaler(enabled=tc["amp"])

    best, best_epoch, history, patience = -1.0, -1, [], 0
    for epoch in range(1, tc["epochs"] + 1):
        t0 = time.time()
        model.train()
        total = 0.0
        for x, y in loader:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=tc["amp"]):
                loss = criterion(model(x), y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total += loss.item()
        scheduler.step()

        probs = predict(model, val_rows, dc, jitter=jitter, device=device)
        m = compute_metrics(val_rows["target"], probs, task.classes)
        score = m[cfg["train"]["monitor"]]
        history.append({"epoch": epoch, "loss": total / max(len(loader), 1), **{k: m[k] for k in
                        ("accuracy", "balanced_accuracy", "f1_macro") if k in m}, "time_s": time.time() - t0})
        log(f"  época {epoch:2d}  loss={history[-1]['loss']:.4f}  val_f1_macro={m['f1_macro']:.4f}  "
            f"val_bal_acc={m['balanced_accuracy']:.4f}  ({history[-1]['time_s']:.0f}s)")
        if score > best:
            best, best_epoch, patience = score, epoch, 0
            save_checkpoint(out / "best.pt", model, cfg, task, epoch, m)
            best_metrics, best_probs = m, probs
        else:
            patience += 1
            if patience >= tc["patience"]:
                log(f"  early stopping (melhor época: {best_epoch})")
                break

    pd.DataFrame(history).to_csv(out / "history.csv", index=False)
    preds = val_rows[["patch_idx", "image", "label", "target"]].reset_index(drop=True)
    for i, c in enumerate(task.classes):
        preds[f"p_{c}"] = best_probs[:, i]
    preds.to_csv(out / "val_predictions.csv", index=False)
    best_metrics["best_epoch"] = best_epoch
    with open(out / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(best_metrics, f, indent=2, ensure_ascii=False)
    plot_confusion(best_metrics["confusion_matrix"], task.classes, out / "confusion.png",
                   f"{task.description} — fold {fold}")
    return best_metrics


def train_task(cfg, task_name, folds=None, device="cuda", log=print):
    """Treina todos os folds e salva summary.json (média ± desvio)."""
    out = run_dir(cfg, task_name)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
    folds = range(cfg["n_folds"]) if folds is None else folds
    results = [train_fold(cfg, task_name, k, device, log) for k in folds]
    summary = {"task": task_name, "folds": list(folds), "summary": summarize_folds(results)}
    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return summary

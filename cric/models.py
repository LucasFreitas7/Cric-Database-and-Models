"""Fábrica de modelos (qualquer backbone do timm) e checkpoints."""
import timm
import torch


def build_model(name: str, num_classes: int, pretrained: bool = True):
    return timm.create_model(name, pretrained=pretrained, num_classes=num_classes)


def save_checkpoint(path, model, cfg, task, epoch, metrics):
    torch.save({
        "state_dict": model.state_dict(),
        "model_name": cfg["model"]["name"],
        "task": task.name,
        "classes": list(task.classes),
        "data": cfg["data"],
        "epoch": epoch,
        "metrics": metrics,
    }, path)


def load_checkpoint(path, device="cpu"):
    ckpt = torch.load(path, map_location=device, weights_only=False)
    model = build_model(ckpt["model_name"], len(ckpt["classes"]), pretrained=False)
    model.load_state_dict(ckpt["state_dict"])
    return model.to(device).eval(), ckpt

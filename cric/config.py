"""Caminhos do projeto, classes e leitura de configuração (YAML)."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw"
IMAGES_DIR = DATA_RAW / "images"
ANNOTATIONS_JSON = DATA_RAW / "classifications.json"
CACHE_DIR = ROOT / "data" / "cache"
SPLITS_DIR = ROOT / "data" / "splits"
RUNS_DIR = ROOT / "runs"
CONFIGS_DIR = ROOT / "configs"

# Nome no JSON da CRIC -> nome curto usado no projeto
BETHESDA = {
    "Negative for intraepithelial lesion": "NILM",
    "ASC-US": "ASC-US",
    "LSIL": "LSIL",
    "ASC-H": "ASC-H",
    "HSIL": "HSIL",
    "SCC": "SCC",
}
BACKGROUND = "nao_celula"
CELL_CLASSES = ("NILM", "ASC-US", "LSIL", "ASC-H", "HSIL", "SCC")
CLASSES7 = (BACKGROUND,) + CELL_CLASSES
LOW_GRADE = ("ASC-US", "LSIL")
HIGH_GRADE = ("ASC-H", "HSIL", "SCC")
LESIONS = LOW_GRADE + HIGH_GRADE

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def _deep_update(base: dict, other: dict) -> dict:
    for k, v in other.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path=None, overrides=None) -> dict:
    """Lê configs/default.yaml, aplica o YAML do experimento e overrides 'a.b=valor'."""
    with open(CONFIGS_DIR / "default.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if path:
        with open(path, encoding="utf-8") as f:
            _deep_update(cfg, yaml.safe_load(f) or {})
    for item in overrides or []:
        key, value = item.split("=", 1)
        node = cfg
        *parents, leaf = key.split(".")
        for p in parents:
            node = node.setdefault(p, {})
        node[leaf] = yaml.safe_load(value)
    return cfg

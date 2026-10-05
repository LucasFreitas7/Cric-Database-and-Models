"""Gera tabelas (Markdown e LaTeX) com os resultados de um experimento.

    python scripts/report.py                       # experimento do default.yaml
    python scripts/report.py --experiment baseline_v1

Saída: runs/<experiment>/report.md e report.tex (prontas para a dissertação).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from cric.config import RUNS_DIR, load_config  # noqa: E402
from cric.tasks import TASKS  # noqa: E402

COLS = [("accuracy", "Acurácia"), ("balanced_accuracy", "Acur. bal."), ("f1_macro", "F1 macro"),
        ("sensitivity", "Sensib."), ("specificity", "Especif."), ("roc_auc", "AUC")]


def fmt(s, key):
    return f"{s[key]['mean']:.3f} ± {s[key]['std']:.3f}" if key in s else "—"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", default=None)
    a = ap.parse_args()
    exp = a.experiment or load_config()["experiment"]
    root = RUNS_DIR / exp

    rows = []
    for name, task in TASKS.items():
        f = root / name / "summary.json"
        if f.exists():
            s = json.loads(f.read_text(encoding="utf-8"))["summary"]
            rows.append([f"{name} — {task.description}"] + [fmt(s, k) for k, _ in COLS])
    for split in ("val", "test"):
        f = root / "hierarchy" / split / "summary.json"
        if f.exists():
            for method, groups in json.loads(f.read_text(encoding="utf-8")).items():
                for g, s in groups.items():
                    rows.append([f"{method} ({g}, {split})"] + [fmt(s, k) for k, _ in COLS])
    if not rows:
        sys.exit(f"Nenhum resultado em {root}")

    header = ["Modelo"] + [c for _, c in COLS]
    md = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows]
    (root / "report.md").write_text(f"# Resultados — {exp}\n\n" + "\n".join(md) + "\n", encoding="utf-8")

    tex = ["\\begin{tabular}{l" + "c" * len(COLS) + "}", "\\hline", " & ".join(header) + " \\\\ \\hline"]
    tex += [" & ".join(c.replace("±", "$\\pm$").replace("—", "--").replace("_", "\\_") for c in r) + " \\\\" for r in rows]
    tex += ["\\hline", "\\end{tabular}"]
    (root / "report.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nSalvo em {root / 'report.md'} e report.tex")


if __name__ == "__main__":
    main()

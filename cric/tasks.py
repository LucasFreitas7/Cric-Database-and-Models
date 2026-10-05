"""Definição de cada classificador da hierarquia e dos baselines flat.

Convenção: em tarefas binárias a classe de índice 1 é sempre a clinicamente
"positiva" (célula, com lesão, alto grau), então sensibilidade/especificidade
calculadas com pos_label=1 têm o significado clínico correto.
"""
from dataclasses import dataclass

from .config import BACKGROUND, CELL_CLASSES, CLASSES7, HIGH_GRADE, LESIONS, LOW_GRADE


@dataclass(frozen=True)
class Task:
    name: str
    classes: tuple
    mapping: dict  # rótulo de 7 classes -> índice da classe (rótulos ausentes ficam de fora)
    description: str

    @property
    def num_classes(self) -> int:
        return len(self.classes)

    @property
    def binary(self) -> bool:
        return self.num_classes == 2


TASKS = {
    "c1": Task("c1", ("nao_celula", "celula"),
               {BACKGROUND: 0, **{c: 1 for c in CELL_CLASSES}},
               "Célula × não-célula"),
    "c2": Task("c2", ("sem_lesao", "com_lesao"),
               {"NILM": 0, **{c: 1 for c in LESIONS}},
               "Sem lesão (NILM) × com lesão"),
    "c3": Task("c3", ("baixo_grau", "alto_grau"),
               {**{c: 0 for c in LOW_GRADE}, **{c: 1 for c in HIGH_GRADE}},
               "Baixo grau × alto grau"),
    "c4": Task("c4", ("ASC-US", "LSIL"),
               {"ASC-US": 0, "LSIL": 1},
               "ASC-US × LSIL"),
    "c5": Task("c5", ("ASC-H", "HSIL", "SCC"),
               {"ASC-H": 0, "HSIL": 1, "SCC": 2},
               "ASC-H × HSIL × SCC"),
    "flat7": Task("flat7", CLASSES7,
                  {c: i for i, c in enumerate(CLASSES7)},
                  "Baseline flat: 7 classes (inclui não-célula)"),
    "flat6": Task("flat6", CELL_CLASSES,
                  {c: i for i, c in enumerate(CELL_CLASSES)},
                  "Baseline flat: 6 classes Bethesda"),
}

HIERARCHY = ("c1", "c2", "c3", "c4", "c5")


def get_task(name: str) -> Task:
    if name not in TASKS:
        raise ValueError(f"Tarefa desconhecida '{name}'. Opções: {', '.join(TASKS)}")
    return TASKS[name]

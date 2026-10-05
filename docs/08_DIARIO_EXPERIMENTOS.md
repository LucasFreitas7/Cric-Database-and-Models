# 08 — Diário de experimentos

Um registro por experimento, sempre com: **pergunta → configuração → resultado → decisão**.
Resultados completos ficam em `runs/<experimento>/` (fora do git); aqui só o resumo.
Tabelas: `python scripts/report.py --experiment <nome>`.

---

## baseline_v1 — 05/10/2026

- **Pergunta:** qual é o desempenho real da hierarquia com o protocolo sem vazamento?
- **Configuração:** `configs/default.yaml` — EfficientNet-B0, recorte 70 px, split por imagem (seed 42, 5 folds + teste com 81 imagens), sem aumento offline, `WeightedRandomSampler`, AdamW 3e-4, até 40 épocas, early stopping no F1-macro.
- **Resultado:** *(em execução)*
- **Decisão:** —

---

## Modelo de registro

```
## <nome> — <data>
- Pergunta:
- Configuração: configs/<nome>.yaml (o que muda em relação ao default)
- Resultado: (tabela do report.py ou números principais)
- Decisão:
```

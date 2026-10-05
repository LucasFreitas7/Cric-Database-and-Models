# 04 — Roadmap e melhorias possíveis

> **Atualização 05/10/2026:** Fases 0 e 1 implementadas no pacote `cric/` (cache de patches, split por imagem, aumento online, sampler balanceado, métricas com classe clínica positiva, hierarquia hard/soft). O cronograma com datas está em [07_PLANO_DE_ACAO.md](07_PLANO_DE_ACAO.md); este arquivo fica como lista de ideias.

Organizado em fases. As fases 0–2 são **necessárias** para o artigo ficar defensável; 3–5 são **evoluções** que podem virar contribuição nova.

## Fase 0 — Arrumar a casa (1–2 dias)

- [ ] `git init` real com `.gitignore` (ignorar `base/`, `recortes_*/`, `*.pth`, `.venv/`, `env/`, `build/`, `dist/`); primeiro commit; repositório remoto privado (GitHub).
- [x] Reorganizar pastas; interface antiga e `.pyc` em `legacy/` (falta apagar `src/env/` e `build/` à mão).
- [x] `requirements.txt` completo (falta fixar versões).
- [x] README único e correto.
- [ ] Corrigir bugs A1–A3 da interface (rótulos invertidos + sigmoid) — dá para testar já com os modelos atuais.

## Fase 1 — Pipeline de dados reprodutível (sem vazamento)

Reestruturar em módulos (pacote `cric/` na raiz) em vez de 6 scripts duplicados:

```
cric/
  config.py        # caminhos, tamanho de recorte, seeds, mapeamento de classes
  data.py          # lê JSON → DataFrame (image, x, y, classe) ; recorte on-the-fly
  splits.py        # StratifiedGroupKFold por imagem + test set fixo (salvo em CSV)
  datasets.py      # Dataset PyTorch que recorta da imagem original (sem pastas de recortes)
  models.py        # fábrica de backbones (timm)
  train.py         # loop de treino genérico (AMP, early stopping, seed, logging)
  evaluate.py      # métricas por classe, AUC, matriz de confusão, IC bootstrap
  hierarchy.py     # inferência hierárquica C1→C2→C3→C4/C5
  infer_image.py   # imagem inteira → detecções + classes
```

- [ ] **Split por imagem**: ~15–20% das imagens viram *test set* congelado; nos 80% restantes, `StratifiedGroupKFold(k=5)` agrupado por `image_name`.
- [ ] **Recorte on-the-fly** a partir das coordenadas (sem milhares de PNGs no disco), com padding por reflexão nas bordas.
- [ ] **Aumento de dados só no treino e online** (flip H/V, rotação 90°, jitter de cor/HED, blur leve). Fim do `aumentar_scc.py`/`aumentar_ascus.py`.
- [ ] **Desbalanceamento**: `WeightedRandomSampler` ou *class weights* / *focal loss* em vez de duplicar SCC.
- [ ] Reescrever o gerador de não-célula: amostrar janelas longe de qualquer núcleo anotado + *hard negatives* (bordas de célula, leucócitos, debris).

## Fase 2 — Protocolo de avaliação único (o coração do artigo)

- [ ] Mesmo split, mesma normalização, mesmos epochs/early stopping para todos os modelos.
- [ ] Métricas com a **classe clínica como positiva** (lesão, alto grau): sensibilidade, especificidade, VPP, VPN, F1, AUC-ROC, AUC-PR, acurácia balanceada; média ± desvio entre folds; IC 95% por bootstrap no test set.
- [ ] **Avaliação ponta a ponta da hierarquia** no test set: dado um recorte anotado, passar por C2→C3→C4/C5 e comparar com o rótulo de 6 classes → matriz de confusão 6×6 do sistema hierárquico **vs.** matriz do flat (mesmo backbone).
- [ ] Teste estatístico hierárquico × flat (McNemar no test set).
- [ ] Análise de **propagação de erro** (quanto do erro final vem de cada nível).
- [ ] Ajuste de limiares de C2/C3 para alta sensibilidade (em triagem, perder lesão custa mais que falso positivo) — escolher o limiar na validação, reportar no teste.
- [ ] Também reportar em **2 classes** (normal × anormal) e **3 classes** (normal / baixo / alto), que é como a literatura da CRIC costuma comparar.

## Fase 3 — Modelos melhores

Experimentos baratos com a RTX 4060 (8 GB):
- [ ] **Resolução de entrada**: 70 px nativo vs. upsample para 224; recorte maior (96/128 px) para dar contexto de citoplasma.
- [ ] **Backbones**: EfficientNet-B0/B3, EfficientNetV2-S, ConvNeXt-Tiny, ResNet-50, Swin-T/ViT-S; usar `timm` para todos.
- [ ] **Modelos de fundação para patologia/citologia** (extrator congelado + *linear probe*/fine-tune leve): checar licenças e disponibilidade no Hugging Face (ex.: UNI, Phikon, CONCH, Virchow, DINOv2).
- [ ] **Ensemble** dos 5 folds no teste (média de probabilidades).
- [ ] Treino com AMP (mixed precision), cosine LR, *label smoothing*.
- [ ] **Hierarquia com um backbone compartilhado e várias cabeças** (multi-task) em vez de 5 redes separadas — menos parâmetros e menos propagação de erro.

## Fase 4 — Da classificação de recortes para a imagem inteira

A interface hoje usa janela deslizante cega. Evoluções:
- [ ] **Detecção de núcleos** treinada com as coordenadas da CRIC: YOLOv8/YOLO11 com caixas fixas em torno do ponto, ou detecção por *heatmap* de pontos (estilo CenterNet). Depois, classificar cada detecção com a hierarquia.
- [ ] Métricas de detecção (precisão/revocação por distância ao ponto anotado, ex. ≤ 20 px) + classificação.
- [ ] Usar a coleção de **segmentação** da CRIC (se disponível) para núcleo/citoplasma.
- [ ] Saída por imagem/lâmina: "esta imagem tem célula de alto grau?" (nível de triagem clínica).

## Fase 5 — Explicabilidade e aplicação

- [ ] **Grad-CAM / Grad-CAM++** nos recortes (figura muito boa para o artigo).
- [ ] Interface: mostrar probabilidade, subtipo Bethesda (C4/C5), exportar CSV/relatório, processar pasta inteira, usar GPU se houver.
- [ ] Trocar Tkinter por **Gradio/Streamlit** (demo web local) — mais fácil de mostrar em banca.
- [ ] Empacotar com `sys._MEIPASS` correto ou distribuir como pasta (`--onedir`), que é mais rápido para abrir que `--onefile` com PyTorch.

## Ideias de contribuição para o texto

1. **Hierárquico × flat com protocolo sem vazamento** — muitos trabalhos na CRIC dividem por recorte; mostrar a diferença entre split por recorte e por imagem já é um resultado interessante (dá até uma tabela "antes/depois").
2. **Limiar orientado à sensibilidade clínica** em cada nível da hierarquia.
3. **Pipeline completo imagem → laudo de triagem**, não só recorte.

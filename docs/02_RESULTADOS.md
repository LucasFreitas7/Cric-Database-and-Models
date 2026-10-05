# 02 — Resultados existentes

> ⚠️ **Leia antes de usar estes números no artigo.** Há divergências entre a saída dos notebooks e os CSV/TXT salvos (execuções diferentes), e várias métricas foram calculadas com a **classe positiva trocada** e com **vazamento de dados**. Ver [03_PROBLEMAS_E_PENDENCIAS.md](03_PROBLEMAS_E_PENDENCIAS.md). Na prática, esses resultados devem ser tratados como **preliminares** e refeitos com o protocolo novo do roadmap.

## Atenção: qual é a classe "positiva"?

`torchvision.datasets.ImageFolder` numera as classes em ordem alfabética, e o `sklearn` usa o rótulo **1** como positivo. Então:

| Classificador | Rótulo 0 | Rótulo 1 (= "positivo" nas métricas) |
|---|---|---|
| C1 | celula | **nao_celula** |
| C2 | com_lesao | **sem_lesao** |
| C3 | alto_grau | **baixo_grau** |

Consequência: em C2, a "Revocação" reportada é a sensibilidade para **células normais**, e a "Especificidade" é, na verdade, a **sensibilidade para lesão**. O mesmo vale para C3 (a "Especificidade" é a sensibilidade para **alto grau**). Nas tabelas abaixo isso já está traduzido na última coluna.

## C1 — célula × não-célula (EfficientNet-B0, hold-out 70/30, 18.000 recortes)

| Fonte | Acurácia | Precisão | Revocação | Especificidade | F1 |
|---|---:|---:|---:|---:|---:|
| `results/c1/metricas_classificador1.txt` | 0,9428 | 0,9576 | 0,9286 | 0,9574 | 0,9429 |
| saída do notebook | 0,9331 | 0,9250 | 0,9431 | 0,9231 | 0,9340 |

## C2 — com lesão × sem lesão (EfficientNet-B0, KFold 3, 11.534 recortes)

| Fold | Acurácia | Precisão* | Revocação* | F1* | Especif.* → **Sensib. lesão** |
|---|---:|---:|---:|---:|---:|
| 1 | 0,9030 | 0,8752 | 0,9708 | 0,9205 | 0,8100 |
| 2 | 0,9064 | 0,9359 | 0,9028 | 0,9190 | 0,9115 |
| 3 | 0,9045 | 0,9361 | 0,9014 | 0,9184 | 0,9091 |
| **Média (CSV)** | **0,9046** | 0,9157 | 0,9250 | 0,9193 | **0,8769** |
| Média (notebook, outra execução) | 0,9117 | 0,9227 | 0,9277 | 0,9250 | 0,8891 |

\* calculadas com "sem lesão" como positivo.

## C3 — baixo × alto grau (EfficientNet-B0, StratifiedKFold 3, 4.755 recortes)

| Fold | Acurácia | Precisão* | Revocação* | F1* | Especif.* → **Sensib. alto grau** |
|---|---:|---:|---:|---:|---:|
| 1 | 0,9312 | 0,9320 | 0,8992 | 0,9153 | 0,9538 |
| 2 | 0,9256 | 0,9137 | 0,9053 | 0,9095 | 0,9398 |
| 3 | 0,9312 | 0,8924 | 0,9482 | 0,9194 | 0,9193 |
| **Média (CSV)** | **0,9293** | 0,9127 | 0,9176 | 0,9148 | **0,9376** |
| Média (notebook) | 0,9264 | 0,9060 | 0,9186 | 0,9118 | 0,9319 |

\* calculadas com "baixo grau" como positivo.

## C4 — ASC-US × LSIL (EfficientNet-B0, KFold 3, 2.710 recortes, 744 sintéticos)

Métricas macro.

| Fold | Acurácia | Precisão | Revocação | F1 |
|---|---:|---:|---:|---:|
| 1 | 0,8330 | 0,8343 | 0,8338 | 0,8329 |
| 2 | 0,8261 | 0,8256 | 0,8258 | 0,8257 |
| 3 | 0,8461 | 0,8516 | 0,8471 | 0,8457 |
| **Média (CSV)** | **0,8351** | 0,8372 | 0,8356 | 0,8348 |
| Média (notebook) | 0,8258 | 0,8260 | 0,8260 | 0,8257 |

## C5 — ASC-H × HSIL × SCC (EfficientNet-B0, KFold 3, 3.628 recortes, 839 sintéticos)

| Fold | Acurácia | Precisão | Revocação | F1 |
|---|---:|---:|---:|---:|
| 1 | 0,8777 | 0,8780 | 0,8767 | 0,8773 |
| 2 | 0,8586 | 0,8580 | 0,8534 | 0,8556 |
| 3 | 0,8602 | 0,8564 | 0,8617 | 0,8588 |
| **Média** | **0,8655** | 0,8641 | 0,8640 | 0,8639 |

## Baseline flat — ConvNeXt-Tiny 7 classes (StratifiedKFold 3, 22.117 recortes)

| Fold | Acurácia | Precisão (macro) | Revocação (macro) | F1 (macro) |
|---|---:|---:|---:|---:|
| 1 | 0,8650 | 0,7665 | 0,7253 | 0,7427 |
| 2 | 0,8658 | 0,7531 | 0,7643 | 0,7572 |
| 3 | 0,8607 | 0,7732 | 0,7194 | 0,7235 |
| **Média** | **0,8639** | 0,7643 | 0,7364 | **0,7412** |

F1 por classe (fold 1 / 2 / 3):

| Classe | F1 fold 1 | F1 fold 2 | F1 fold 3 |
|---|---:|---:|---:|
| ASC-H | 0,53 | 0,59 | 0,41 |
| ASC-US | 0,68 | 0,70 | 0,65 |
| HSIL | 0,73 | 0,76 | 0,76 |
| LSIL | 0,53 | 0,53 | 0,55 |
| SCC | 0,87 | 0,87 | 0,83 |
| não-célula | 0,98 | 0,98 | 0,98 |
| NILM | 0,89 | 0,89 | 0,89 |

Leitura: a acurácia de 86% é puxada pelas classes grandes (não-célula, NILM). As classes clínicas difíceis (ASC-H, LSIL) ficam em ~0,5 de F1. O SCC com F1 0,87 está **inflado** pelos 839 recortes sintéticos (vazamento).

> A pasta `results/flat_convnext/` tem matrizes de confusão de **10 folds**, mas o CSV tem 3 → houve uma execução com 10 folds cujos números não foram salvos.

## O que falta para uma comparação justa hierárquico × flat

Os números acima **não são comparáveis entre si**: cada classificador foi avaliado isoladamente, em recortes "perfeitos" (centrados na anotação), com splits diferentes. Nunca foi medido:
- o desempenho do **sistema hierárquico completo** (erro de C1 propaga para C2, que propaga para C3…);
- o desempenho **na imagem inteira** (detecção + classificação), que é o que a interface faz.

Isso é o item nº 1 do [roadmap](04_ROADMAP_MELHORIAS.md).

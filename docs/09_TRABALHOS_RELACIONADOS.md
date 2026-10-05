# 09 — Candidatos para os trabalhos relacionados (Cap. 2)

Levantamento feito em 05/10/2026 para atualizar o Cap. 2. **👤 Validar cada item lendo o artigo** antes de citar — aqui só está o que a busca retornou. Status: ⬜ a ler · ✅ lido e entra · ❌ descartado.

## Base de dados e grupo CRIC (UFOP)

| Status | Referência | Por que importa |
|---|---|---|
| ⬜ | Rezende, M. T. et al. *Cric searchable image database as a public platform for conventional pap smear cytology data.* **Scientific Data** 8, 2021. https://www.nature.com/articles/s41597-021-00933-8 | **Referência correta da base** (substitui o `rezende2021cervical` atual — item L6). 400 imagens 1.376×1.020, 11.534 células, 3 citopatologistas. |
| ⬜ | Diniz, D. N.; Rezende, M. T.; Bianchi, A. G. C. et al. *A deep learning ensemble method to assist cytopathologists in Pap test image classification.* **Journal of Imaging** 7(7):111, 2021. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8321382/ | Deep learning na CRIC pelo mesmo grupo — **comparação direta obrigatória** (2, 3 e 6 classes). |
| ⬜ | Diniz, D. N. et al. *A Hierarchical Feature-Based Methodology to Perform Cervical Cancer Classification.* **Applied Sciences** 11(9):4091, 2021. https://dx.doi.org/10.3390/app11094091 | Já citado (`diniz2021hierarchical`) — a hierarquia em que o trabalho se inspira. |
| ⬜ | Freitas, L. A. et al. SBCAS 2023 (`freitas2023prediccao`) | Trabalho anterior do autor (recortes 70×70). |

## Novas bases (validação externa)

| Status | Referência | Por que importa |
|---|---|---|
| ⬜ | *RIVA: An Image Dataset of Conventional Pap Smear Cytology with Multiple Independent Annotations.* **Scientific Data** 12, 1991, dez/2025. https://www.nature.com/articles/s41597-025-06280-2 · dados: https://zenodo.org/records/17288879 | Papanicolau **convencional**, 959 imagens 1024×1024 (40x), 115 pacientes, até 4 anotadores, 15.949 células, classes Bethesda (SCC, HSIL, ASC-H, LSIL, ASC-US + NILM, ENDO, INFL). **Permite testar o modelo treinado na CRIC em outra base** (generalização). Teve um desafio (RIVA Cervical Cytology Challenge) com artigos de detecção em 2026. |
| ⬜ | *Annotated Pap cell images and smear slices for cell classification.* Scientific Data, 2024. https://www.nature.com/articles/s41597-024-03596-3 | Outra base anotada recente. |

## Vazamento de dados (para justificar o split por imagem)

| Status | Referência | Por que importa |
|---|---|---|
| ⬜ | Bussola, N. et al. *AI slipping on tiles: data leakage in digital pathology.* ICPR Workshops, 2021. https://arxiv.org/abs/1909.06539 | Mostra estimativas infladas em até 41% quando recortes do mesmo paciente aparecem em treino e validação — **é exatamente o nosso experimento leakage_v1**. |

## Estado da arte recente (2024–2026)

| Status | Referência | Por que importa |
|---|---|---|
| ⬜ | Revisão sistemática: *A systematic review of deep learning-based cervical cytology screening: from cell identification to whole slide image analysis.* Artificial Intelligence Review, 2023. https://link.springer.com/article/10.1007/s10462-023-10588-z | Visão geral para o Cap. 2. |
| ⬜ | Revisão sistemática: *A systematic review on deep learning based methods for cervical cell image analysis.* Neurocomputing, 2024. https://www.sciencedirect.com/science/article/pii/S0925231224014012 | Idem. |
| ⬜ | *CVM-Cervix: CNN + Visual Transformer + MLP.* Pattern Recognition, 2022. https://arxiv.org/abs/2206.00971 | Híbrido CNN/ViT. |
| ⬜ | *A hierarchical framework for cervical cell classification using attention-based multi-scale local binary CNNs.* 2025. https://www.sciencedirect.com/science/article/pii/S2590093525000438 | **Hierarquia recente** — comparar com a nossa. |
| ⬜ | *CNN based method for classifying cervical cancer cells in pap smear images.* Scientific Reports, 2025. https://www.nature.com/articles/s41598-025-10009-x | CNN recente. |
| ⬜ | *Robust Cell-Level Classification for Liquid-Based Cervical Cytology Using Deep Transfer Learning: A Multi-Source Study* (usa CRIC, Herlev, SIPaKMeD). Bioengineering, 2026. https://doi.org/10.3390/bioengineering13030289 | Mistura bases incluindo CRIC; robustez entre domínios. |
| ⬜ | *UniCAS: A foundation model for cervical cytology screening.* Cell Reports Medicine, 2025. https://www.cell.com/cell-reports-medicine/fulltext/S2666-3791(25)00643-3 | **Modelo de fundação** para citologia cervical (48 mil lâminas) — contexto para o experimento E6. |
| ⬜ | *An efficient framework based on large foundation model for cervical cytopathology WSI screening.* 2024. https://arxiv.org/abs/2407.11486 | Modelo de fundação + lâmina inteira. |
| ⬜ | *CerviCell-detector: object detection for cancerous cells in pap smear images.* Heliyon, 2023. https://www.cell.com/heliyon/fulltext/S2405-8440(23)09532-4 | Detecção (para a parte de imagem inteira). |

## Próximos passos

1. 👤 Ler os ⬜ e marcar ✅/❌ (prioridade: Rezende 2021, Diniz 2021 J. Imaging, RIVA, Bussola, hierárquico 2025).
2. 🤖 Gerar as entradas BibTeX dos ✅ e redigir os parágrafos novos do Cap. 2 para revisão.
3. 🤖 Montar a tabela comparativa "trabalhos × base × classes × protocolo de divisão × resultado".

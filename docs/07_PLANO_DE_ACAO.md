# 07 — Plano de ação (out → dez/2026)

**Meta:** dissertação defendida em **dezembro/2026**, com todos os resultados refeitos no protocolo novo (sem vazamento) e a comparação **hierárquico × flat** como contribuição central.

**Premissa** (confirmar): texto completo com a orientadora até **o fim de novembro**, e defesa em dezembro.

Legenda: 👤 Lucas · 🤖 Claude · 🎓 orientadora · ✅ feito

---

## Visão geral

| Sprint | Datas | Tema | Entregável |
|---|---|---|---|
| **S1** | 05/10 – 18/10 | Fundação + baseline novo | Tabela com os resultados do baseline_v1 (5 folds) + texto corrigido nos pontos simples |
| **S2** | 19/10 – 01/11 | Melhorar os modelos | Configuração final escolhida (backbone, resolução, balanceamento) |
| **S3** | 02/11 – 15/11 | Hierarquia final, teste e imagem inteira | Números finais no teste + Grad-CAM + app atualizado |
| **S4** | 16/11 – 29/11 | Escrita | Caps. 3, 4 e 5 completos → enviar à orientadora 🎓 |
| **S5** | 30/11 – defesa | Revisões e defesa | Versão final + slides + ensaio |

Ritmo semanal sugerido: **segunda**, a gente escolhe as tarefas da semana neste arquivo; **durante a semana**, os experimentos rodam em segundo plano (o PC fica treinando); **sexta**, os resultados são registrados em [08_DIARIO_EXPERIMENTOS.md](08_DIARIO_EXPERIMENTOS.md) e mandamos um resumo curto para a orientadora 🎓.

---

## S1 — Fundação + baseline novo (05/10 – 18/10)

**Código**
- [x] ✅ Estrutura do projeto reorganizada + git (`Cric-Database-and-Models`)
- [x] ✅ Pacote `cric/` + comandos em `scripts/` + `configs/default.yaml`
- [x] ✅ Cache de patches reais (23.534: 11.534 células + 12.000 fundo) — sem aumento offline
- [x] ✅ Split **por imagem**: teste com 81 imagens + 5 folds (`data/splits/splits_seed42.csv`)
- [x] ✅ Bug dos rótulos invertidos da interface corrigido (A1–A3)
- [ ] 🤖 Rodar o **baseline_v1** (EfficientNet-B0, 70 px): C1–C5 + flat7 + avaliação hierárquica *(em execução)*
- [ ] 🤖 **Experimento do vazamento**: mesmo modelo com split por recorte + aumento offline (protocolo antigo) × split por imagem. Mostra o quanto os números antigos estavam inflados — vira uma tabela/argumento forte na dissertação.
- [ ] 🤖 Gerador do C1 documentado (agora é o `build_cache` + jitter de 25 px = regra da fronteira de 10 px)

**Texto** (correções rápidas — ver [06](06_ANALISE_DISSERTACAO.md))
- [ ] 🤖 Capa/metadados de mestrado (T1) — 👤 passar nome do programa, banca e data
- [ ] 🤖 Erros factuais: colunas trocadas (T2), "sexto classificador" (T3), NILM como anormal (T4), 6×7 classes (T5), objetivo 3 (T6)
- [ ] 🤖 LaTeX: `\texit`, labels, `\cite{unknown}`, `.bib` duplicado (L1–L5)
- [ ] 👤 Conferir referências da CRIC e do GLOBOCAN (L6, L7)
- [ ] 👤 Começar a atualizar os trabalhos relacionados (T11) — 🤖 posso montar uma lista de candidatos para você validar

**Decisões no fim da S1**
- O baseline novo ficou muito abaixo do antigo? (Esperado: sim, principalmente C4/C5/SCC.) → a dissertação passa a discutir isso como resultado.
- 🎓 Mostrar o plano e a análise de vazamento para a orientadora.

---

## S2 — Melhorar os modelos (19/10 – 01/11)

Cada experimento é um YAML em `configs/` (só com o que muda) e responde a **uma pergunta**. Rodar primeiro em **c2, c3 e c5** (as tarefas que mais importam e que são rápidas) e só levar o vencedor para todas.

| Exp. | Config | Pergunta | Custo |
|---|---|---|---|
| E2 | `img_size: 224` | Ampliar 70→224 ajuda a rede pré-treinada? | médio |
| E3 | `crop_size: 96` / `112` | Mais contexto (citoplasma) ajuda? | baixo |
| E4 | `model.name: convnext_tiny`, `efficientnetv2_rw_s`, `resnet50` | Qual backbone? | médio |
| E5 | `balance: none / sampler / loss` | Como tratar o desbalanceamento (SCC = 161)? | baixo |
| E6 | DINOv2 / modelo de fundação congelado + classificador linear | Representações modernas superam o fine-tuning? | médio |
| E7 | `label_smoothing: 0.1`, warmup, épocas | Ajuste fino de treino | baixo |

- [ ] 🤖 Criar os YAMLs e rodar E2–E5 (cada um roda sozinho no PC, ~30–60 min por tarefa)
- [ ] 🤖 `scripts/report.py` gera a tabela comparativa (Markdown + LaTeX)
- [ ] 👤 Revisar Cap. 2 (fundamentação) e enviar trechos para revisão
- [ ] **Decisão**: configuração final = melhor F1-macro médio em validação (nunca olhar o teste aqui)

---

## S3 — Hierarquia final, teste e imagem inteira (02/11 – 15/11)

- [ ] 🤖 Treinar todas as tarefas com a configuração final
- [ ] 🤖 Hierarquia **hard × soft × flat7** em 7, 3 e 2 classes (já implementado em `cric/hierarchy.py`)
- [ ] 🤖 **Limiar orientado à sensibilidade** no C2 (perder lesão custa mais que falso positivo)
- [ ] 🤖 Teste estatístico hierárquico × flat (McNemar / bootstrap)
- [ ] 🤖 **Avaliação no teste — uma única vez**: `python scripts/evaluate_hierarchy.py --split test`
- [ ] 🤖 **Grad-CAM** em exemplos de cada classe (figura para a dissertação)
- [ ] 🤖 **Imagem inteira**: mapa de calor do C1 + detecção de núcleos, com avaliação contra os pontos anotados (precisão/revocação num raio de ~20 px)
- [ ] 🤖 Interface: usar os modelos novos, caixas centradas nas detecções, mostrar a classe Bethesda (C4/C5) e a probabilidade
- [ ] 👤 Prints da interface nova para a dissertação

---

## S4 — Escrita (16/11 – 29/11)

Estrutura proposta em [06](06_ANALISE_DISSERTACAO.md#proposta-de-nova-estrutura-versão-de-defesa).

- [ ] 🤖👤 Cap. 3 — Materiais e métodos (base, cache, split por imagem, hierarquia, flat, métricas, imagem inteira)
- [ ] 🤖👤 Cap. 4 — Resultados (tabelas geradas pelo `report.py`, matrizes de confusão, Grad-CAM, vazamento)
- [ ] 👤 Cap. 5 — Discussão e conclusão; resumo/abstract com números
- [ ] 👤 Revisão geral + 🎓 envio à orientadora (**29/11**)

## S5 — Revisões e defesa (30/11 – dezembro)

- [ ] 👤🤖 Incorporar as correções da orientadora
- [ ] 👤 Slides (🤖 posso montar um rascunho a partir da dissertação)
- [ ] 👤 Ensaio da apresentação
- [ ] 🤖 Congelar o código: tag `v1.0-defesa` no git + README final

---

## Riscos e planos B

| Risco | Plano B |
|---|---|
| Resultados novos bem piores que os da qualificação | Assumir e explicar: o protocolo novo é mais honesto; a análise de vazamento vira contribuição |
| SCC com só 161 células (25–31 por fold) → métricas instáveis | Reportar também em 3 e 2 classes; IC por bootstrap; discutir como limitação |
| Hierárquico não supera o flat | Ainda é resultado: discutir propagação de erro, soft × hard; a hierarquia dá interpretabilidade e limiares por nível |
| Falta de tempo | Cortar na ordem: E6 → detecção na imagem inteira → app. **Nunca** cortar o baseline novo nem a comparação hierárquico × flat |
| PC ocupado/desligado | Rodar à noite; cada fold salva o resultado, então dá para retomar com `--folds` |

# 06 — Análise da dissertação (texto × código)

Repositório do texto: `docs/artigo/` → GitHub `LucasFreitas7/Disserta-o---Lucas-Andrade-Freitas` (sincronizado com o Overleaf via GitHub Sync).
Classe `abntex2`, arquivo principal `Monografia.tex`, capítulos em `Capitulos/`. Análise feita em 05/10/2026.

## Fluxo de sincronização

1. Antes de eu editar: no Overleaf, **Menu → GitHub → Push Overleaf changes to GitHub**; aqui, `git pull` em `docs/artigo`.
2. Eu edito o `.tex`, mostro o diff e, com o seu ok, faço `commit` + `push`.
3. No Overleaf, **Menu → GitHub → Pull GitHub changes into Overleaf**.

## Diagnóstico geral

O texto atual é a **versão da qualificação**: o Cap. 4 se chama "Resultados Preliminares", o resumo fala no futuro ("espera-se"), há cronograma, e a conclusão diz que falta integrar os classificadores. A metodologia do texto **não corresponde ao código atual** (outra biblioteca, outro protocolo e outros números).

### Texto × código

| Aspecto | Dissertação (Cap. 3–4) | Código atual (notebooks) |
|---|---|---|
| Framework | TensorFlow/Keras | PyTorch |
| Hardware | Colab, Nvidia K80 | GPU local (CUDA) |
| Épocas | 40 em todos | 3 a 20 (varia por classificador) |
| Divisão | "70/30" **e** "k-fold 3" (os dois ao mesmo tempo) | C1: hold-out 70/30; C2–C5: k-fold 3 |
| C1 célula / não-célula | 11.534 / 11.600 | 9.000 / 9.000 |
| C4 / C5 | sem aumento (ASC-US 606, SCC 161) | com aumento offline (ASC-US 1.350, SCC 1.000) |
| Acurácia C1 / C2 / C3 / C4 / C5 | **0,98 / 0,97 / 0,96 / 0,94 / 0,92** | **0,94 / 0,90 / 0,93 / 0,83 / 0,87** |
| Baseline flat (ConvNeXt 7 classes) | não aparece | 0,86 acc / 0,74 F1-macro |
| Interface / sistema integrado | não aparece (há prints em `Figuras/` sem uso) | existe, mas com rótulos invertidos |

➡️ **Nenhum código deste repositório gera os números do Cap. 4.** Ou existe um código antigo em Keras (Colab?) que não está aqui, ou os números precisam ser refeitos. De qualquer forma, com o protocolo novo (split por imagem, sem vazamento) os resultados vão mudar e o Cap. 4 será reescrito.

## Problemas de conteúdo

| # | Onde | Problema |
|---|---|---|
| T1 | capa (`Monografia.tex`) | Metadados do modelo de graduação: `\tipotrabalho{Monografia}`, `\grau{Bacharel em Ciência da Computação}`, `\ano{2024}`, "XX de mês", banca com placeholders. Trocar por Dissertação / Mestre / PPGCC-UFOP. |
| T2 | Cap. 3, tabelas C2 e C3 | **Colunas trocadas**: C2 mostra "Com lesão = 6.779" (o certo é 4.755; 6.779 é NILM); C3 mostra "Alto grau = 1.966" (o certo é 2.789). |
| T3 | Cap. 3, Modelo Proposto | Fala em "quinto classificador" (alto grau) e "sexto" (baixo grau), mas só existem 5; nas tabelas, C4 = baixo grau e C5 = alto grau. |
| T4 | Cap. 3, Base CRIC | "células com lesão ou anormal (LSIL, HSIL, ASC-H, ASC-US, **NILM**)" — NILM não é anormal e falta o SCC. |
| T5 | Cap. 1 × Cap. 5 | Objetivos falam em **7 classes**; a conclusão fala em **6**. |
| T6 | Cap. 1, objetivo 3 | "sem a necessidade de segmentar **ou analisar recortes individuais**" contradiz o método, que é todo baseado em recortes. |
| T7 | Cap. 4, discussão | Diz "classificador 4 com 0.92", mas a tabela mostra acurácia 0,94. |
| T8 | Cap. 4, tabelas | Especificidade para o C5 (3 classes) sem dizer como foi calculada (macro? one-vs-rest?); "± %" sem dizer se é desvio-padrão entre folds. |
| T9 | Cap. 2, métricas | TP/TN são definidos com "anormal = positivo", mas o código calculou com a classe positiva trocada (ver `03`, item B3). |
| T10 | Cap. 3 | Não descreve o aumento de dados, a votação por grade, o sistema integrado, nem a comparação com o modelo flat. |
| T11 | Cap. 2 | Revisão de trabalhos relacionados curta e majoritariamente até 2023; faltam trabalhos de deep learning na própria CRIC e trabalhos recentes (2024–2026), ViT/modelos de fundação em citologia, detecção de células. |
| T12 | Resumo/Abstract | Escrito no futuro; sem resultados numéricos. |
| T13 | Cap. 5 | Cronograma da qualificação (com uma tabela aninhada quebrada) — remover na versão final. |
| T14 | Estilo | Mistura de 1ª pessoa do singular ("abordarei") e do plural; vários erros de digitação ("anteorimente", "Mémoria", "Especifidade", "a de uma metodologia"). |

## Problemas de LaTeX / referências

| # | Problema |
|---|---|
| L1 | `\texit{com lesão}` (Cap. 3, Modelo Proposto) — comando inexistente; deveria ser `\textit`. |
| L2 | `\label{tabelaCric}` está **fora** do ambiente `table` → `\ref{tabelaCric}` aponta para a seção errada. |
| L3 | Figura da EfficientNet com `\label{inception}` e `\cite{unknown}`. |
| L4 | `\include` de arquivos que não existem: FichaCatalografica, Errata, FichaAprovacao, Dedicatoria, Agradecimento, Epigrafe, Cap6-TrabalhosFuturos, Apendice, Anexo. |
| L5 | Entradas duplicadas no `.bib` para o mesmo artigo: `freitas2023prediccao` e `freitas2023citologia` (SBCAS 2023). |
| L6 | `rezende2021cervical` tem título "Cervical cancer: Automation of pap test screening" (Diagnostic Cytopathology). O artigo que descreve a base CRIC é outro (Rezende et al., *Scientific Data*, 2021) — **conferir e citar o correto**. |
| L7 | `globocan2023cervical` ("Global cancer statistics 2023"?) — conferir; os números de 604 mil casos / 342 mil mortes são do GLOBOCAN 2020 (Sung et al., 2021, *CA Cancer J Clin*). A taxa de falso-negativo de 2–62% está citada com a mesma referência do GLOBOCAN — precisa de outra fonte. |
| L8 | Figuras não usadas: `30x30Matriz.png` … `90x90Matriz.png` (podem justificar a escolha do 70×70), `Home.png`, `Tela-Analise-2.png`, `Tela-conclusao.png`, `tela-incial-analise.png` (interface), `Predição Modelo.jpeg`, `mobileNet.png`, `rede-neural.png`, etc. |

## O que dá para aproveitar

- Cap. 1 (motivação) e Cap. 2 (fundamentação de CNN, métricas, transfer learning, ViT/ConvNeXt) estão razoáveis — precisam de revisão e atualização, não de reescrita.
- Cap. 3: a descrição da base, do recorte centralizado/descentralizado e da regra de fronteira (10 px) continua válida — **a regra dos 10 px é a informação que faltava para reconstruir o gerador C1 perdido**.

## Proposta de nova estrutura (versão de defesa)

1. **Introdução** — motivação, problema, objetivos (corrigidos), contribuições.
2. **Fundamentação e trabalhos relacionados** — atualizada até 2026.
3. **Materiais e métodos** — base; recortes; **protocolo sem vazamento (split por imagem + test set)**; hierarquia; baseline flat; métricas com a classe clínica como positiva; aplicação na imagem inteira.
4. **Resultados** — cada nível; **hierárquico × flat ponta a ponta**; análise de erros; Grad-CAM; resultados na imagem inteira; interface.
5. **Discussão** — comparação com a literatura da CRIC, limitações (incluindo o efeito do vazamento: "split por recorte × por imagem").
6. **Conclusão e trabalhos futuros.**

## Perguntas em aberto

1. Existe um código em Keras/Colab que gerou os números do Cap. 4? (Se existir, vale trazer para `legacy/`.)
2. Os números do Cap. 4 foram publicados em algum lugar (SBCAS? artigo da qualificação)?
3. Nome do programa, orientadora (Andrea G. Campos?), coorientador e banca para a capa.
4. Prazo da defesa.

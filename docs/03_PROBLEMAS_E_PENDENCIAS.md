# 03 — Problemas encontrados e pendências

Classificação: 🔴 crítico (invalida resultado/app) · 🟠 importante (enfraquece o artigo) · 🟡 menor/limpeza.

## A. Bugs na interface / aplicação

| # | Sev. | Problema | Onde | Efeito |
|---|---|---|---|---|
| A1 | ✅ | **[corrigido 05/10] Rótulo de C2 invertido.** No treino `com_lesao=0`, `sem_lesao=1`; a interface faz `has_lesion = model2(x) > 0.45`, ou seja, marca como lesão o que o modelo acha que é **normal**. | `app/interface_hierarquica.py` (`process_crop`) | Células normais aparecem como lesão e vice-versa. Confirmado visualmente em `results/interface/resultado_hierarquico.png` (células escamosas superficiais/intermediárias normais em vermelho). |
| A2 | ✅ | **[corrigido 05/10] Rótulo de C3 invertido.** `alto_grau=0`, `baixo_grau=1`; a interface faz `is_high_grade = model3(x) > 0.5`. | idem | Baixo grau ↔ alto grau trocados. |
| A3 | ✅ | **[corrigido 05/10] Sem `sigmoid`.** O modelo devolve *logit*, mas é comparado com 0,5/0,45 como se fosse probabilidade. Limiar 0,5 em logit ≈ probabilidade 0,62. | idem (e `interface.py`) | Limiares descalibrados. |
| A4 | 🟠 | Votação com "≥ 1 voto" (OR) entre 3 grades. | idem | Aumenta falsos positivos; o ideal é média de probabilidades ou maioria. |
| A5 | 🟠 | Varredura em grade cega 70×70; a caixa não fica centrada na célula, uma célula pode cair entre 4 janelas, e C1 foi treinado com recortes "célula" centrados (± tolerância). | idem | Detecção imprecisa / contagem duplicada. |
| A6 | 🟠 | No `.exe` *onefile*, os `datas` são extraídos para `sys._MEIPASS`, mas o código procura `models/` ao lado do executável (`os.path.dirname(sys.executable)`). | interface + `.spec` | O `.exe` provavelmente não encontra os modelos se a pasta `models/` não estiver ao lado dele. |
| A7 | 🟡 | `legacy/interface_antiga.py` redimensiona recorte para 224×224, mas os modelos foram treinados em 70×70. | `legacy/` | Já arquivada em `legacy/`. |
| A8 | 🟡 | `pathex` com caminho absoluto fixo; `console=False` esconde erros; `resultado_hierarquico.png` empacotado no exe sem necessidade. | `.spec` | Build frágil. |
| A9 | 🟡 | C4 e C5 não estão integrados na interface (só 3 níveis). | — | A app não mostra o subtipo Bethesda. |

**Evidência de A1/A2** (05/10/2026, 300 recortes reais por pasta, `sigmoid` da saída dos `.pth` salvos):

| Modelo | Pasta | sigmoid médio | fração > 0,5 |
|---|---|---:|---:|
| C1 | celula / nao_celula | 0,032 / 0,964 | 0,03 / 0,97 |
| C2 | com_lesao / **sem_lesao** | 0,116 / **0,926** | 0,08 / 0,97 |
| C3 | alto_grau / **baixo_grau** | 0,033 / **0,966** | 0,02 / 0,98 |

Saída alta = `sem_lesao` (C2) e `baixo_grau` (C3); a interface trata saída alta como "lesão" e "alto grau". **Correção**: `has_lesion = sigmoid(model2(x)) < t2` e `is_high_grade = sigmoid(model3(x)) < t3`.
(Obs.: esses recortes provavelmente estavam no treino, então os valores são quase perfeitos — servem só para mostrar a **direção** dos rótulos.)

## B. Problemas metodológicos (afetam o artigo)

| # | Sev. | Problema | Detalhe |
|---|---|---|---|
| B1 | 🔴→✅ | **[resolvido no pipeline novo `cric/`] Vazamento por aumento offline.** `aumentar_scc.py`/`aumentar_ascus.py` gravam versões aumentadas (`aug_scc_*.png`) **na mesma pasta** antes do K-fold. Uma imagem de validação tem "gêmeas" aumentadas no treino. | Afeta C4, C5 e o flat. SCC: 839 de 1.000 recortes são sintéticos, gerados de só **161** reais. ASC-US: 744 de 1.350. Os números de SCC e ASC-US estão superestimados. |
| B2 | 🔴→✅ | **[resolvido no pipeline novo] Split por recorte e não por imagem/lâmina.** Recortes da mesma imagem (mesmo campo, mesma coloração, células vizinhas que se sobrepõem no recorte) caem no treino e na validação. | Todos os classificadores. Precisa `StratifiedGroupKFold` com `groups = image_name`. |
| B3 | 🔴→✅ | **[resolvido no pipeline novo] Classe positiva trocada nas métricas** (ver [02_RESULTADOS.md](02_RESULTADOS.md)). | A "revocação" reportada de C2 é da classe normal; a sensibilidade para lesão real é ~0,88 (não ~0,93). |
| B4 | 🟠 | **Sem conjunto de teste independente.** Só validação cruzada, e hiperparâmetros/épocas foram mexidos olhando a validação. | Precisa de um test set separado (por imagem) tocado uma única vez. |
| B5 | 🟠 | **Augmentação aleatória na validação** (C3, C4, C5 usam a mesma `transform` com flip/rotação para treino e validação). | Métricas ruidosas e não reprodutíveis. |
| B6 | 🟠 | **Normalização inconsistente**: C1–C3 ImageNet; C4/C5 nenhuma; ConvNeXt `[0.5]`. | Dificulta comparação/integração. |
| B7 | 🟠 | **Hierarquia nunca avaliada ponta a ponta** nem comparada com o flat no mesmo split. | É justamente a contribuição do trabalho. |
| B8 | 🟠 | Modelo salvo = **último fold** (treinado em 2/3 dos dados), não um modelo final em 100% do treino nem ensemble dos folds. | C2, C3. |
| B9 | 🟠 | Sem semente fixa (`torch.manual_seed`), sem early stopping, sem curvas de validação; nº de épocas muito diferente entre modelos (3 a 20). | Reprodutibilidade. |
| B10 | 🟠 | Imagens 70×70 entram direto em redes pré-treinadas em 224×224 (EfficientNet reduz para ~3×3 no fim). | Provável perda de desempenho; testar upsample para 224 ou recortes maiores. |
| B11 | 🟡 | Não-célula foi amostrada de grade aleatória — recortes "difíceis" (leucócitos, debris, bordas de células) podem estar sub-representados. | Hard negative mining. |
| B12 | 🟡 | Recortes na borda: `max(x-35,0)` desloca o núcleo do centro; à direita/embaixo o PIL preenche com preto. | Pequeno ruído. |
| B13 | 🟡 | Métricas só como média; falta desvio-padrão, intervalo de confiança, AUC, matriz de confusão agregada. | Rigor estatístico. |

## C. Coisas faltando / perdidas

| # | Sev. | Item |
|---|---|---|
| C1 | 🔴→✅ | **[substituído por `cric/data.py` + jitter] Código-fonte do gerador célula × não-célula perdido** (`main.py`, `config.py`, `preprocessor.py` só existem como `.pyc` de Python 3.14). A lógica foi reconstruída pelas strings do bytecode: grade `CROP_SIZE`, `is_cell_in_crop` com `TOLERANCE` em torno do centro. O valor de `TOLERANCE` e o critério de balanceamento 9.000/9.000 não são conhecidos → reescrever. |
| C2 | 🟠 | Git: `.gitignore` criado e commit inicial feito em 05/10/2026; falta repositório remoto (GitHub) e backup de dados/modelos. |
| C3 | 🟠 | O notebook do C1 referencia `example_input` não definido e não tem `torch.save` → origem do `classificador1.pth` não é rastreável. |
| C4 | 🟠 | Resultados dos notebooks ≠ CSV/TXT salvos (execuções diferentes). Não se sabe qual entrou no artigo. |
| C5 | 🟠 | Execução de ConvNeXt com 10 folds sem CSV. |
| C6 | 🟡 | `requirements.txt` incompleto (faltam numpy, pandas, scikit-learn, matplotlib, seaborn, tqdm, timm). |
| C7 | ✅ | ~~`README.md` com duas versões coladas~~ — reescrito em 05/10/2026. |
| C8 | 🟡 | Pasta antiga `src/` (venv quebrado `src/env/` + 3 PNG duplicados da base) e `build/` ainda no disco — apagar à mão (já fora do git). |
| C9 | 🟡 | Pequenos bugs nos geradores: `print(... rotulo == "LSIL" or "ASC-US")` sempre verdadeiro (só no print); `aumentar_ascus.py` salva como `aug_scc_*`; função `is_LISL`. Muito código duplicado entre os 4 geradores. |
| C10 | 🟡 | Citação da base no README está incompleta ("Mariana, Claudia, Alessandra"). |

## D. Ordem sugerida de correção

1. Versionar (git + `.gitignore`) — **C2**
2. Corrigir rótulos/sigmoid da interface — **A1, A2, A3** (rápido, alto impacto)
3. Reescrever pipeline de dados com split por imagem e test set — **B1, B2, B4, C1**
4. Retreinar tudo com protocolo único — **B3, B5, B6, B8, B9**
5. Avaliação ponta a ponta hierárquico × flat — **B7**
6. Demais melhorias → [04_ROADMAP_MELHORIAS.md](04_ROADMAP_MELHORIAS.md)

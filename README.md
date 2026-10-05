# Classificador Hierárquico de Células Cervicais (CRIC)

Dissertação de mestrado (UFOP): classificação de células de Papanicolau segundo o Sistema Bethesda, na base **CRIC Cervix** (400 imagens, 11.534 células), usando uma cascata de CNNs comparada a um classificador único ("flat"):

```
C1 célula × não-célula → C2 com × sem lesão → C3 baixo × alto grau → C4 ASC-US × LSIL
                                                                   → C5 ASC-H × HSIL × SCC
```

## Como rodar (pipeline novo)

```powershell
.\.venv\Scripts\Activate.ps1

python scripts\build_cache.py          # 1. extrai patches das imagens (≈1 min, uma vez)
python scripts\make_splits.py          # 2. divide as IMAGENS em teste + 5 folds (uma vez)
python scripts\train.py --task c1 c2 c3 c4 c5 flat7   # 3. treina (5 folds cada)
python scripts\evaluate_hierarchy.py   # 4. hierarquia (hard/soft) × flat7
python scripts\report.py               # 5. tabelas Markdown + LaTeX
```

Experimentos novos: criar `configs/<nome>.yaml` só com o que muda e rodar `python scripts\train.py --task c2 --config configs\<nome>.yaml`. Ajustes rápidos: `--set train.lr=1e-4 model.name=convnext_tiny`. Para testar o código: `--set train.limit=500 train.epochs=1 experiment=teste`.

Resultados vão para `runs/<experimento>/<tarefa>/fold<k>/` (checkpoint, métricas, matriz de confusão, predições).

## Estrutura

```
├── cric/                    # pacote: dados, splits, datasets, modelos, treino, métricas, hierarquia
├── scripts/                 # comandos (build_cache, make_splits, train, evaluate_hierarchy, report)
│   └── preprocessing/       # geradores antigos de recortes (protocolo antigo)
├── configs/                 # default.yaml + um YAML por experimento
├── data/                    # imagens, cache, splits (ver data/README.md)
├── runs/                    # saídas dos experimentos (fora do git)
├── models/                  # pesos antigos usados pela interface (ver models/README.md)
├── notebooks/               # notebooks do protocolo antigo (referência)
├── results/                 # resultados do protocolo antigo
├── app/                     # interface Tkinter + build do .exe
├── legacy/                  # código antigo mantido como referência
└── docs/                    # documentação (+ docs/artigo = dissertação, repo próprio)
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [01_CONTEXTO_PROJETO.md](docs/01_CONTEXTO_PROJETO.md) | objetivo, base, pipeline antigo, modelos |
| [02_RESULTADOS.md](docs/02_RESULTADOS.md) | resultados do protocolo **antigo** (com vazamento) |
| [03_PROBLEMAS_E_PENDENCIAS.md](docs/03_PROBLEMAS_E_PENDENCIAS.md) | bugs e falhas metodológicas |
| [04_ROADMAP_MELHORIAS.md](docs/04_ROADMAP_MELHORIAS.md) | lista de ideias de evolução |
| [05_SETUP.md](docs/05_SETUP.md) | instalação do ambiente |
| [06_ANALISE_DISSERTACAO.md](docs/06_ANALISE_DISSERTACAO.md) | texto da dissertação × código |
| [07_PLANO_DE_ACAO.md](docs/07_PLANO_DE_ACAO.md) | **sprints até dezembro** |
| [08_DIARIO_EXPERIMENTOS.md](docs/08_DIARIO_EXPERIMENTOS.md) | registro de cada experimento |

## Interface

```powershell
python app\interface_hierarquica.py    # usa models/classificador{1,2,3}.pth
python app\build.py                    # gera app\dist\Classificador_Hierarquico_Celulas.exe
```

Cores: **amarelo** = baixo grau, **vermelho** = alto grau (células sem lesão são contadas, mas não desenhadas).

## Base de dados

CRIC Cervix: http://database.cric.com.br. Citação: Rezende, M. T. et al. *Cric searchable image database as a public platform for conventional pap smear cytology data.* Scientific Data, 8, 151 (2021). *(conferir antes de usar no texto)*

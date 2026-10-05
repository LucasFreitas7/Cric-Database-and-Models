# Classificador Hierárquico de Células Cervicais (CRIC)

Dissertação de mestrado (UFOP) — classificação de células de Papanicolau segundo o Sistema Bethesda, na base **CRIC Cervix** (400 imagens, 11.534 células), usando uma cascata de CNNs:

```
célula × não-célula → com × sem lesão → baixo × alto grau → (ASC-US × LSIL | ASC-H × HSIL × SCC)
```

## Estrutura

```
├── app/                     # interface Tkinter + build do .exe (PyInstaller)
├── data/                    # imagens CRIC e recortes (não versionados) — ver data/README.md
├── docs/                    # documentação do projeto (+ docs/artigo = dissertação, repo próprio)
├── legacy/                  # código antigo / restos mantidos como referência
├── models/                  # pesos .pth (não versionados) — ver models/README.md
├── notebooks/               # treino e validação de cada classificador
├── results/                 # métricas e matrizes de confusão por classificador
├── scripts/preprocessing/   # geração de recortes e aumento de dados
└── requirements.txt
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [01_CONTEXTO_PROJETO.md](docs/01_CONTEXTO_PROJETO.md) | objetivo, base de dados, pipeline, modelos |
| [02_RESULTADOS.md](docs/02_RESULTADOS.md) | todas as métricas obtidas até agora |
| [03_PROBLEMAS_E_PENDENCIAS.md](docs/03_PROBLEMAS_E_PENDENCIAS.md) | bugs e falhas metodológicas conhecidas |
| [04_ROADMAP_MELHORIAS.md](docs/04_ROADMAP_MELHORIAS.md) | próximos passos e evoluções |
| [05_SETUP.md](docs/05_SETUP.md) | instalação do ambiente (Python 3.12 + PyTorch CUDA) |
| [06_ANALISE_DISSERTACAO.md](docs/06_ANALISE_DISSERTACAO.md) | estado do texto da dissertação × código |

## Início rápido

```powershell
.\.venv\Scripts\Activate.ps1
python app\interface_hierarquica.py          # interface
python scripts\preprocessing\gerar_recortes_c2_lesao.py   # exemplo de gerador
```

Notebooks: abrir em `notebooks/` com o kernel **"Python (CRIC)"** (os caminhos são relativos a essa pasta).

> ⚠️ A interface atual tem os rótulos dos classificadores 2 e 3 invertidos — ver [docs/03_PROBLEMAS_E_PENDENCIAS.md](docs/03_PROBLEMAS_E_PENDENCIAS.md) (A1–A3).

## Gerar o executável

```powershell
python app\build.py   # saída em app\dist\Classificador_Hierarquico_Celulas.exe
```

## Base de dados

CRIC Cervix — http://database.cric.com.br. Citação: Rezende, M. T. et al. *Cric searchable image database as a public platform for conventional pap smear cytology data.* Scientific Data, 8, 151 (2021). *(conferir antes de usar no texto)*

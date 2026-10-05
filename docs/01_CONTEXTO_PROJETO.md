# 01 — Contexto do Projeto

> Documento de "estado da arte" do repositório, levantado em **05/10/2026** a partir do código, notebooks e artefatos existentes (último trabalho: **ago/2025**).

## 1. Objetivo

Classificar automaticamente células de exames de Papanicolau (citologia cervical convencional) segundo o **Sistema Bethesda**, usando a base pública **CRIC Cervix**, com uma abordagem **hierárquica** de redes convolucionais:

```
recorte 70×70
   │
   ▼
[C1] célula × não-célula ──► não-célula: descarta
   │ célula
   ▼
[C2] com lesão × sem lesão ──► sem lesão (NILM): verde
   │ com lesão
   ▼
[C3] baixo grau × alto grau
   ├── baixo grau ──► [C4] ASC-US × LSIL       (treinado, não integrado)
   └── alto grau  ──► [C5] ASC-H × HSIL × SCC  (treinado, não integrado)
```

Em paralelo existe um **baseline "flat"** (ConvNeXt-Tiny, 7 classes de uma vez) para comparar com a hierarquia.

A aplicação final é uma interface desktop (Tkinter → `.exe` via PyInstaller) que varre uma imagem inteira em janelas 70×70 e pinta as células por grau de lesão.

## 2. Base de dados — CRIC Cervix (classificação)

| Item | Valor |
|---|---|
| Imagens | 400 (PNG, ~1376×1020, RGB) |
| Células anotadas | 11.534 (ponto no centro do núcleo `nucleus_x`, `nucleus_y`) |
| Fonte | http://database.cric.com.br — cada imagem tem DOI (figshare) |
| Anotação | por imagem: `image_id`, `image_name`, `image_doi`, lista `classifications` |

Distribuição real das classes (do `data/classifications.json`):

| Classe Bethesda | Nº células | % |
|---|---:|---:|
| NILM (Negative for intraepithelial lesion) | 6.779 | 58,8% |
| HSIL | 1.703 | 14,8% |
| LSIL | 1.360 | 11,8% |
| ASC-H | 925 | 8,0% |
| ASC-US | 606 | 5,3% |
| SCC | 161 | 1,4% |

Agrupamentos usados:
- **Baixo grau** = ASC-US + LSIL (1.966)
- **Alto grau** = ASC-H + HSIL + SCC (2.789)
- **Com lesão** = tudo exceto NILM (4.755)

## 3. Estrutura de pastas (reorganizada em 05/10/2026)

```
C:\CRIC Projeto\
├── base.zip                  # backup das 400 imagens (~850 MB)
└── celula_classifier\celula_classifier\      ← raiz do projeto (git)
    ├── app/
    │   ├── interface_hierarquica.py          # interface atual (ex-interface_classificador_hierarquico_interface.py)
    │   ├── build.py, celula_classifier.spec  # build do .exe
    │   └── dist/                             # .exe gerado (ignorado no git)
    ├── data/
    │   ├── raw/images/                       # 400 imagens (ex-src/base)
    │   ├── raw/classifications.{json,csv}, README_CRIC.md
    │   └── crops/{c1..c5, flat_7_classes}/   # recortes 70×70 (ex-src/recortes_*)
    ├── models/classificador{1,2,3}.pth
    ├── notebooks/{c1..c5, flat}_*.ipynb      # ex-src/classificador*.ipynb
    ├── scripts/preprocessing/                # ex-src/gerador*.py
    ├── results/{c1..c5, flat_convnext, interface}/
    ├── legacy/                               # interface antiga + .pyc do gerador C1 perdido
    ├── docs/                                 # esta documentação
    │   └── artigo/                           # dissertação LaTeX (repo GitHub sincronizado com o Overleaf)
    └── .venv/                                # Python 3.12 + PyTorch CUDA
```

Mapeamento de nomes antigos → novos:

| Antigo (`src/…`) | Novo |
|---|---|
| `recortes_balanceado` | `data/crops/c1_celula_vs_nao_celula` |
| `recortes_lesao` | `data/crops/c2_lesao` |
| `recortes_alto_baixo` | `data/crops/c3_alto_vs_baixo` |
| `recortes_baixo` | `data/crops/c4_baixo_grau` |
| `recortes_alto` | `data/crops/c5_alto_grau` |
| `recortes_7_classes` | `data/crops/flat_7_classes` |
| `gerador-recortes-lesao.py` / `gerador-alto-medio.py` / `gerador-baixo.py` / `gerador-alto.py` | `scripts/preprocessing/gerar_recortes_{c2_lesao,c3_alto_baixo,c4_baixo_grau,c5_alto_grau}.py` |
| `gerador_ascus.py` / `gerador_scc.py` | `scripts/preprocessing/aumentar_{ascus,scc}.py` |
| `notebooks/c1_celula_vs_nao_celula.ipynb` … `notebooks/flat_convnext_tiny_7_classes.ipynb` | `notebooks/c1_celula_vs_nao_celula.ipynb` … `notebooks/flat_convnext_tiny_7_classes.ipynb` |

## 4. Pipeline de dados (como os recortes foram gerados)

Todos os recortes têm **70×70 px** centrados no núcleo anotado (`left = max(x-35, 0)`).

| Script | Saída | Conteúdo |
|---|---|---|
| *(perdido: `main.py` + `preprocessor.py` + `config.py`)* | `recortes/celula`, `recortes/nao_celula` → `recortes_balanceado` | Grade 70×70 sobre a imagem; recorte = "célula" se há núcleo a até `TOLERANCE` px do centro, senão "não célula". Balanceado em 9.000 × 9.000. Nomes `<imagem>_<x>_<y>.png`. |
| `gerador-recortes-lesao.py` | `recortes_lesao/{com_lesao,sem_lesao}` | 4.755 × 6.779 |
| `gerador-alto-medio.py` | `recortes_alto_baixo/{alto_grau,baixo_grau}` | 2.789 × 1.966 |
| `gerador-baixo.py` | `recortes_baixo/{ASCUS,LSIL}` | 606→**1.350** × 1.360 |
| `gerador-alto.py` | `recortes_alto/{ASCH,HSIL,SCC}` | 925 × 1.703 × 161→**1.000** |
| `gerador_ascus.py` / `gerador_scc.py` | mesmas pastas | **aumento offline**: +744 ASC-US e +839 SCC sintéticos (`aug_scc_*.png`) |
| *(manual)* | `recortes_7_classes/` | junção: ASCH, ASCUS(aug), HSIL, LSIL, SCC(aug), nao_celula(9.000), sem_lesao — 22.117 |

## 5. Classificadores treinados

Todos: entrada 70×70, Adam lr=3e-4, batch 32, pesos ImageNet.

| # | Notebook | Tarefa | Modelo | Validação | Épocas | Salvo? |
|---|---|---|---|---|---|---|
| C1 | `notebooks/c1_celula_vs_nao_celula.ipynb` | célula × não-célula | EfficientNet-B0 (1 logit, BCE) | hold-out 70/30 | 10 | `models/classificador1.pth` |
| C2 | `notebooks/c2_lesao_vs_sem_lesao.ipynb` | com × sem lesão | EfficientNet-B0 (BCE) | KFold 3 | 3 | `models/classificador2.pth` (último fold) |
| C3 | `notebooks/c3_baixo_vs_alto_grau.ipynb` | baixo × alto grau | EfficientNet-B0 (BCE) | StratifiedKFold 3 | 10 | `models/classificador3.pth` (último fold) |
| C4 | `notebooks/c4_ascus_vs_lsil.ipynb` | ASC-US × LSIL | EfficientNet-B0 (2 saídas, CE) | KFold 3 | 10 (código diz 30) | não |
| C5 | `notebooks/c5_asch_hsil_scc.ipynb` | ASC-H × HSIL × SCC | EfficientNet-B0 (3 saídas, CE) | KFold 3 | 3 | não |
| Flat | `notebooks/flat_convnext_tiny_7_classes.ipynb` | 7 classes | ConvNeXt-Tiny (timm) | StratifiedKFold 3 | 20 | não |

Resultados detalhados: [02_RESULTADOS.md](02_RESULTADOS.md).

## 6. Aplicação (interface)

`app/interface_hierarquica.py`:
1. Redimensiona a imagem para 1400×1040.
2. Varre em 3 grades 70×70 (normal, deslocada +23 px, deslocada −23 px).
3. Para cada janela roda C1 → C2 → C3 e acumula "votos" na célula de grade mais próxima.
4. Basta **1 voto** para marcar célula/lesão/alto grau; desenha retângulo vermelho (alto) ou amarelo (baixo). Sem lesão não é desenhado.
5. Mostra contagens na tela.

⚠️ A interface tem bugs sérios de rótulo — ver [03_PROBLEMAS_E_PENDENCIAS.md](03_PROBLEMAS_E_PENDENCIAS.md).

## 7. Ambiente

Ver [05_SETUP.md](05_SETUP.md).

## 8. Documentos

- [01_CONTEXTO_PROJETO.md](01_CONTEXTO_PROJETO.md) — este arquivo
- [02_RESULTADOS.md](02_RESULTADOS.md) — todas as métricas existentes
- [03_PROBLEMAS_E_PENDENCIAS.md](03_PROBLEMAS_E_PENDENCIAS.md) — bugs, falhas metodológicas, coisas faltando
- [04_ROADMAP_MELHORIAS.md](04_ROADMAP_MELHORIAS.md) — próximos passos e evoluções
- [05_SETUP.md](05_SETUP.md) — como montar o ambiente e rodar

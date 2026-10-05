# Dados

```
data/
├── raw/
│   ├── images/                 # 400 imagens CRIC Cervix (NÃO versionado — ~850 MB)
│   ├── classifications.json    # anotações (ponto do núcleo + classe Bethesda)
│   ├── classifications.csv     # mesmas anotações em CSV
│   └── README_CRIC.md          # descrição oficial dos campos
└── crops/                      # recortes 70×70 gerados (NÃO versionado)
    ├── c1_celula_vs_nao_celula/   celula, nao_celula (9.000 cada)
    ├── c2_lesao/                  com_lesao, sem_lesao
    ├── c3_alto_vs_baixo/          alto_grau, baixo_grau
    ├── c4_baixo_grau/             ASCUS (+744 aumentadas), LSIL
    ├── c5_alto_grau/              ASCH, HSIL, SCC (+839 aumentadas)
    └── flat_7_classes/            as 7 classes juntas
```

## Como obter

- **Imagens**: baixar em http://database.cric.com.br (coleção *Cervix — classification*) ou descompactar o backup `C:\CRIC Projeto\base.zip` em `data/raw/images/`.
- **Recortes**: rodar os scripts em `scripts/preprocessing/` (o gerador do C1 está perdido — ver `docs/03_PROBLEMAS_E_PENDENCIAS.md`, item C1).

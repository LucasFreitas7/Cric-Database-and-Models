# Dados

```
data/
├── raw/
│   ├── images/                 # 400 imagens CRIC Cervix (NÃO versionado — ~850 MB)
│   ├── classifications.json    # anotações (ponto do núcleo + classe Bethesda)
│   ├── classifications.csv     # mesmas anotações em CSV
│   └── README_CRIC.md          # descrição oficial dos campos
├── cache/                      # pipeline novo (NÃO versionado, recriável)
│   ├── patches_128.npy         # 23.534 patches 128×128 (uint8, ~1,1 GB, lido com mmap)
│   └── index_128.csv           # uma linha por patch: image, x, y, label, kind
├── splits/
│   └── splits_seed42.csv       # imagem -> fold (0..4) ou -1 = teste   ← VERSIONADO
└── crops/                      # protocolo ANTIGO: recortes em pastas (NÃO versionado)
```

## Pipeline novo (`cric/`)

1. `python scripts/build_cache.py` — para cada uma das 400 imagens:
   - extrai um patch 128×128 centrado em **cada núcleo anotado** (11.534 células reais, sem cópias);
   - sorteia **30 pontos de fundo** sem núcleo anotado num raio de 50 px (12.000 "não célula"); metade precisa ter conteúdo (desvio-padrão de cinza ≥ 12) — bordas de citoplasma, leucócitos, debris;
   - bordas da imagem são preenchidas por reflexão, então todo núcleo fica no centro do patch.
2. `python scripts/make_splits.py` — divisão **por imagem** (StratifiedGroupKFold): 81 imagens de teste + 5 folds de 62–65 imagens. Nenhuma imagem aparece em mais de uma parte.
3. O `PatchDataset` recorta 70×70 do patch na hora; no C1 o centro é deslocado até 25 px (núcleo sempre a ≥ 10 px da borda = **regra da fronteira** da dissertação), o que substitui o gerador perdido de células "descentralizadas".

| Classe | Patches | Teste | Por fold (≈) |
|---|---:|---:|---:|
| não célula | 12.000 | 2.430 | 1.900 |
| NILM | 6.779 | 1.363 | 1.080 |
| HSIL | 1.703 | 337 | 270 |
| LSIL | 1.360 | 271 | 218 |
| ASC-H | 925 | 186 | 148 |
| ASC-US | 606 | 121 | 97 |
| SCC | 161 | 31 | 26 |

## Protocolo antigo (`crops/`, só referência)

Recortes 70×70 gerados pelos scripts de `scripts/preprocessing/`, com cópias aumentadas de SCC/ASC-US gravadas antes da divisão — ver `docs/03_PROBLEMAS_E_PENDENCIAS.md` (B1, B2).

## Como obter as imagens

Baixar em http://database.cric.com.br (coleção *Cervix — classification*) ou descompactar `C:\CRIC Projeto\base.zip` em `data/raw/images/`.

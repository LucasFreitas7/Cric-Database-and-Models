# Modelos treinados

Pesos não são versionados no git (`*.pth`, ~16 MB cada).

| Arquivo | Classificador | Arquitetura | Saída (logit → sigmoid) |
|---|---|---|---|
| `classificador1.pth` | C1 célula × não-célula | EfficientNet-B0, 1 saída | alto = **não célula** |
| `classificador2.pth` | C2 com × sem lesão | EfficientNet-B0, 1 saída | alto = **sem lesão** |
| `classificador3.pth` | C3 baixo × alto grau | EfficientNet-B0, 1 saída | alto = **baixo grau** |

Entrada: recorte RGB 70×70, normalização ImageNet. C4 e C5 não foram salvos.
Backup recomendado: Google Drive, ou *Release* do GitHub / Git LFS.

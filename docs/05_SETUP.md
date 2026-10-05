# 05 — Setup do ambiente

## Máquina atual (05/10/2026)

| Item | Situação |
|---|---|
| SO | Windows 11 Home |
| GPU | NVIDIA GeForce RTX 4060 (8 GB), driver 610.74 (CUDA 13.x) — **não precisa instalar CUDA Toolkit**, o PyTorch traz o runtime |
| Git | 2.55 (já instalado) |
| Python | 3.12.10 (instalado via `winget`, escopo do usuário) |
| Ambiente | `.venv/` na raiz do projeto (`celula_classifier\celula_classifier\.venv`) |
| PyTorch | build **CUDA 12.8** (`--index-url https://download.pytorch.org/whl/cu128`) |
| Kernel Jupyter | "Python (CRIC)" |

## Recriar do zero

```powershell
winget install --id Python.Python.3.12 -e --scope user
cd "C:\CRIC Projeto\celula_classifier\celula_classifier"
py -3.12 -m venv .venv            # ou: & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name cric --display-name "Python (CRIC)"
```

Verificar GPU:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Rodar

- **Notebooks**: abrir no VS Code (extensão Jupyter) e escolher o kernel "Python (CRIC)". Os caminhos são relativos à pasta `notebooks/` (o VS Code já usa a pasta do notebook como diretório de trabalho).
- **Interface**: `.\.venv\Scripts\python.exe app\interface_hierarquica.py`
  (atenção aos bugs de rótulo listados em [03_PROBLEMAS_E_PENDENCIAS.md](03_PROBLEMAS_E_PENDENCIAS.md)).
- **Geradores de recortes**: `.\.venv\Scripts\python.exe scripts\preprocessing\<script>.py` (funcionam de qualquer diretório).
- **Executável**: `.\.venv\Scripts\python.exe app\build.py`.

## Observações

- As pastas antigas `src/` (só sobrou o venv quebrado `src/env/` + 3 PNG duplicados) e `build/` podem ser apagadas manualmente; estão no `.gitignore`.
- `base.zip` (850 MB) na pasta `C:\CRIC Projeto` é o backup das 400 imagens; já está descompactado em `data/raw/images/`.

import os
import json
from PIL import Image
from tqdm import tqdm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # raiz do projeto

# === CONFIGURAÇÕES ===
CROP_SIZE = 70
JSON_PATH = ROOT / "data" / "raw" / "classifications.json"  # Caminho para o JSON
IMAGE_DIR = ROOT / "data" / "raw" / "images"                  # Pasta onde estão as imagens
OUTPUT_DIR = ROOT / "data" / "crops" / "c2_lesao"      # Pasta onde serão salvos os recortes

# Subpastas
COM_LESAO = os.path.join(OUTPUT_DIR, "com_lesao")
SEM_LESAO = os.path.join(OUTPUT_DIR, "sem_lesao")
os.makedirs(COM_LESAO, exist_ok=True)
os.makedirs(SEM_LESAO, exist_ok=True)

# === FUNÇÕES ===
def is_sem_lesao(rotulo):
    return rotulo.strip().lower() == "negative for intraepithelial lesion"

# === EXECUÇÃO ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    dados = json.load(f)

total_lesao = 0
total_sem_lesao = 0

for item in tqdm(dados, desc="Processando imagens"):
    nome_img = item["image_name"]
    path_img = os.path.join(IMAGE_DIR, nome_img)

    if not os.path.exists(path_img):
        print(f"Imagem não encontrada: {path_img}")
        continue

    try:
        imagem = Image.open(path_img).convert("RGB")
    except Exception as e:
        print(f"Erro ao abrir imagem: {nome_img} - {e}")
        continue

    for idx, celula in enumerate(item["classifications"]):
        x, y = celula["nucleus_x"], celula["nucleus_y"]
        rotulo = celula["bethesda_system"]

        left = max(x - CROP_SIZE // 2, 0)
        upper = max(y - CROP_SIZE // 2, 0)
        right = left + CROP_SIZE
        lower = upper + CROP_SIZE

        crop = imagem.crop((left, upper, right, lower))
        nome_crop = f"{os.path.splitext(nome_img)[0]}_{idx}.png"

        if is_sem_lesao(rotulo):
            crop.save(os.path.join(SEM_LESAO, nome_crop))
            total_sem_lesao += 1
        else:
            crop.save(os.path.join(COM_LESAO, nome_crop))
            total_lesao += 1

print("\n=== RESUMO ===")
print(f"Recortes com lesão    : {total_lesao}")
print(f"Recortes sem lesão    : {total_sem_lesao}")
print(f"Total de imagens lidas: {len(dados)}")

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
OUTPUT_DIR = ROOT / "data" / "crops" / "c3_alto_vs_baixo"      # Pasta onde serão salvos os recortes

# Subpastas
ALTO_GRAU = os.path.join(OUTPUT_DIR, "alto_grau")
BAIXO_GRAU = os.path.join(OUTPUT_DIR, "baixo_grau")
os.makedirs(ALTO_GRAU, exist_ok=True)
os.makedirs(BAIXO_GRAU, exist_ok=True)

# === FUNÇÕES ===
def is_baixo_grau(rotulo):
    print("baixo grau  = ", rotulo == "LSIL" or "ASC-US")
    return rotulo == "LSIL" or  rotulo == "ASC-US"

def is_alto_grau(rotulo):
    print("alto gru  = ", rotulo == "SCC" or "ASC-H" or "HSIL")
    return rotulo == "SCC" or  rotulo == "ASC-H" or rotulo == "HSIL"

# === EXECUÇÃO ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    dados = json.load(f)

total_alto_grau = 0
total_baixo_grau = 0

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

        print("Rotulo = ", rotulo)

        if is_baixo_grau(rotulo):
            crop.save(os.path.join(BAIXO_GRAU, nome_crop))
            total_baixo_grau += 1
        elif is_alto_grau(rotulo):
            crop.save(os.path.join(ALTO_GRAU, nome_crop))
            total_alto_grau += 1

print("\n=== RESUMO ===")
print(f"Recortes de alta lesao    : {total_alto_grau}")
print(f"Recortes de baixa lesao    : {total_baixo_grau}")
print(f"Total de imagens lidas: {len(dados)}")

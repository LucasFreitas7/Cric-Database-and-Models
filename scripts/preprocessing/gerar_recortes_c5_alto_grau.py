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
OUTPUT_DIR = ROOT / "data" / "crops" / "c5_alto_grau"      # Pasta onde serão salvos os recortes

# Subpastas
HSIL = os.path.join(OUTPUT_DIR, "HSIL")
ASCH = os.path.join(OUTPUT_DIR, "ASCH")
SCC = os.path.join(OUTPUT_DIR, "SCC")
os.makedirs(HSIL, exist_ok=True)
os.makedirs(ASCH, exist_ok=True)
os.makedirs(SCC, exist_ok=True)
# === FUNÇÕES ===
def is_SCC(rotulo):
    return rotulo == "SCC"

def is_ASCH(rotulo):
    return rotulo == "ASC-H"
def is_HSIL(rotulo):
    return rotulo == "HSIL"

# === EXECUÇÃO ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    dados = json.load(f)

total_scc = 0
total_hsil = 0
total_asch = 0

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


        if is_SCC(rotulo):
            crop.save(os.path.join(SCC, nome_crop))
            total_scc += 1
        elif is_HSIL(rotulo):
            crop.save(os.path.join(HSIL, nome_crop))
            total_hsil += 1
        elif is_ASCH(rotulo):
            crop.save(os.path.join(ASCH, nome_crop))
            total_asch += 1

print("\n=== RESUMO ===")
print(f"Recortes SCC  : {total_scc}")
print(f"Recortes de HSIL   : {total_hsil}")
print(f"Recortes de ASCH   : {total_asch}")
print(f"Total de imagens lidas: {len(dados)}")

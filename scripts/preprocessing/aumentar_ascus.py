import os
from PIL import Image
from torchvision import transforms
import random
from tqdm import tqdm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # raiz do projeto

# Caminho original e de destino
BASE_SCC = ROOT / "data" / "crops" / "c4_baixo_grau" / "ASCUS"
TARGET_COUNT = 1350  # Total desejado de imagens após aumento

# Definição das transformações
augmentations = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(degrees=30),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
    transforms.RandomResizedCrop(size=70, scale=(0.9, 1.0)),
])

# Lista de imagens originais
original_images = [f for f in os.listdir(BASE_SCC) if f.endswith(".png")]
current_count = len(original_images)
new_images_needed = TARGET_COUNT - current_count

print(f"Total atual: {current_count}, aumentará para: {TARGET_COUNT}")

# Loop de aumento de dados
idx = 0
for _ in tqdm(range(new_images_needed), desc="Gerando aumentos para ASCUS"):
    img_name = random.choice(original_images)
    img_path = os.path.join(BASE_SCC, img_name)

    with Image.open(img_path).convert("RGB") as img:
        transformed = augmentations(img)
        save_path = os.path.join(BASE_SCC, f"aug_scc_{idx}.png")
        transformed.save(save_path)
        idx += 1

print("\n✅ Aumento de dados concluído para ASCUS!")

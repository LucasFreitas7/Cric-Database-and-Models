import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image, ImageDraw
from tkinter import Tk, filedialog, messagebox, Label, Button

# Caminhos dos modelos
MODEL_DIR = "models"
CLASSIF_1_PATH = os.path.join(MODEL_DIR, "classificador1.pth")
CLASSIF_2_PATH = os.path.join(MODEL_DIR, "classificador2.pth")
CLASSIF_3_PATH = os.path.join(MODEL_DIR, "classificador3.pth")

# Configurações
CROP_SIZE = 70
RESIZED_SIZE = (1400, 1040)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Transformação
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def load_model(path):
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 1)
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

# Carregando os 3 classificadores
model1 = load_model(CLASSIF_1_PATH)
model2 = load_model(CLASSIF_2_PATH)
model3 = load_model(CLASSIF_3_PATH)

def process_image(image_path, output_path="resultado_hierarquico.png"):
    image = Image.open(image_path).convert("RGB").resize(RESIZED_SIZE)
    draw = ImageDraw.Draw(image)

    width, height = image.size
    counts = {
        "total_celulas": 0,
        "sem_lesao": 0,
        "baixo_grau": 0,
        "alto_grau": 0
    }

    for y in range(0, height - CROP_SIZE + 1, CROP_SIZE):
        for x in range(0, width - CROP_SIZE + 1, CROP_SIZE):
            crop = image.crop((x, y, x + CROP_SIZE, y + CROP_SIZE))
            input_tensor = transform(crop).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                is_cell = model1(input_tensor).item() < 0.5

            if not is_cell:
                continue

            counts["total_celulas"] += 1

            with torch.no_grad():
                has_lesion = model2(input_tensor).item() > 0.5

            if not has_lesion:
                counts["sem_lesao"] += 1
                draw.rectangle([x, y, x + CROP_SIZE, y + CROP_SIZE], outline="green", width=2)
                continue

            with torch.no_grad():
                is_high_grade = model3(input_tensor).item() > 0.5

            if is_high_grade:
                counts["alto_grau"] += 1
                draw.rectangle([x, y, x + CROP_SIZE, y + CROP_SIZE], outline="red", width=2)
            else:
                counts["baixo_grau"] += 1
                draw.rectangle([x, y, x + CROP_SIZE, y + CROP_SIZE], outline="yellow", width=2)

    image.save(output_path)
    return counts, output_path

# Interface Gráfica com Tkinter
def run_gui():
    def selecionar_imagem():
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if not file_path:
            return
        try:
            contadores, saida = process_image(file_path)
            messagebox.showinfo("Processamento Finalizado",
                f"Imagem salva: {saida}\n\n"
                f"Total de células: {contadores['total_celulas']}\n"
                f"Sem lesão: {contadores['sem_lesao']}\n"
                f"Lesão de baixo grau: {contadores['baixo_grau']}\n"
                f"Lesão de alto grau: {contadores['alto_grau']}"
            )
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    root = Tk()
    root.title("Classificador Hierárquico - Lesões Cervicais")

    Label(root, text="Selecione uma imagem para classificar as células:").pack(pady=10)
    Button(root, text="Selecionar Imagem", command=selecionar_imagem).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    run_gui()

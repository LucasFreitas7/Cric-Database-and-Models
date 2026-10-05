
import os
import sys
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Button, Label, Progressbar
from collections import Counter

# === CONFIGURAÇÕES ===
CROP_SIZE = 70
TARGET_WIDTH = 1400
TARGET_HEIGHT = 1040
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === TRANSFORMAÇÃO ===
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])
contagem = Counter()
# === FUNÇÕES ===
def load_model(path):
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 1)
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

def process_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((TARGET_WIDTH, TARGET_HEIGHT))
    draw = ImageDraw.Draw(image)
    
    # Criando um grid para armazenar votos de classificação
    grid_votes = {}  # Dicionário (x,y) -> {'celula': bool, 'lesao': int, 'alto_grau': int}
    
    # Função para processar um recorte em uma posição específica e registrar votos
    def process_crop(x, y, vote=True):
        # Normaliza as coordenadas para o grid original para votação
        # Isso garante que votos de posições deslocadas sejam agregados à posição do grid original mais próxima
        grid_x = round(x / CROP_SIZE) * CROP_SIZE
        grid_y = round(y / CROP_SIZE) * CROP_SIZE
        grid_key = (grid_x, grid_y)
        
        if grid_key not in grid_votes:
            grid_votes[grid_key] = {'celula': 0, 'lesao': 0, 'alto_grau': 0, 'total_votes': 0}
            
        crop = image.crop((x, y, x + CROP_SIZE, y + CROP_SIZE))
        input_tensor = transform(crop).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            is_cell = model1(input_tensor).item() < 0.5
            
        if not is_cell:
            return False, None
        
        if vote:
            grid_votes[grid_key]['celula'] += 1
            grid_votes[grid_key]['total_votes'] += 1
        
        with torch.no_grad():
            # Ajuste no limiar para detectar mais lesões
            has_lesion = model2(input_tensor).item() > 0.45  # Limiar reduzido para detectar mais lesões
        
        if vote:
            # Sempre registra o voto, independentemente do resultado
            if has_lesion:
                grid_votes[grid_key]['lesao'] += 1
        
        with torch.no_grad():
            is_high_grade = model3(input_tensor).item() > 0.5
            
        if vote and has_lesion:
            if is_high_grade:
                grid_votes[grid_key]['alto_grau'] += 1
        
        # Não desenhamos mais a caixa aqui, apenas retornamos as informações
        return True, {'is_cell': True, 'has_lesion': has_lesion, 'is_high_grade': is_high_grade}
    
    # Primeiro scanner - grade regular
    print("Iniciando primeiro scanner (grade regular)...")
    for y in range(0, TARGET_HEIGHT - CROP_SIZE + 1, CROP_SIZE):
        for x in range(0, TARGET_WIDTH - CROP_SIZE + 1, CROP_SIZE):
            process_crop(x, y)
    
    # Segundo scanner - grade deslocada para direita
    offset_right = CROP_SIZE // 3
    print("Iniciando segundo scanner (grade deslocada à direita)...")
    for y in range(0, TARGET_HEIGHT - CROP_SIZE + 1, CROP_SIZE):
        for x in range(offset_right, TARGET_WIDTH - CROP_SIZE + 1, CROP_SIZE):
            process_crop(x, y)
    
    # Terceiro scanner - grade deslocada para esquerda
    offset_left = -CROP_SIZE // 3
    print("Iniciando terceiro scanner (grade deslocada à esquerda)...")
    for y in range(0, TARGET_HEIGHT - CROP_SIZE + 1, CROP_SIZE):
        for x in range(offset_left, TARGET_WIDTH - CROP_SIZE + 1, CROP_SIZE):
            if x >= 0:  # Evitar coordenadas negativas
                process_crop(x, y)
    
    # Processar as votações e desenhar os retângulos finais
    print("Processando votações e desenhando resultados...")
    for (x, y), votes in grid_votes.items():
        # Debug para verificar os votos
        print(f"Posição ({x},{y}): {votes}")
        
        # Só conta como célula se teve pelo menos 1 voto
        if votes['celula'] >= 1:
            contagem["celula"] += 1
            
            # Verifica se é lesão (pelo menos 1 voto para lesão)
            if votes['lesao'] >= 1:
                # Verifica se é alto grau (pelo menos 1 voto para alto grau)
                is_high_grade = votes['alto_grau'] >= 1
                
                color = "red" if is_high_grade else "yellow"
                # Desenha a caixa na posição do grid original, garantindo que não haja sobreposição
                draw.rectangle([x, y, x + CROP_SIZE, y + CROP_SIZE], outline=color, width=2)
                contagem["alto_grau" if is_high_grade else "baixo_grau"] += 1
            else:
                # Célula sem lesão - não pintar
                contagem["sem_lesao"] += 1
    
    output_path = "resultado_hierarquico.png"
    image.save(output_path)
    return output_path, contagem

def processar_com_loading(caminho):
    """Função para processar a imagem em uma thread separada com loading"""
    global contagem
    contagem = Counter()  # Reinicia o contador para cada nova imagem
    
    # Cria janela de loading
    loading_window = tk.Toplevel(root)
    loading_window.title("Processando")
    loading_window.geometry("300x100")
    loading_window.transient(root)  # Define como janela filha da principal
    loading_window.grab_set()  # Foca na janela de loading
    
    # Centraliza a janela
    loading_window.update_idletasks()
    width = loading_window.winfo_width()
    height = loading_window.winfo_height()
    x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
    y = (loading_window.winfo_screenheight() // 2) - (height // 2)
    loading_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Adiciona mensagem e barra de progresso
    tk.Label(loading_window, text="Processando imagem, por favor aguarde...").pack(pady=10)
    
    # Barra de progresso indeterminada
    progress = tk.ttk.Progressbar(loading_window, mode="indeterminate")
    progress.pack(fill=tk.X, padx=20)
    progress.start(10)
    
    # Atualiza a interface
    loading_window.update()
    
    try:
        # Processa a imagem
        resultado_path, contagem = process_image(caminho)
        loading_window.destroy()  # Fecha a janela de loading
        
        # Exibe resultados
        msg = f"""
[OK] Imagem processada com sucesso!"""
        messagebox.showinfo("Resultado", msg)
        img = Image.open(resultado_path)
        img.thumbnail((700, 500))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk
        
        # Atualiza os contadores após o processamento
        contador_info.config(text=f"Células encontradas: {contagem['celula']}\n"
                               f"Sem lesão: {contagem['sem_lesao']}\n"
                               f"Baixo grau: {contagem['baixo_grau']}\n"
                               f"Alto grau: {contagem['alto_grau']}")
    except Exception as e:
        loading_window.destroy()  # Fecha a janela de loading em caso de erro
        messagebox.showerror("Erro", str(e))

def escolher_imagem():
    caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
    if not caminho:
        return
    
    # Inicia o processamento com loading
    root.after(100, lambda: processar_com_loading(caminho))


# === CARREGAR MODELOS ===
# Detecta se está rodando como executável ou como script Python
if getattr(sys, 'frozen', False):
    # Se for executável empacotado pelo PyInstaller
    application_path = os.path.dirname(sys.executable)
    MODEL_DIR = os.path.join(application_path, "models")
else:
    # Se for script Python normal: modelos ficam em <raiz do projeto>/models
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

print(f"Carregando modelos de: {MODEL_DIR}")
try:
    model1 = load_model(os.path.join(MODEL_DIR, "classificador1.pth"))
    model2 = load_model(os.path.join(MODEL_DIR, "classificador2.pth"))
    model3 = load_model(os.path.join(MODEL_DIR, "classificador3.pth"))
except Exception as e:
    messagebox.showerror("Erro ao carregar modelos", f"Não foi possível carregar os modelos: {str(e)}\nPasta de modelos: {MODEL_DIR}")

# === INTERFACE TKINTER ===
root = tk.Tk()
root.title("Classificador Hierárquico de Células")
# Maximiza a janela ao iniciar (modo tela cheia em Windows)
root.state('zoomed')

Label(root, text="Selecione uma imagem para classificar.").pack(pady=10)
Label(root, text="Dimensão recomendada próxima de 1400x1050 (múltiplos de 70).", foreground="gray").pack()

Button(root, text="Escolher imagem", command=escolher_imagem).pack(pady=20)

image_label = Label(root)
image_label.pack()

# Criar uma label para exibir contadores que será atualizada após o processamento
contador_info = Label(root, text="")
contador_info.pack(pady=10)

root.mainloop()

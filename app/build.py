# build.py - Script para construir o executável
import os
import subprocess
import shutil

print("Iniciando a construção do executável...")

# Garante que dist/ e build/ fiquem dentro de app/, de onde quer que o script seja chamado
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Limpa a pasta dist se já existir
if os.path.exists("dist"):
    print("Limpando pasta dist anterior...")
    shutil.rmtree("dist")

# Constrói o executável usando o arquivo spec
print("Executando PyInstaller...")
result = subprocess.run([
    'pyinstaller',
    'celula_classifier.spec',
    '--clean'
], capture_output=True, text=True)

print("Saída do PyInstaller:")
print(result.stdout)

if result.returncode != 0:
    print("Erro ao construir o executável:")
    print(result.stderr)
else:
    print("Executável criado com sucesso na pasta 'dist'!")

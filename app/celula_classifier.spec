# -*- mode: python ; coding: utf-8 -*-
# Rodar a partir da pasta app/:  python build.py
import os

ROOT = os.path.dirname(SPECPATH)  # raiz do projeto (SPECPATH = pasta deste .spec)
block_cipher = None

a = Analysis(
    [os.path.join(SPECPATH, 'interface_hierarquica.py')],
    pathex=[SPECPATH],
    binaries=[],
    datas=[
        (os.path.join(ROOT, 'models', 'classificador1.pth'), 'models/'),
        (os.path.join(ROOT, 'models', 'classificador2.pth'), 'models/'),
        (os.path.join(ROOT, 'models', 'classificador3.pth'), 'models/'),
    ],
    hiddenimports=['torch', 'torchvision', 'PIL', 'tkinter'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Classificador_Hierarquico_Celulas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False  # False para esconder a janela do console
)

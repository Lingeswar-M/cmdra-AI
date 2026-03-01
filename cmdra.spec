# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller one-file production spec for cmdraAI."""

import os

icon_file = None
if os.path.exists('cmdra-ai.png'):
    icon_file = 'cmdra-ai.png'
elif os.path.exists('icon.ico'):
    icon_file = 'icon.ico'
elif os.path.exists('icon.png'):
    icon_file = 'icon.png'

datas = [
    ('assets', 'assets'),
]
if os.path.exists('icon.png'):
    datas.append(('icon.png', '.'))
if os.path.exists('cmdra-ai.png'):
    datas.append(('cmdra-ai.png', '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt5',
        'pyautogui',
        'screen_brightness_control',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'tensorflow',
        'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    exclude_binaries=False,
    name='cmdraAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)



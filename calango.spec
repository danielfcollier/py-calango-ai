# calango.spec
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# 1. Collect Streamlit's static assets (frontend files)
datas = []
datas += collect_data_files('streamlit')
datas += copy_metadata('streamlit')
datas += copy_metadata('litellm') 

# 2. Add YOUR source code to the bundle
# (Source Path, Destination Path inside exe)
datas += [('src', 'src')]

block_cipher = None

a = Analysis(
    ['run_executable.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'litellm',
        'tinydb',
        'yaml',
        'plotly',
        'pandas'
    ],
    hookspath=[],
    hooksconfig={},
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
    name='CalangoAI',        # <--- Name of your output file
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,             # Set to False to hide terminal window (Windows/Mac)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/icon.ico' # Optional: Add an icon if you have one
)
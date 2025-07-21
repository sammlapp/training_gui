# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Add the scripts directory to the path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

a = Analysis(
    ['scripts/inference.py'],
    pathex=[str(scripts_dir)],
    binaries=[],
    datas=[
        # Include all Python scripts that might be imported
        ('scripts/*.py', 'scripts'),
        # Include any model files
        ('scripts/*.ckpt', 'scripts'),
    ],
    hiddenimports=[
        # PyTorch hidden imports
        'torch',
        'torchvision',
        'torchaudio',
        # Bioacoustics hidden imports
        'opensoundscape',
        'opensoundscape.ml',
        'opensoundscape.audio',
        'opensoundscape.spectrogram',
        # Audio processing
        'librosa',
        'soundfile',
        'resampy',
        # Scientific computing
        'numpy',
        'pandas',
        'scipy',
        'sklearn',
        'matplotlib',
        'seaborn',
        'plotly',
        'h5py',
        'psutil',
        'tqdm',
        'pydantic',
        'transformers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'email',
        'html',
        'http',
        'urllib',
        'xml',
        'test',
        'tests',
        'testing',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
        'jupyter',
        'notebook',
        'ipython',
        'wandb',
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
    [],
    exclude_binaries=True,
    name='inference',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='inference',
)
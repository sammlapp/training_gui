# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['scripts/http_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('scripts/*.py', 'scripts'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # TensorFlow-related exclusions
        'tensorflow',
        'tensorflow_hub', 
        'tensorflow_io',
        'tf_keras',
        'keras',
        'tensorboard',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='http_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
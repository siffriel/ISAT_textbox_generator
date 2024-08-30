# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ISAT_textbox_gen.py'],
    pathex=[],
    binaries=[],
    datas=[('textbox_translucent.png', '.'), ('VCR_OSD_MONO_1.001.ttf', '.')],
    hiddenimports=['PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ISAT_textbox_gen',
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

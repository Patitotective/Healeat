# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

with open('requirements.txt') as f:
    hiddenimports = f.read().splitlines()

a = Analysis(['main.py'],
             #pathex=[r'C:\Users\crist\Documents\Healeat\Healeat'], # Windows
             pathex=['/home/cristobal/Documents/Projects/Healeat/Healeat'], # Linux
             binaries=[],
             #datas=[('./Images/icon.ico', './Images')], # Windows
             datas=[('./Images/icon.png', './Images')], # Linux   
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='Healeat',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None, 
          #icon='Images/icon.ico' # Windows
          icon='Images/icon.png' # Linux
        )
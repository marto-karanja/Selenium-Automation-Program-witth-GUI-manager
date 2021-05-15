# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Admin\\Documents\\projects\\bots\\shark\\bot'],
             binaries=[('driver\\chromedriver.exe', 'driver\\')],
             datas=[('config.json', '.'), ('setup.ini', '.')],
             hiddenimports=[],
             hookspath=[],
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
          name='shark bot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
import shutil
shutil.copyfile('setup.ini', '{0}/setup.ini'.format(DISTPATH))
shutil.copyfile('config.json', '{0}/config.json'.format(DISTPATH))
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['client_windows.py'],
             pathex=['D:\Projects\Reverse-Shell\ClientSide\client_windows.py'],
             binaries=[],
             datas=[ ("./_portaudio.cp38-win32.pyd","."), ("./_portaudio.cp39-win_amd64.pyd",".") ],
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
          name='client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

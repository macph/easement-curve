# -*- mode: python -*-

block_cipher = None

a = Analysis(['__main__.py'],
             pathex=['.'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
a.datas += [('resources\\logo.ico', 'resources\\logo.ico', 'DATA'),
            ('resources\\logo.png', 'resources\\logo.png', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='eccalc',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='resources/logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ECCalc')

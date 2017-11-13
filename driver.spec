# -*- mode: python -*-
block_cipher = None

import os
import PyInstaller.utils.hooks

DEPENDENCIES = "./dependencies"

a = Analysis(['main.py'],
             pathex=[DEPENDENCIES],
             binaries=None,
             datas=[(os.path.join(DEPENDENCIES, "cloudshell/layer_one/core/response/templates/*.xml"), 'cloudshell/layer_one/core/response/templates'), 
			 (os.path.join(DEPENDENCIES, "cloudshell/layer_one/core/response/resource_info/templates/*.xml"), 'cloudshell/layer_one/core/response/resource_info/templates'), 
			 (os.path.join(DEPENDENCIES, "cloudshell/core/logger/qs_config.ini"), 'cloudshell/core/logger')] + \
             PyInstaller.utils.hooks.collect_data_files('mrv'),
             hiddenimports=PyInstaller.utils.hooks.collect_submodules('cloudshell-cli') + \
             PyInstaller.utils.hooks.collect_submodules('.\sources\paramiko') + [
                "drivername"
             ] + PyInstaller.utils.hooks.collect_submodules('cloudshell'),
             hookspath=[os.path.join(DEPENDENCIES, "cloudshell")],
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MRV_MCC_GENERIC',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          version='version.txt',
          icon="./img/icon.ico")

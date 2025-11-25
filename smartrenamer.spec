# -*- mode: python ; coding: utf-8 -*-
"""
SmartRenamer PyInstaller 配置文件

此文件用于配置 PyInstaller 的打包行为，包括：
- 应用入口点
- 隐藏导入模块
- 数据文件和资源
- 平台特定设置
"""

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目根目录
project_root = Path(SPECPATH)
src_dir = project_root / 'src'
assets_dir = project_root / 'assets'
i18n_dir = project_root / 'i18n'

# 检测平台
IS_WINDOWS = sys.platform.startswith('win')
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

# 应用基本信息
APP_NAME = 'SmartRenamer'
APP_VERSION = '0.9.0'

# 收集数据文件
datas = []

# 添加国际化文件
if i18n_dir.exists():
    for json_file in i18n_dir.glob('*.json'):
        datas.append((str(json_file), 'i18n'))

# 添加主题文件
themes_dir = assets_dir / 'themes'
if themes_dir.exists():
    for qss_file in themes_dir.glob('*.qss'):
        datas.append((str(qss_file), 'assets/themes'))

# 添加图标文件
for icon_file in assets_dir.glob('icon.*'):
    if icon_file.suffix in ['.png', '.ico', '.icns']:
        datas.append((str(icon_file), 'assets'))

# 添加 .desktop 文件（Linux）
desktop_file = assets_dir / 'smartrenamer.desktop'
if desktop_file.exists():
    datas.append((str(desktop_file), 'assets'))

# 收集 PySide6 数据文件
try:
    pyside6_datas = collect_data_files('PySide6', include_py_files=False)
    datas.extend(pyside6_datas)
except Exception as e:
    print(f"警告: 收集 PySide6 数据文件失败: {e}")

# 隐藏导入
hiddenimports = [
    # PySide6 核心模块
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    
    # TMDB API
    'tmdbv3api',
    'tmdbv3api.tmdb',
    'tmdbv3api.as_obj',
    
    # HTTP 客户端
    'requests',
    'requests.adapters',
    'requests.packages',
    'requests.packages.urllib3',
    'urllib3',
    
    # Jinja2 模板引擎
    'jinja2',
    'jinja2.ext',
    
    # 图像处理
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',
    
    # SmartRenamer 子模块
    'smartrenamer',
    'smartrenamer.core',
    'smartrenamer.core.models',
    'smartrenamer.core.config',
    'smartrenamer.core.scanner',
    'smartrenamer.core.library',
    'smartrenamer.core.parser',
    'smartrenamer.core.matcher',
    'smartrenamer.core.renamer',
    'smartrenamer.api',
    'smartrenamer.api.tmdb_client',
    'smartrenamer.api.tmdb_client_enhanced',
    'smartrenamer.ui',
    'smartrenamer.ui.main_window',
    'smartrenamer.ui.theme_manager',
    'smartrenamer.ui.i18n_manager',
    'smartrenamer.storage',
    'smartrenamer.storage.base',
    'smartrenamer.storage.local',
    'smartrenamer.storage.storage_115',
    'smartrenamer.storage.storage_123',
    'smartrenamer.storage.manager',
    'smartrenamer.utils',
    'smartrenamer.utils.file_utils',
]

# 收集所有子模块
try:
    smartrenamer_submodules = collect_submodules('smartrenamer')
    hiddenimports.extend(smartrenamer_submodules)
except Exception as e:
    print(f"警告: 收集 smartrenamer 子模块失败: {e}")

# 排除不需要的模块
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'IPython',
    'jupyter',
    'notebook',
]

# 二进制文件（通常由 PyInstaller 自动处理）
binaries = []

# 分析配置
block_cipher = None

a = Analysis(
    [str(src_dir / 'smartrenamer' / 'main.py')],
    pathex=[str(src_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Windows 平台配置
if IS_WINDOWS:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # GUI 应用不显示控制台
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(assets_dir / 'icon.ico') if (assets_dir / 'icon.ico').exists() else None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=APP_NAME,
    )

# macOS 平台配置
elif IS_MACOS:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
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
        name=APP_NAME,
    )
    
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=str(assets_dir / 'icon.icns') if (assets_dir / 'icon.icns').exists() else None,
        bundle_identifier='com.smartrenamer.app',
        version=APP_VERSION,
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'NSHighResolutionCapable': 'True',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
        },
    )

# Linux 平台配置
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
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
        name=APP_NAME,
    )

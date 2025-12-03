#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartRenamer macOS 构建脚本

自动化构建流程：
1. 检查构建环境（仅支持 macOS）
2. 安装依赖
3. 执行 PyInstaller 打包
4. 创建 DMG 镜像
5. 生成校验和
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path
import argparse

# 仅支持 macOS - 快速失败
if platform.system() != 'Darwin':
    print(f'错误: 此构建脚本仅支持 macOS 平台', file=sys.stderr)
    print(f'当前平台: {platform.system()}', file=sys.stderr)
    print(f'请在 macOS 系统上运行此脚本', file=sys.stderr)
    sys.exit(1)


class Builder:
    """SmartRenamer macOS 构建器"""
    
    def __init__(self, clean=False, debug=False):
        self.platform = 'darwin'  # macOS only
        self.clean = clean
        self.debug = debug
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / 'dist'
        self.build_dir = self.project_root / 'build'
        
    def log(self, message, level='INFO'):
        """打印日志"""
        print(f'[{level}] {message}')
        
    def run_command(self, command, cwd=None):
        """执行命令"""
        self.log(f'执行命令: {" ".join(command)}')
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                self.log(result.stdout)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.log(f'命令执行失败: {e}', 'ERROR')
            if e.stdout:
                self.log(e.stdout, 'ERROR')
            if e.stderr:
                self.log(e.stderr, 'ERROR')
            return False
            
    def check_environment(self):
        """检查构建环境"""
        self.log('检查构建环境...')
        
        # 检查 Python 版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.log('需要 Python 3.8 或更高版本', 'ERROR')
            return False
            
        self.log(f'Python 版本: {sys.version}')
        self.log(f'平台: {self.platform}')
        
        return True
        
    def install_dependencies(self):
        """安装构建依赖"""
        self.log('安装依赖...')
        
        # 安装运行时依赖
        if not self.run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']):
            return False
            
        # 安装构建工具（macOS）
        build_deps = ['pyinstaller']
            
        if not self.run_command([sys.executable, '-m', 'pip', 'install'] + build_deps):
            return False
            
        return True
        
    def clean_build(self):
        """清理构建目录"""
        self.log('清理构建目录...')
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                self.log(f'删除: {dir_path}')
                shutil.rmtree(dir_path)
                
    def generate_icons(self):
        """生成应用图标"""
        self.log('生成应用图标...')
        
        icon_script = self.project_root / 'generate_icons.py'
        
        if not icon_script.exists():
            self.log('图标生成脚本不存在，跳过', 'WARNING')
            return True
            
        # 检查是否已存在有效的图标文件
        assets_dir = self.project_root / 'assets'
        icon_ico = assets_dir / 'icon.ico'
        
        if icon_ico.exists() and icon_ico.stat().st_size > 10000:
            self.log('图标文件已存在且有效，跳过生成')
            return True
            
        # 运行图标生成脚本
        self.log('运行图标生成脚本...')
        return self.run_command([sys.executable, str(icon_script)])
    
    def build_executable(self):
        """构建可执行文件"""
        self.log('构建可执行文件...')
        
        spec_file = self.project_root / 'smartrenamer.spec'
        
        command = [
            sys.executable,
            '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ]
        
        if self.debug:
            command.append('--debug')
            
        return self.run_command(command)
        
    def create_macos_dmg(self):
        """创建 macOS DMG 镜像"""
        self.log('创建 macOS DMG 镜像...')
        
        app_path = self.dist_dir / 'SmartRenamer.app'
        dmg_path = self.dist_dir / 'SmartRenamer-macOS.dmg'
        
        if not app_path.exists():
            self.log(f'应用包不存在: {app_path}', 'ERROR')
            return False
            
        # 创建临时 DMG 目录
        dmg_tmp = self.build_dir / 'dmg_tmp'
        dmg_tmp.mkdir(parents=True, exist_ok=True)
        
        # 复制应用到临时目录
        app_tmp = dmg_tmp / 'SmartRenamer.app'
        if app_tmp.exists():
            shutil.rmtree(app_tmp)
        shutil.copytree(app_path, app_tmp)
        
        # 创建 Applications 符号链接
        apps_link = dmg_tmp / 'Applications'
        if not apps_link.exists():
            apps_link.symlink_to('/Applications')
            
        # 创建 DMG
        command = [
            'hdiutil', 'create',
            '-volname', 'SmartRenamer',
            '-srcfolder', str(dmg_tmp),
            '-ov',
            '-format', 'UDZO',
            str(dmg_path)
        ]
        
        result = self.run_command(command)
        
        # 清理临时目录
        shutil.rmtree(dmg_tmp)
        
        return result
        
    def create_installer(self):
        """创建 macOS DMG 镜像"""
        return self.create_macos_dmg()
            
    def generate_checksums(self):
        """生成 macOS 输出文件的校验和"""
        self.log('生成 macOS 输出文件校验和...')
        
        import hashlib
        
        checksum_file = self.dist_dir / 'checksums.txt'
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            for file_path in self.dist_dir.glob('*'):
                if file_path.is_file() and file_path.name != 'checksums.txt':
                    # 计算 SHA256
                    sha256_hash = hashlib.sha256()
                    with open(file_path, 'rb') as binary_file:
                        for chunk in iter(lambda: binary_file.read(4096), b''):
                            sha256_hash.update(chunk)
                    
                    checksum = sha256_hash.hexdigest()
                    f.write(f'{checksum}  {file_path.name}\n')
                    self.log(f'macOS 输出: {file_path.name}: {checksum}')
                    
        return True
        
    def build(self):
        """执行完整构建流程"""
        self.log('=' * 60)
        self.log('SmartRenamer macOS 构建脚本')
        self.log('=' * 60)
        
        # 检查环境
        if not self.check_environment():
            return False
            
        # 清理构建目录
        if self.clean:
            self.clean_build()
            
        # 安装依赖
        if not self.install_dependencies():
            self.log('依赖安装失败', 'ERROR')
            return False
            
        # 生成图标
        if not self.generate_icons():
            self.log('图标生成失败', 'WARNING')
            # 不返回 False，继续构建
            
        # 构建可执行文件
        if not self.build_executable():
            self.log('可执行文件构建失败', 'ERROR')
            return False
            
        # 创建 DMG 镜像
        if not self.create_installer():
            self.log('DMG 镜像创建失败', 'WARNING')
            # 不返回 False，因为 .app 文件已经生成
            
        # 生成校验和
        if not self.generate_checksums():
            self.log('校验和生成失败', 'WARNING')
            
        self.log('=' * 60)
        self.log('macOS 构建完成！')
        self.log(f'输出目录: {self.dist_dir}')
        self.log(f'生成文件: SmartRenamer.app 和 SmartRenamer-macOS.dmg')
        self.log('=' * 60)
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SmartRenamer macOS 构建脚本')
    parser.add_argument('--clean', action='store_true', help='清理构建目录')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    builder = Builder(clean=args.clean, debug=args.debug)
    
    if builder.build():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

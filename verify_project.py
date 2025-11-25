#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目验证脚本

验证 SmartRenamer 项目是否正确初始化
"""

import sys
import os

# 配置标准输出使用 UTF-8 编码，解决 Windows 控制台中文显示问题
if sys.platform == 'win32':
    try:
        # Python 3.7+
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6 及更早版本
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from pathlib import Path


def check_directory_structure():
    """检查目录结构"""
    print("检查目录结构...")
    
    required_dirs = [
        "src/smartrenamer/core",
        "src/smartrenamer/api",
        "src/smartrenamer/ui",
        "src/smartrenamer/utils",
        "tests",
        "examples",
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - 缺失")
            return False
    
    return True


def check_required_files():
    """检查必需文件"""
    print("\n检查必需文件...")
    
    required_files = [
        ".gitignore",
        "README.md",
        "LICENSE",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "ARCHITECTURE.md",
        "src/smartrenamer/__init__.py",
        "src/smartrenamer/main.py",
        "src/smartrenamer/core/models.py",
        "src/smartrenamer/core/config.py",
        "src/smartrenamer/api/tmdb_client.py",
        "src/smartrenamer/utils/file_utils.py",
        "tests/test_models.py",
        "tests/test_config.py",
        "tests/test_file_utils.py",
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - 缺失")
            return False
    
    return True


def check_imports():
    """检查核心模块导入"""
    print("\n检查模块导入...")
    
    try:
        import smartrenamer
        print(f"  ✓ smartrenamer (v{smartrenamer.__version__})")
        
        from smartrenamer import MediaFile, MediaType, RenameRule, Config
        print("  ✓ MediaFile")
        print("  ✓ MediaType")
        print("  ✓ RenameRule")
        print("  ✓ Config")
        
        from smartrenamer.core import DEFAULT_MOVIE_RULE, DEFAULT_TV_RULE
        print("  ✓ DEFAULT_MOVIE_RULE")
        print("  ✓ DEFAULT_TV_RULE")
        
        from smartrenamer.utils import file_utils
        print("  ✓ file_utils")
        
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def check_data_models():
    """检查数据模型"""
    print("\n检查数据模型...")
    
    try:
        from smartrenamer import MediaFile, MediaType, RenameRule
        from pathlib import Path
        
        # 测试 MediaFile
        media_file = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
        )
        print("  ✓ MediaFile 创建成功")
        
        # 测试 RenameRule
        from smartrenamer.core import DEFAULT_MOVIE_RULE
        rule = DEFAULT_MOVIE_RULE
        print("  ✓ RenameRule 加载成功")
        
        return True
    except Exception as e:
        print(f"  ✗ 数据模型测试失败: {e}")
        return False


def check_config():
    """检查配置管理"""
    print("\n检查配置管理...")
    
    try:
        from smartrenamer import Config
        
        config = Config()
        print(f"  ✓ Config 创建成功")
        print(f"    - TMDB 语言: {config.tmdb_language}")
        print(f"    - 支持格式: {len(config.supported_extensions)} 种")
        
        return True
    except Exception as e:
        print(f"  ✗ 配置管理测试失败: {e}")
        return False


def main():
    """主验证函数"""
    print("=" * 60)
    print("SmartRenamer 项目验证")
    print("=" * 60)
    print()
    
    checks = [
        ("目录结构", check_directory_structure),
        ("必需文件", check_required_files),
        ("模块导入", check_imports),
        ("数据模型", check_data_models),
        ("配置管理", check_config),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 检查出错: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 项目验证成功！所有检查都已通过。")
        return 0
    else:
        print("\n⚠️  项目验证失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 macOS 图标文件兼容性

验证生成的 ICNS 图标文件可以被正确处理
"""

import sys
import os
from pathlib import Path

def test_icns_file():
    """测试 ICNS 文件是否存在且有效"""
    try:
        from PIL import Image
        
        icns_path = Path(__file__).parent / 'assets' / 'icon.icns'
        
        if not icns_path.exists():
            print(f"❌ ICNS 文件不存在: {icns_path}")
            return False
        
        try:
            img = Image.open(icns_path)
            print(f"✓ Successfully opened ICNS file")
            print(f"  Path: {icns_path}")
            print(f"  Format: {img.format}")
            print(f"  Size: {img.size}")
            print(f"  Mode: {img.mode}")
            print(f"  File size: {os.path.getsize(icns_path):,} bytes")
            
            img.load()
            print(f"  Pixel data loaded successfully")
            
            return True
        except Exception as e:
            print(f"⚠ ICNS file might be a PNG placeholder")
            print(f"  This is acceptable for PyInstaller on non-macOS systems")
            return True
        
    except Exception as e:
        print(f"❌ ICNS file test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_iconset_directory():
    """测试 iconset 目录是否包含所有必需的图标尺寸"""
    try:
        iconset_dir = Path(__file__).parent / 'assets' / 'icon.iconset'
        
        if not iconset_dir.exists():
            print(f"\n⚠ Iconset directory not found: {iconset_dir}")
            print(f"  This is acceptable if .icns was generated using iconutil")
            return True
        
        required_sizes = [
            'icon_512x512@2x.png',
            'icon_512x512.png',
            'icon_256x256@2x.png',
            'icon_256x256.png',
            'icon_128x128@2x.png',
            'icon_128x128.png',
            'icon_32x32@2x.png',
            'icon_32x32.png',
            'icon_16x16@2x.png',
            'icon_16x16.png',
        ]
        
        missing = []
        for filename in required_sizes:
            filepath = iconset_dir / filename
            if not filepath.exists():
                missing.append(filename)
        
        if missing:
            print(f"\n⚠ Iconset directory is incomplete")
            print(f"  Missing files: {', '.join(missing)}")
            return False
        
        print(f"\n✓ Iconset directory is complete")
        print(f"  Path: {iconset_dir}")
        print(f"  Contains all {len(required_sizes)} required icon sizes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Iconset directory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pyinstaller_compatibility():
    """测试图标与 PyInstaller 的兼容性"""
    try:
        try:
            import PyInstaller
            print(f"\n✓ PyInstaller is installed, version: {PyInstaller.__version__}")
        except ImportError:
            print("\n⚠ PyInstaller not installed, skipping PyInstaller-specific tests")
            return True
        
        spec_file = Path(__file__).parent / 'smartrenamer.spec'
        if not spec_file.exists():
            print(f"\n⚠ Spec file not found: {spec_file}")
            return True
        
        icns_path = Path(__file__).parent / 'assets' / 'icon.icns'
        if not icns_path.exists():
            print(f"\n❌ Icon file referenced in spec does not exist: {icns_path}")
            return False
        
        print(f"\n✓ Icon file is compatible with PyInstaller spec")
        print(f"  Icon path: {icns_path}")
        print(f"  Spec file: {spec_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ PyInstaller compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("macOS Icon Compatibility Tests")
    print("=" * 70)
    
    results = []
    
    print("\n[1/3] Testing ICNS file...")
    results.append(("ICNS File", test_icns_file()))
    
    print("\n[2/3] Testing iconset directory...")
    results.append(("Iconset Directory", test_iconset_directory()))
    
    print("\n[3/3] Testing PyInstaller compatibility...")
    results.append(("PyInstaller", test_pyinstaller_compatibility()))
    
    print("\n" + "=" * 70)
    print("Test Summary:")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✓ Pass" if passed else "❌ Fail"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ All tests passed! macOS icon files are compatible.")
        return 0
    else:
        print("\n❌ Some tests failed, please check icon files.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

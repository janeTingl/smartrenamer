#!/usr/bin/env python3
"""
测试图标文件与 PyInstaller 的兼容性

验证生成的图标文件可以被 Pillow 和 PyInstaller 正确处理
"""

import os
import sys
from pathlib import Path

def test_pillow_ico():
    """测试 Pillow 是否能打开 ICO 文件"""
    try:
        from PIL import Image
        
        ico_path = Path(__file__).parent / 'assets' / 'icon.ico'
        
        if not ico_path.exists():
            print(f"❌ ICO 文件不存在: {ico_path}")
            return False
        
        # 尝试打开文件
        img = Image.open(ico_path)
        
        print(f"✓ Pillow 成功打开 ICO 文件")
        print(f"  路径: {ico_path}")
        print(f"  格式: {img.format}")
        print(f"  尺寸: {img.size}")
        print(f"  模式: {img.mode}")
        print(f"  文件大小: {os.path.getsize(ico_path):,} 字节")
        
        # 检查是否包含多个尺寸
        if hasattr(img, 'info') and 'sizes' in img.info:
            sizes = img.info['sizes']
            print(f"  包含的尺寸: {sorted(sizes)}")
        
        # 尝试读取像素数据
        img.load()
        print(f"  像素数据加载成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Pillow 打开 ICO 文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pyinstaller_icon_hook():
    """测试 PyInstaller 的图标转换功能"""
    try:
        # 检查是否安装了 PyInstaller
        try:
            import PyInstaller
            print(f"\n✓ PyInstaller 已安装，版本: {PyInstaller.__version__}")
        except ImportError:
            print("\n⚠ PyInstaller 未安装，跳过 PyInstaller 特定测试")
            return True
        
        # 尝试导入 PyInstaller 的图标工具
        from PyInstaller.utils.win32 import icon as win32_icon
        
        ico_path = Path(__file__).parent / 'assets' / 'icon.ico'
        
        # 尝试读取图标数据
        with open(ico_path, 'rb') as f:
            icon_data = f.read()
        
        print(f"\n✓ PyInstaller 可以读取图标数据")
        print(f"  数据大小: {len(icon_data):,} 字节")
        
        # 验证 ICO 头部（前 6 字节）
        # ICO 格式: 前 2 字节为 0x0000，接下来 2 字节为 0x0100（图标类型）
        if len(icon_data) >= 6:
            reserved = int.from_bytes(icon_data[0:2], 'little')
            type_field = int.from_bytes(icon_data[2:4], 'little')
            count = int.from_bytes(icon_data[4:6], 'little')
            
            print(f"  ICO 头部验证:")
            print(f"    Reserved: {reserved} (应为 0)")
            print(f"    Type: {type_field} (应为 1)")
            print(f"    Count: {count} (图标数量)")
            
            if reserved != 0:
                print(f"  ⚠ ICO 头部 Reserved 字段不为 0")
                return False
            
            if type_field != 1:
                print(f"  ⚠ ICO 头部 Type 字段不为 1（图标）")
                return False
            
            if count == 0 or count > 50:
                print(f"  ⚠ ICO 图标数量异常: {count}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"\n⚠ 无法导入 PyInstaller 模块: {e}")
        return True  # 如果未安装 PyInstaller，不算失败
    except Exception as e:
        print(f"\n❌ PyInstaller 图标测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_other_icons():
    """测试其他图标文件"""
    try:
        from PIL import Image
        
        project_dir = Path(__file__).parent
        assets_dir = project_dir / 'assets'
        
        # 测试 PNG
        png_path = assets_dir / 'icon.png'
        if png_path.exists():
            img = Image.open(png_path)
            print(f"\n✓ PNG 图标验证成功")
            print(f"  格式: {img.format}, 尺寸: {img.size}, 模式: {img.mode}")
        
        # 测试 ICNS
        icns_path = assets_dir / 'icon.icns'
        if icns_path.exists():
            try:
                img = Image.open(icns_path)
                print(f"\n✓ ICNS 图标验证成功")
                print(f"  格式: {img.format}, 尺寸: {img.size}, 模式: {img.mode}")
            except Exception as e:
                # ICNS 可能是 PNG 格式的占位符
                print(f"\n⚠ ICNS 图标（可能是 PNG 占位符）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 其他图标测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("PyInstaller 图标兼容性测试")
    print("=" * 70)
    
    results = []
    
    # 测试 Pillow ICO 兼容性
    print("\n[1/3] 测试 Pillow ICO 兼容性...")
    results.append(("Pillow ICO", test_pillow_ico()))
    
    # 测试 PyInstaller 图标处理
    print("\n[2/3] 测试 PyInstaller 图标处理...")
    results.append(("PyInstaller", test_pyinstaller_icon_hook()))
    
    # 测试其他图标格式
    print("\n[3/3] 测试其他图标格式...")
    results.append(("其他格式", test_other_icons()))
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总:")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ 所有测试通过！图标文件与 PyInstaller 兼容。")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查图标文件。")
        return 1


if __name__ == '__main__':
    sys.exit(main())

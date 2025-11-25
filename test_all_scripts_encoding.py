#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有脚本的 UTF-8 编码配置

检查所有 Python 脚本是否包含正确的 UTF-8 编码配置
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
import re


def check_file_encoding_config(file_path):
    """
    检查文件是否包含正确的 UTF-8 编码配置
    
    返回：
        (bool, str): (是否配置正确, 详细信息)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查编码声明
        has_coding_declaration = bool(re.search(r'#.*-\*-.*coding:.*utf-8.*-\*-', content))
        
        # 检查 Windows 编码配置
        has_windows_config = bool(re.search(
            r'if\s+sys\.platform\s*==\s*[\'"]win32[\'"].*sys\.stdout\.reconfigure',
            content,
            re.DOTALL
        ))
        
        if has_coding_declaration and has_windows_config:
            return True, "✓ 配置完整"
        elif not has_coding_declaration and not has_windows_config:
            return None, "⚪ 无中文输出（不需要配置）"
        elif has_coding_declaration and not has_windows_config:
            return False, "⚠ 缺少 Windows 编码配置"
        elif not has_coding_declaration and has_windows_config:
            return False, "⚠ 缺少编码声明"
        else:
            return False, "❌ 配置不完整"
            
    except Exception as e:
        return False, f"❌ 检查失败: {e}"


def main():
    """主函数"""
    print("=" * 70)
    print("验证所有脚本的 UTF-8 编码配置")
    print("=" * 70)
    
    # 定义需要检查的脚本列表
    script_groups = {
        "核心脚本": [
            "generate_icons.py",
            "test_icon_compat.py",
            "verify_project.py",
            "test_encoding_fix.py",
        ],
        "构建脚本": [
            "scripts/build.py",
        ],
        "示例脚本": [
            "examples/basic_usage.py",
            "examples/parser_and_matcher_example.py",
            "examples/scan_library_example.py",
            "examples/renamer_example.py",
            "examples/storage_example.py",
        ],
    }
    
    project_root = Path(__file__).parent
    total_checked = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    results = []
    
    # 检查每个脚本
    for group_name, scripts in script_groups.items():
        print(f"\n【{group_name}】")
        print("-" * 70)
        
        for script_path in scripts:
            full_path = project_root / script_path
            
            if not full_path.exists():
                status = "❌ 文件不存在"
                results.append((group_name, script_path, False, status))
                total_failed += 1
            else:
                status_ok, status_msg = check_file_encoding_config(full_path)
                results.append((group_name, script_path, status_ok, status_msg))
                
                if status_ok is True:
                    total_passed += 1
                elif status_ok is False:
                    total_failed += 1
                else:
                    total_skipped += 1
            
            total_checked += 1
            print(f"  {script_path:<50} {status_msg}")
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("检查结果汇总")
    print("=" * 70)
    print(f"  总计检查: {total_checked} 个文件")
    print(f"  ✓ 配置正确: {total_passed} 个")
    print(f"  ❌ 配置错误: {total_failed} 个")
    print(f"  ⚪ 无需配置: {total_skipped} 个")
    print("=" * 70)
    
    # 显示失败的文件
    if total_failed > 0:
        print("\n⚠ 以下文件需要修复:")
        for group, path, status, msg in results:
            if status is False:
                print(f"  - {path}: {msg}")
        print()
        return 1
    else:
        print("\n✓ 所有脚本的 UTF-8 编码配置正确！")
        return 0


if __name__ == '__main__':
    sys.exit(main())

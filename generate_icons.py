#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 SmartRenamer macOS 应用图标

为 macOS (.icns) 平台生成应用图标。
图标包含 "SR" 字母，代表 SmartRenamer。
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_base_icon(size=512):
    """
    创建基础图标图像
    
    Args:
        size: 图标尺寸（正方形）
    
    Returns:
        PIL.Image: 图标图像
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    padding = size // 10
    bg_color = (41, 128, 185, 255)
    
    draw.rounded_rectangle(
        [(padding, padding), (size - padding, size - padding)],
        radius=size // 8,
        fill=bg_color
    )
    
    text = "SR"
    text_color = (255, 255, 255, 255)
    
    try:
        font_size = size // 2
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        
        if font is None:
            font = ImageFont.load_default()
    except Exception as e:
        print(f"Warning: Could not load font, using default: {e}")
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2 - bbox[0]
    text_y = (size - text_height) // 2 - bbox[1]
    
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    return img


def save_icns(img, output_path):
    """
    Save as ICNS format for macOS
    
    Creates an iconset directory with all required sizes,
    then uses iconutil to generate the .icns file.
    """
    sizes = {
        'icon_512x512@2x': 1024,
        'icon_512x512': 512,
        'icon_256x256@2x': 512,
        'icon_256x256': 256,
        'icon_128x128@2x': 256,
        'icon_128x128': 128,
        'icon_32x32@2x': 64,
        'icon_32x32': 32,
        'icon_16x16@2x': 32,
        'icon_16x16': 16,
    }
    
    iconset_dir = output_path.replace('.icns', '.iconset')
    os.makedirs(iconset_dir, exist_ok=True)
    
    for name, size in sizes.items():
        icon = img.resize((size, size), Image.Resampling.LANCZOS)
        icon.save(os.path.join(iconset_dir, f'{name}.png'), 'PNG')
    
    print(f"✓ Created iconset directory: {iconset_dir}")
    print(f"  Tip: On macOS, use the following command to generate .icns file:")
    print(f"  iconutil -c icns {iconset_dir}")
    
    if os.path.exists('/usr/bin/iconutil'):
        import subprocess
        try:
            subprocess.run(
                ['iconutil', '-c', 'icns', iconset_dir, '-o', output_path],
                check=True
            )
            print(f"✓ Created ICNS icon: {output_path}")
        except Exception as e:
            print(f"Warning: Could not generate ICNS file: {e}")
    else:
        icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        icon_512.save(output_path, 'PNG')
        print(f"✓ Created ICNS placeholder (PNG format): {output_path}")


def main():
    """Main function"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_root, 'assets')
    
    os.makedirs(assets_dir, exist_ok=True)
    
    print("Generating SmartRenamer macOS application icon...")
    print("=" * 60)
    
    base_icon = create_base_icon(512)
    
    save_icns(base_icon, os.path.join(assets_dir, 'icon.icns'))
    
    print("=" * 60)
    print("✓ Icon generation complete!")
    
    print("\nVerifying generated file:")
    filename = 'icon.icns'
    filepath = os.path.join(assets_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size:,} bytes")
        
        try:
            img = Image.open(filepath)
            print(f"    → Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        except Exception as e:
            print(f"    → Warning: Could not verify image: {e}")


if __name__ == '__main__':
    main()

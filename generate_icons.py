#!/usr/bin/env python3
"""
生成 SmartRenamer 应用图标

为 Windows (.ico)、macOS (.icns) 和 Linux (.png) 平台生成应用图标。
图标包含 "SR" 字母，代表 SmartRenamer。
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_base_icon(size=512):
    """
    创建基础图标图像
    
    Args:
        size: 图标尺寸（正方形）
    
    Returns:
        PIL.Image: 图标图像
    """
    # 创建带透明背景的图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆角矩形背景
    padding = size // 10
    bg_color = (41, 128, 185, 255)  # 蓝色背景
    
    # 绘制圆角矩形
    draw.rounded_rectangle(
        [(padding, padding), (size - padding, size - padding)],
        radius=size // 8,
        fill=bg_color
    )
    
    # 绘制 "SR" 文字
    text = "SR"
    text_color = (255, 255, 255, 255)  # 白色文字
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        font_size = size // 2
        # 尝试多个字体路径
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        
        if font is None:
            # 使用默认字体
            font = ImageFont.load_default()
    except Exception as e:
        print(f"警告: 无法加载字体，使用默认字体: {e}")
        font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2 - bbox[0]
    text_y = (size - text_height) // 2 - bbox[1]
    
    # 绘制文字
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    return img


def save_png(img, output_path):
    """保存为 PNG 格式"""
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已创建 PNG 图标: {output_path}")


def save_ico(img, output_path):
    """
    保存为 ICO 格式（Windows）
    
    ICO 文件包含多个尺寸的图标
    """
    # Windows ICO 标准尺寸
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    
    # 创建多尺寸图标
    icons = []
    for size in sizes:
        icon = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(icon)
    
    # 保存为 ICO（第一个图像为主图像，其余为不同尺寸）
    icons[0].save(
        output_path,
        format='ICO',
        sizes=[icon.size for icon in icons],
        append_images=icons[1:]
    )
    print(f"✓ 已创建 ICO 图标: {output_path}")


def save_icns(img, output_path):
    """
    保存为 ICNS 格式（macOS）
    
    注意：Pillow 本身不支持 ICNS 格式，需要使用其他工具。
    这里我们保存为 PNG，然后建议使用 iconutil 或其他工具转换。
    """
    # macOS iconset 标准尺寸
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
    
    # 创建 iconset 目录
    iconset_dir = output_path.replace('.icns', '.iconset')
    os.makedirs(iconset_dir, exist_ok=True)
    
    # 生成各个尺寸的图标
    for name, size in sizes.items():
        icon = img.resize((size, size), Image.Resampling.LANCZOS)
        icon.save(os.path.join(iconset_dir, f'{name}.png'), 'PNG')
    
    print(f"✓ 已创建 iconset 目录: {iconset_dir}")
    print(f"  提示: 在 macOS 上可以使用以下命令生成 .icns 文件:")
    print(f"  iconutil -c icns {iconset_dir}")
    
    # 尝试使用 iconutil 生成 .icns（仅在 macOS 上）
    if os.path.exists('/usr/bin/iconutil'):
        import subprocess
        try:
            subprocess.run(
                ['iconutil', '-c', 'icns', iconset_dir, '-o', output_path],
                check=True
            )
            print(f"✓ 已创建 ICNS 图标: {output_path}")
        except Exception as e:
            print(f"警告: 无法生成 ICNS 文件: {e}")
    else:
        # 如果不在 macOS 上，只创建一个 512x512 的 PNG 并重命名为 .icns
        # PyInstaller 在某些情况下可以接受 PNG 格式的 .icns
        icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        icon_512.save(output_path, 'PNG')
        print(f"✓ 已创建 ICNS 占位符（PNG 格式）: {output_path}")


def main():
    """主函数"""
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_root, 'assets')
    
    # 确保 assets 目录存在
    os.makedirs(assets_dir, exist_ok=True)
    
    print("正在生成 SmartRenamer 应用图标...")
    print("=" * 60)
    
    # 创建基础图标（512x512）
    base_icon = create_base_icon(512)
    
    # 保存为各种格式
    save_png(base_icon, os.path.join(assets_dir, 'icon.png'))
    save_ico(base_icon, os.path.join(assets_dir, 'icon.ico'))
    save_icns(base_icon, os.path.join(assets_dir, 'icon.icns'))
    
    print("=" * 60)
    print("✓ 图标生成完成！")
    
    # 验证文件
    print("\n验证生成的文件:")
    for filename in ['icon.png', 'icon.ico', 'icon.icns']:
        filepath = os.path.join(assets_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  {filename}: {size:,} 字节")
            
            # 尝试打开验证
            try:
                img = Image.open(filepath)
                print(f"    → 格式: {img.format}, 尺寸: {img.size}, 模式: {img.mode}")
            except Exception as e:
                print(f"    → 警告: 无法验证图像: {e}")


if __name__ == '__main__':
    main()

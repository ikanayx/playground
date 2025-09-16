import subprocess
import os
import argparse

"""
如果你已经安装了 Homebrew（macOS 包管理器），直接运行：
brew install ghostscript

安装完成后，验证是否成功：
gs --version
如果显示版本号，说明安装成功
"""


def compress_pdf_ghostscript(input_path, output_path, quality=3):
    """
    使用 Ghostscript 压缩 PDF
    :param input_path: 输入 PDF 路径
    :param output_path: 输出 PDF 路径
    :param quality: 压缩质量（1=低质量高压缩，2=中等，3=高质量低压缩）
    """
    # Ghostscript 参数
    gs_params = [
        "gs",  # macOS/Linux 直接调用 gs，Windows 用 gswin64c
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        # "-sColorConversionStrategy=Gray",
        # "-dProcessColorModel=/DeviceGray",
        f"-dPDFSETTINGS=/{['screen', 'ebook', 'prepress'][quality - 1]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]

    try:
        subprocess.run(gs_params, check=True)
        print(f"✅ PDF 压缩成功！压缩质量: {quality}, 保存至: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 压缩失败: {e}")
    except FileNotFoundError:
        print("❌ 未找到 Ghostscript，请确保已安装！")


def add_suffix_to_filename(absolute_path, suffix):
    """
    给文件的绝对路径中的文件名添加指定尾缀

    参数:
        absolute_path: str - 文件的绝对路径
        suffix: str - 要添加的尾缀

    返回:
        str - 添加尾缀后的新绝对路径
    """
    # 分离文件的目录路径和文件名
    dir_path, file_name = os.path.split(absolute_path)

    # 分离文件名和扩展名
    file_base, file_ext = os.path.splitext(file_name)

    # 构建新的文件名（在文件名和扩展名之间添加尾缀）
    new_file_name = f"{file_base}{suffix}{file_ext}"

    # 组合新的绝对路径
    new_absolute_path = os.path.join(dir_path, new_file_name)

    return new_absolute_path


# 使用示例
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='切割长图片为多张短图')
    parser.add_argument('--input', required=True, help='输入图片路径')
    parser.add_argument('--output', help='输出图片目录')
    parser.add_argument('--quality', type=int, default=2, help='压缩质量，1=低质量，2=中等，3=高质量')

    args = parser.parse_args()

    quality = args.quality
    path_in = args.input
    if not args.output:
        path_out = add_suffix_to_filename(path_in, '_compressed')
    else:
        path_out = args.output
    compress_pdf_ghostscript(path_in, path_out, quality)

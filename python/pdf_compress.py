import subprocess
import os

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
        f"-dPDFSETTINGS=/{['screen', 'ebook', 'prepress'][quality - 1]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]

    try:
        subprocess.run(gs_params, check=True)
        print(f"✅ PDF 压缩成功！保存至: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 压缩失败: {e}")
    except FileNotFoundError:
        print("❌ 未找到 Ghostscript，请确保已安装！")


# 使用示例
if __name__ == "__main__":
    input_pdf = "/path/to/input.pdf"
    output_pdf = "/path/to/output.pdf"
    compress_pdf_ghostscript(input_pdf, output_pdf, quality=1)  # 中等压缩

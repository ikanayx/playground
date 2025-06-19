import os

from PyPDF2 import PdfWriter, PdfReader


def split_pdf(input_pdf_path, output_folder, pages_per_pdf=1):
    """直接按页数拆分PDF"""
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    os.makedirs(output_folder, exist_ok=True)
    generated_files = []

    for i in range(0, total_pages, pages_per_pdf):
        writer = PdfWriter()
        end = min(i + pages_per_pdf, total_pages)

        for j in range(i, end):
            writer.add_page(reader.pages[j])

        output_path = os.path.join(output_folder, f"part_{i // pages_per_pdf + 1}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
        generated_files.append(output_path)

    return generated_files

# 使用示例
if __name__ == "__main__":
    # 替换为你的PDF文件路径
    input_pdf = "/path/to/large_file.pdf"

    # 输出文件夹
    output_dir = "/path/to/split_files"

    # 每个小PDF包含100张图片
    split_pdf(input_pdf, output_dir, pages_per_pdf=100)

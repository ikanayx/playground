import os
from PIL import Image
from pathlib import Path
import argparse


def resize_images(input_dir, output_dir, scale_factor=0.5):
    """
    调整目录中所有图片的尺寸

    参数:
    input_dir (str): 输入图片目录
    output_dir (str): 输出图片目录
    scale_factor (float): 缩放因子，默认为0.5（即缩小为原图的一半）
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 支持的图片格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}

    # 获取输出目录中已存在的带@2x后缀的图片
    existing_output_files = set()
    for filename in os.listdir(output_dir):
        if '@2x' in filename:
            # 提取原始文件名（不包含@2x和扩展名）
            base_name = filename.split('@2x')[0]
            existing_output_files.add(base_name.lower())

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        # 检查是否为文件且为支持的图片格式
        if os.path.isfile(file_path):
            file_ext = Path(filename).suffix.lower()
            if file_ext in supported_formats:
                # 提取文件名（不包含扩展名）
                base_name = Path(filename).stem

                # 检查是否已存在处理过的文件
                if base_name.lower() in existing_output_files:
                    print(f"跳过已处理的文件: {filename}")
                    continue

                try:
                    # 打开图片
                    with Image.open(file_path) as img:
                        # 获取原始尺寸
                        width, height = img.size

                        # 计算新尺寸
                        new_width = int(width * scale_factor)
                        new_height = int(height * scale_factor)

                        # 调整尺寸
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        # 构建输出文件名（添加@2x后缀）
                        new_filename = f"{base_name}@2x{file_ext}"
                        output_path = os.path.join(output_dir, new_filename)

                        # 保存图片，保留原始格式
                        resized_img.save(output_path)

                        print(f"已调整: {filename} ({width}x{height} -> {new_width}x{new_height})")
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {str(e)}")
            else:
                print(f"跳过非图片文件: {filename}")


def main():
    parser = argparse.ArgumentParser(description='批量调整图片尺寸为原图的一半')
    parser.add_argument('--input', required=True, help='输入图片目录')
    parser.add_argument('--output', required=True, help='输出图片目录')
    parser.add_argument('--scale', type=float, default=0.5, help='缩放因子，默认为0.5')

    args = parser.parse_args()
    input_d = args.input
    out_d = args.output
    scale_f = args.scale

    # 验证输入目录是否存在
    if not os.path.isdir(input_d):
        print(f"错误: 输入目录 '{input_d}' 不存在")
        return

    resize_images(input_d, out_d, scale_f)


if __name__ == "__main__":
    main()
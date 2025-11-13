from PIL import Image
import os
from typing import List, Tuple


def crop_images(image_paths: List[str],
                crop_area: Tuple[int, int, int, int],
                output_dir: str = "cropped_images") -> None:
    """
    裁剪一批图片的指定区域并保存到输出目录

    参数:
        image_paths: 图片绝对路径的列表
        crop_area: 裁剪区域，格式为(left, upper, right, lower)
        output_dir: 裁剪后图片的保存目录，默认为"cropped_images"
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    for img_path in image_paths:
        try:
            # 检查文件是否存在
            if not os.path.exists(img_path):
                print(f"警告: 文件不存在 - {img_path}")
                continue

            # 打开图片
            with Image.open(img_path) as img:
                # 检查裁剪区域是否有效
                img_width, img_height = img.size
                left, upper, right, lower = crop_area

                if left < 0 or upper < 0 or right > img_width or lower > img_height:
                    print(f"警告: 裁剪区域超出图片范围 - {img_path}")
                    continue

                if left >= right or upper >= lower:
                    print(f"警告: 无效的裁剪区域 - {img_path}")
                    continue

                # 裁剪图片
                cropped_img = img.crop(crop_area)

                # 生成输出文件名
                file_name = os.path.basename(img_path)
                name, ext = os.path.splitext(file_name)
                output_name = f"{name}_cropped{ext}"
                output_path = os.path.join(output_dir, output_name)

                # 保存裁剪后的图片
                cropped_img.save(output_path)
                print(f"已保存: {output_path}")

        except Exception as e:
            print(f"处理 {img_path} 时出错: {str(e)}")


if __name__ == "__main__":
    # 示例用法
    if True:  # 设为True时运行示例
        # 示例图片路径列表（请替换为实际图片路径）
        example_image_paths = [
            '/path/to/png',
        ]

        # 示例裁剪区域 (left, upper, right, lower)
        # 坐标原点在左上角，向右为x轴正方向，向下为y轴正方向
        example_crop_area = (0, 0, 1360, 230)  # 裁剪一个区域

        # 调用裁剪函数
        if example_image_paths:
            crop_images(example_image_paths, example_crop_area)
        else:
            print("请在example_image_paths中添加图片路径以运行示例")

import os

import cv2
from os.path import join, exists
from os import mkdir
from PIL import Image
import argparse


def opencv_handler(src_dir, dst_dir, split_height = 1024):
    if not exists(dst_dir):
        mkdir(dst_dir)

    img = cv2.imread(src_dir)
    shape = img.shape
    print(shape)
    height = shape[0]
    width = shape[1]
    if height < 1420:
        print('高度不足，退出裁剪')
        exit(0)
    offset = 0
    serial_no = 1
    while True:
        start_y = offset
        end_y = min(start_y + split_height, height)
        cropped = img[start_y:end_y, 0:width] # 裁剪坐标为[y0:y1, x0:x1]
        cv2.imwrite(join(str(dst_dir), "img_" + str(serial_no) + ".png"), cropped)
        if end_y == height:
            break
        offset = end_y
        serial_no = serial_no + 1


def pillow_handler(src_file_path, dst_dir, split_height = 1024):

    # 步骤1：提取文件名（包含扩展名）
    file_name_with_ext = os.path.basename(src_file_path)  # 结果："report.pdf"
    # 步骤2：分割文件名和扩展名，取文件名部分
    file_name = os.path.splitext(file_name_with_ext)[0]  # 结果："report"

    dst_dir = join(dst_dir, file_name)
    if not exists(dst_dir):
        mkdir(dst_dir)

    img = Image.open(src_file_path)
    shape = img.size
    print(shape)
    height = shape[1]
    width = shape[0]
    if height < 1420:
        print('高度不足，退出裁剪')
        exit(0)
    offset = 0
    serial_no = 1
    while True:
        start_y = offset
        end_y = min(start_y + split_height, height)
        cropped = img.crop((0, start_y, width, end_y))  # (left, upper, right, lower)
        cropped.save(join(str(dst_dir), file_name + "_" + str(serial_no) + ".png"))
        if end_y == height:
            break
        offset = end_y
        serial_no = serial_no + 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='切割长图片为多张短图')
    parser.add_argument('--input', required=True, help='输入图片路径')
    parser.add_argument('--output', required=True, help='输出图片目录')
    parser.add_argument('--delta', type=float, default=750, help='每张图片高度，默认为750')

    args = parser.parse_args()

    src_dir0 = args.input
    dst_dir0 = args.output

    delta = args.delta
    # opencv比较快，裁剪出来的图体积较大，python依赖包也大
    # opencv_handler(src_dir0, dst_dir0, delta)

    # pillow与opencv相比处理较慢，裁剪出来的图片文件体积比opencv的小
    pillow_handler(src_dir0, dst_dir0, delta)

import cv2
import time
from os.path import join, exists
from os import mkdir
from PIL import Image


def opencv_handler(src_dir, dst_dir, file_name, split_height = 1024):
    img = cv2.imread(join(str(src_dir), str(file_name)))
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


def pillow_handler(src_dir, dst_dir, file_name, split_height = 1024):
    img = Image.open(join(str(src_dir), str(file_name)))
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
        cropped.save(join(str(dst_dir), "img_" + str(serial_no) + ".png"))
        if end_y == height:
            break
        offset = end_y
        serial_no = serial_no + 1


if __name__ == '__main__':
    src_dir0 = '/path/to/long_image'
    dst_dir0 = '/path/to/split_image_' + str(int(time.time()))
    # split_time = time.strftime('%Y%m%d_%H%M', time.localtime(time.time()))
    if not exists(dst_dir0):
        mkdir(dst_dir0)
    file_name0 = "rule.png"
    delta = 1200
    # opencv比较快，裁剪出来的图体积较大，python依赖包也大
    # opencv_handler(src_dir0, dst_dir0, file_name0, delta)

    # pillow与opencv相比处理较慢，裁剪出来的图片文件体积比opencv的小
    pillow_handler(src_dir0, dst_dir0, file_name0, delta)

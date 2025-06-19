# -*- coding: utf-8 -*-


import os
from datetime import datetime
# import re
# import time


def rename_by_mtime(files_root):
    prefix = 'wx_'
    for file in os.listdir(files_root):
        if file.startswith(prefix):
            continue
        abs_path_old = os.path.join(files_root, file)
        datetime_instance = datetime.fromtimestamp(os.path.getmtime(abs_path_old))
        mtime_format_name = datetime.strftime(datetime_instance,'%Y%m%d_%H%M')
        print(mtime_format_name)
        p = file.split('.')
        ext = p[1]
        abs_path_new = os.path.join(files_root, prefix + mtime_format_name + '.' + ext)
        if os.path.exists(abs_path_new):
            count = 2
            while True:
                abs_path_new = os.path.join(files_root, prefix + mtime_format_name + '_' + str(count) + '.' + ext)
                if not os.path.exists(abs_path_new):
                    break
                count = count + 1
        os.rename(abs_path_old, abs_path_new)


if __name__ == '__main__':
    files_dir = ''
    rename_by_mtime(files_dir)

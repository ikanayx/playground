#!/usr/bin/python3
# 第一行用于指定Python解析器的位置，仅在Unix系统下生效

#!/usr/bin/env python3
# 解析器位置也可填写↑，这种用法先在 env（环境变量）设置里查找 python 的安装路径，再调用对应路径下的解释器程序完成操作

# 注释方式一：添加井号

'''
注释方式二：使用连续3个单引号
注意：在Unix内核系统直接对.py文件添加执行权限，或执行`sh *.py`时，此注释方式会被判断为执行命令导致出错
'''

"""
注释方式三：使用连续3个双引号
注意：在Unix内核系统直接对.py文件添加执行权限，或执行`sh *.py`时，此注释方式会被判断为执行命令导致出错
"""

print("comment code style.")
print()

# 字符串
# 字符串 * N(N≥1)，代表字符串重复N次
print('repeat string demo:' + '0' * 3)
print()

# 通过在字符串前加控制符r，使字符串内的反斜杠转义符不生效
str0 = r'hello python\tworld'
str0_len = len(str0)
print('str length = ' + str(str0_len))
print()

# 字符串的字符下标分两种：从左往右为0到len-1、从右往左为-1到-len
# 字符串[截取起始下标:截取结束下标:步进]
# -> 索引起始值不能大于结束值
print('-1到-5\t' + str0[-1:-5]) # 这样写索引下标，截取内容是空，索引起始值不能大于结束值
print('-5到-1\t' + str0[-5:-1])
print()

# -> 0:-1是例外，相当于 -len:-1
print('0   到-1\t' + str0[0:-1])
print('-len到-1\t' + str0[-str0_len:-1])
# 截取内容 = 原内容
# print('0到-1\t' + str0[0:str0_len])

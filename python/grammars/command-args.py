#!/usr/bin/python3

# 直接获取执行命令的所有选项值
from sys import argv, exit

print('arg count: ' + str(len(argv)))
print('arg: ' + str(argv)) # -foo bar 选项和值会被认为是2个选项
print('arg[0] = ' + argv[0])

# 使用 getopt 模块
# 支持短选项模式 - 和长选项模式 --
from getopt import getopt, GetoptError

try:
    # 定义短选项，以 - 开头，每个选项都是单个字母，区分大小写
    # ab:c代表接收3个选项，分别是a\b\c，其中跟随-b后的第一个字符串将被视为选项b的值，如果-b后面没有跟随任何内容，则抛出GetoptError错误
    # 正确命令示例: *.py -a -b hello -c
    # 错误命令示例1: *.py -a -b -c '-c'将被认为是-b选项的值，而不是一个有效的选项
    # 错误命令示例2: *.py -a -c    抛出错误 option -b requires argument
    shortopts = 'ab:c'

    # 定义长选项，以 -- 开头
    # 下面定义的长选项中，跟随在--foo1之后的第一个字符串，将被认为是foo1选项的值，foo和foo2可不提供具体值
    # 错误命令示例1: *.py --foo    抛出错误 option --foo1 requires argument
    longopts = ['foo', 'foo1=', 'foo2']

    # getopt的首个参数argv 必须排除执行命令本身
    res = getopt(argv[1:], shortopts, longopts)

    dict = res[0]
    print('dict -> ' + str(dict))
    for option, value in dict:
        print(option, value, sep=":")

    # keys 包含除shortopts和longopts定义以外的选项/参数
    keys = res[1]
    print('keys -> ' + str(keys))

except GetoptError as e:
    print('exception is ' + str(e))
    exit(1)

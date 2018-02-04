#!/usr/bin/env python
# coding:utf-8

import os
import re

f = os.popen('who','r')  #os模块的popen用于读取其它程序运行的输出
for eachLine in f:
	print re.split(r'\s\s+|\t',eachLine.rstrip())
f.close()

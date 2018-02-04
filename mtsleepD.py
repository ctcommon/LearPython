#!/usr/bin/env python
#coding: utf-8

#子类化的Thread,对Thread进行子类化，可以简化线程创建的调用过程，主要是run函数的构建，本例测试参照python核心编程，但是会有多个不同的工作函数

import threading
from time import sleep,ctime

class MyThread(threading.Thread):
	def __init__(self,func,args,name=''):
		threading.Thread.__init__(self)  #子类化记得要调用基类的__init__
		self.name = name
		self.func = func
		self.args = args

	def run(self):  #一定要有run函数
		self.func(*self.args)   #待*号

def loop(nloop,nsec):
	print 'start loop',nloop,'at:', ctime()
	sleep(nsec)
	print 'loop',nloop,'done at:', ctime()

def myfunc():
	print 'run! run! run!'
	sleep(1)
	print 'go! go! go!'

funclist = [loop,loop,myfunc]
argslist = [(0,4),(1,2),()]

def main():
	print 'staring at:',ctime()
	threads = []
	nloops = range(len(funclist))

	for i in nloops:
		t = MyThread(funclist[i],argslist[i],funclist[i].__name__)
		threads.append(t)

	for i in nloops:
		threads[i].start()

	for i in nloops:
		threads[i].join()

	print 'all DONE at:',ctime()

if __name__ == '__main__':
	main()


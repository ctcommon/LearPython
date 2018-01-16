#!/usr/bin/env python
#coding: utf-8
#利用threading的Thread方法先将多个需要调用的函数加入进取，然后放进一个列表threads，这优点线程池的意思？（才学，还需探索）
#然后才遍历线程池并调用相关的操作。这里有点意思的是，先将多个工作函数的参数组成一个列表，然后再需要的时候再遍历加入进去


import threading
from time import sleep, ctime

loops = [4,2]

def loop(nloop,nsec):
	print 'start loop',nloop,'at:',ctime()
	sleep(nsec)
	print 'loop',nloop,'done at:', ctime()

def main():
	print 'starting at:', ctime()
	threads = []
	nloops = range(len(loops))

	for i in nloops:
		t = threading.Thread(target=loop,args=(i,loops[i]))
		threads.append(t)

	for i in nloops:
		threads[i].start()

	for i in nloops:
		threads[i].join()

	print 'all DONE at:',ctime()

if __name__ == '__main__':
	main()

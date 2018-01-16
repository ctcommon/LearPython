#!/usr/bin/env python
#coding:utf-8

#信号量主要是BoundedSemaphore,这里的测试是糖果机最多可以放入5个糖果，用信号量release()方法判定糖果是否超过5个，用acquire(False)测试是否有糖果。
from atexit import register
from random import randrange
from threading import BoundedSemaphore, Lock, Thread
from time import sleep, ctime

lock = Lock()
MAX = 5
candytray = BoundedSemaphore(MAX)

def refill():
	with lock:
		print 'Refilling candy...',
		try:
			candytray.release()
		except ValueError:
			print 'full, skipping'
		else:
			print 'OK'

def buy():
	with lock:
		print 'Buying candy...',
		if candytray.acquire(False):  #计数器即信号量的值不能小于0，因此这个调用一般会在再次增加之前被阻塞。通过传入False让调用不再阻塞，而是在应当阻塞的时候返回一个False，指明为空
			print 'OK'
		else:
			print 'empty, skipping'
		
def producer(loops):
	for i in xrange(loops):
		refill()
		sleep(randrange(3))

def consumer(loops):
	for i in xrange(loops):
		buy()
		sleep(randrange(3))

def _main():
	print 'starting at:', ctime()
	nloops = randrange(2,6)
	print 'THE CANDY MATCHINE (full with %d bars)!' % MAX
	Thread(target=consumer, args=(randrange(nloops,nloops+MAX+2),)).start()
	Thread(target=producer, args=(nloops,)).start()

@register
def _atexit():
	print 'all DONE at:', ctime()

if __name__ == '__main__':
	_main()

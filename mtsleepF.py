#!/usr/bin/env python
#coding:utf-8
from atexit import register
from random import randrange
from threading import Thread, Lock, currentThread
from time import sleep, ctime

class CleanOutputSet(set):
	def __str__(self):
		return ', '.join(x for x in self)

lock = Lock()
loops = (randrange(2,5) for x in xrange(randrange(3,7)))
remaining = CleanOutputSet()

def loop(nsec):
	myname = currentThread().name
	with lock:      #对于Lock、RLock、Condition、semaphonre都包含上下文管理器的，可以使用with，例如LOCK会自动调用acquire()和release()
		remaining.add(myname)
		print '[%s] Started %s' % (ctime(),myname)
	sleep(nsec)
	with lock:
		remaining.remove(myname)
		print '[%s] Completed %s (%d secs)' % (ctime(), myname, nsec)
		print '   (remaining: %s)' % (remaining or 'NONE')

def _main():
	for pause in loops:
		Thread(target=loop, args=(pause,)).start()

@register
def _atexit():
	print 'all DONE at:', ctime()

if __name__ == '__main__':
	_main()

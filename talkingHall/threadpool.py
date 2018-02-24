#!/usr/bin/python
#coding:utf-8

import Queue
import threading


		
class PoolManage:
	def __init__(self,thread_num):
		self.thread_num = thread_num
		self.task_queue = Queue.Queue()
		self.threads = []
		self._threadpool_init()
		
	def _threadpool_init(self):
		for i in range(self.thread_num):
			self.threads.append(Work(self.task_queue))
	
	def word_add(self,func,*args):
		self.task_queue.put((func,args))
		
	def wait_allcomplete(self):
		for item in self.threads:
			if item.isAlive():item.join()
		return None
		
class Work(threading.Thread):
	def __init__(self,taskqueue):
		threading.Thread.__init__(self)
		self.TaskQueue = taskqueue
		self.daemon  = True
		self.start()
		
	def run(self):
		while True:
			func,args = self.TaskQueue.get()
			func(*args)
			self.TaskQueue.task_done()


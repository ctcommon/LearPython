#!/usr/bin/env python
#coding:utf-8

import socket
import select
import sys
import Queue
import threading,time
import threadpool
import signal
import traceback

reload(sys)

#global variable
userlist = []
roomdict = {}

class User:
	def __init__(self,skt,username='none'):
		self.skt = skt
		self.username = username
		self.room = None
	
	def send_msg(self,msg):
		self.skt.send(msg)
	
	def private_send(self,usrname,msg):
		user = None
		for usr in userlist:
			if usr.username == usrname:
				user = usr
				break
		if user != None:
			self.send_msg(msg)
			user.send_msg(msg)
			return True
		return False
	
	def logout_hall(self):
		self.skt.close()
		
	def exit_room(self,ID):  #未实现防止异常  然后是python的useradd重用  如何在强行关闭了服务器的时候能够将服务器断开连接 还有客户端的异常断开
		if self.room == None or self.room != roomdict[ID]:
			warn_mess = 'warning:you are not in %s room' %ID 
			self.send_msg(warn_mess)
		else:
			self.room.exit_room(self)
			self.room = None
			return True
		return False
			
	def create_room(self,ID): 
		if roomdict.has_key(ID):
			warn_mess = 'warning:someone has created %s room' %ID
			self.send_msg(warn_mess)
		else:
			room = Room(ID)
			roomdict.update({ID:room})
			return True
		return False
			
	def enter_room(self,ID):
		if not roomdict.has_key(ID):
			warn_mess = 'warning:nobody create %s room' %ID
			self.send_msg(warn_mess)
		elif self.room == roomdict[ID]:
			warn_mess = 'warning:you has already entered %s room' %ID
			self.send_msg(warn_mess)
		else:
			if self.room != None:
				self.exit_room()
			roomdict[ID].enter_room(self)
			self.room = roomdict[ID]
			return True
		return False
	
	def notice_hall(self,mess_):
		if len(userlist) != 0: 
			for usr in userlist:
				usr.send_msg(mess_)
			return True
		return False	
	def notice_room(self,mess_,ID): 
		if self.room != None and self.room == roomdict[ID]:
			self.room.notice_room(mess_)
			return True
		return False
		
class Room:
	def __init__(self,ID):
		self.ID = ID
		self.roomusers = []
		
	def notice_room(self,mess_):
		if len(self.roomusers) != 0:
			for usr in self.roomusers:
				usr.send_msg(mess_)
	
	def exit_room(self,usr):
		self.roomusers.remove(usr)
		
	def enter_room(self,usr):
		self.roomusers.append(usr)

		
def hand_user_conn(usr,data): 
		msg=data.split('|')
		if msg[0] == 'login':
			login_mess = "login|%s" %msg[1]
			usr.username = msg[1]   #此时此刻就决定了此连接的登陆者是谁，后面聊天都是基于连接，而连接的用户此时登录的时候已经确定
			if usr.notice_hall(login_mess):
				print 'user [%s] login' %msg[1]
		if msg[0] == 'talk':
			#事实上，这些所有的操作函数都应当返回True或False，通过状态来决定后续是否print
			talk_mess = "user[%s] said : %s" %(usr.username,msg[1])
			if usr.notice_hall(talk_mess):
				print talk_mess 
		if msg[0] == 'exit':
			exit_mess =  'user[%s] has already exit' %usr.usernames
			if usr.notice_hall(exit_mess)
				print exit_mess
				usr.logout_hall()
				userlist.remove(usr)  #离线的在userlist消去
		if msg[0] == 'createroom':
			create_mess = 'user[%s] create %s room' %(usr.username,msg[1])
			if usr.create_room(msg[1]):
				print create_mess
		if msg[0] == 'enterroom':
			enter_mess = 'user[%s] entered %s room' %(usr.username,msg[1])
			if usr.enter_room(msg[1]):
				print enter_mess
		if msg[0] == 'exitroom':
			exit_mess = 'user[%s] exited %s room' %(usr.username,msg[1])
			if usr.exit_room(msg[1]):
				print exit_mess
		if msg[0] == 'sendroom':
			talk_mess = "user[%s] said{} : %s" %(usr.username,msg[2])
			if usr.notice_room(talk_mess,msg[1]):
				print talk_mess.format(" to "+msg[1] + " room ")
		if msg[0] == 'privatemass':
			talk_mess = "user[%s] said{}: %s" %(usr.username,msg[2])
			if usr.private_send(msg[1],talk_mess):
				print talk_mess.format(" to "+msg[1] + " you ")
		



class handlersocket:
	def __init__(self,port,lenlisten):
		self.lenlisten = lenlisten
		self.port = port
		self.socket_bind_listen()
		self.make_socket_nonblock()
		
	def socket_bind_listen(self):
		if self.port <= 1024 or self.port >= 65535:
			self.port = 9999
		try:
			self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			self.socket.bind(('0.0.0.0',self.port))
			self.socket.listen(self.lenlisten)
		except:
			self.socket.close()
			traceback.print_exc()
			
	def make_socket_nonblock(self):
		self.socket.setblocking(False)
	
	def returnsocket(self):
		return self.socket
		
	def accept_connect(self):
		try:
			connect,address = self.socket.accept()
			connect.setblocking(False)
			return connect,address
		except:
			traceback.print_exc()
	
class epollhandlersocket:
	def __init__(self,PORT,lenlisten,pool):
		self.handlersocket = handlersocket(PORT,lenlisten)
		self.socket = self.handlersocket.returnsocket()
		self.epoll = select.epoll()
		self.epoll.register(self.socket.fileno(),select.EPOLLIN|select.EPOLLET)
		self.fd_to_socket = {self.socket.fileno():self.socket}
		self.fd_to_usr = {}
		self.pool = pool
		self.message_queues = {}
		print u'waiting for connection...'
		
	def epoll_wait(self):
		self._events = self.epoll.poll()
		
	def handler_event(self):
		for fd,event in self._events:
			socket = self.fd_to_socket[fd]
			if socket == self.socket:
				connect,address = self.handlersocket.accept_connect()
				user = User(connect)
				userlist.append(user)
				self.message_queues[connect] = Queue.Queue()
				self.fd_to_usr[connect.fileno()] = user
				self.epoll.register(connect.fileno(),select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
				self.fd_to_socket[connect.fileno()] = connect
			elif event&select.EPOLLHUP or event&select.EPOLLERR:
				self.epoll.unregister(fd)
				usr = fd_to_usr[fd]
				usr.logout_hall()
				userlist.remove(usr)
				del self.fd_to_socket[fd]
			elif  event&select.EPOLLIN:
				data = socket.recv(1024)
				if data:
					self.message_queues[socket].put(data)
					self.epoll.modify(fd,select.EPOLLOUT|select.EPOLLET|select.EPOLLONESHOT)
			elif event&select.EPOLLOUT:
				try:
					data = self.message_queues[socket].get_nowait()
				except Queue.Empty:
					self.epoll.modify(fd,select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
				else:
					usr = self.fd_to_usr[fd]
					self.pool.word_add(hand_user_conn,usr,data)
					self.epoll.modify(fd,select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
					
def main():
	signal.signal(signal.SIGPIPE, signal.SIG_IGN)
	pool = threadpool.PoolManage(4)
	handlersocket = epollhandlersocket(9999,10,pool)
	while True:
		handlersocket.epoll_wait()
		handlersocket.handler_event()
	handlersocket.socket.close()

if __name__ == '__main__':
	main()
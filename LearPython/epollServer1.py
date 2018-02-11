#!/usr/bin/env python
#coding:utf-8

import socket
import select
import Queue
import sys
import struct
import threading,time
import threadpool
import signal
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')

#global variable
userlist = []
roomdict = {}
userpwddict = {}

class User:
	def __init__(self,skt,username = None):
		self.skt = skt
		self.username = username
		self.room = None
	
	def send_message(self,msg):
		self.skt.send(msg)
	
	def private_send(self,user,msg):
		self.send_message(msg)
		user.send_message(msg)
	
	def logout_hall(self):
		self.skt.close()
		
	def exit_room(self,ID):  
		self.room.exit_room(self)
		self.room = None
			
	def create_room(self,ID):
		room = Room(ID)
		roomdict.update({ID:room})
			
	def enter_room(self,ID):
		if self.room != None:
			self.exit_room()
		roomdict[ID].enter_room(self)
		self.room = roomdict[ID]
	
	def notice_hall(self,mess_):
		for usr in userlist:
			usr.send_message(mess_)

	def notice_room(self,mess_,ID): 
		self.room.notice_room(mess_)
		
class Room:
	def __init__(self,ID):
		self.ID = ID
		self.roomusers = []
		
	def notice_room(self,mess_):
		if len(self.roomusers) != 0:
			for usr in self.roomusers:
				usr.send_message(mess_)
	
	def exit_room(self,usr):
		self.roomusers.remove(usr)
		
	def enter_room(self,usr):
		self.roomusers.append(usr)


def sendMessage(headcmd,datamess):
	send_data = str(headcmd)+struct.pack('<I',len(datamess.encode('utf-8')))+datamess
	return send_data

#服务端要发送的反馈
sendmessagedict = {}
#登录操作的反馈
sendmessagedict['01'] = u'用户登录成功'
sendmessagedict['02'] = u'密码错误'
sendmessagedict['03'] = u'用户已在线'
sendmessagedict['04'] = u'用户未注册'
sendmessagedict['05'] = u'用户名不合法，必须为数字(不能为开头)、字母、下划线'        #这个只需在客户端验证有效性即可
#注册操作的反馈
sendmessagedict['11'] = u'注册成功,请登录'
sendmessagedict['12'] = u'用户名已被注册'
sendmessagedict['13'] = u'用户名不合法，必须为数字(不能为开头)、字母、下划线'        #这个只需在客户端验证有效性即可
##################################################################################################################################
#以下必须是在登录成功后才能继续做的操作
#创建房间的反馈
sendmessagedict['21'] = u'创建房间成功'                                              #此时群发某用户创建了某房间
sendmessagedict['22'] = u'房间已被创建'
sendmessagedict['23'] = u'房间名不合法，必须为数字(不能为开头)、字母、下划线'        #这个只需在客户端验证有效性即可
#发消息的反馈
sendmessagedict['31'] = None                                                              #群发消息，value来自客户端传送过来的数据
sendmessagedict['32'] = None                                                               #群发在房间显示的消息成功，value来自客户端传送过来的数据
sendmessagedict['33'] = u'你并不在房间内' #群发房间消息失败
sendmessagedict['34'] = None                                                              #私聊消息成功，这个value为客户端要发送给某用户的消息
sendmessagedict['35'] = u'该用户并不在线'
#请求查询的消息
sendmessagedict['41'] = None                                                                #请求查询自己所在的房间名，成功则value为自己所在的房间
sendmessagedict['42'] = sendmessagedict['33']
sendmessagedict['43'] = None                                                               #请求查看已经被创建的房间名，成功则value为以|隔开的房间名
sendmessagedict['44'] = u'还没有任何房间被创建'
sendmessagedict['45'] = None                                                               #请求查看在线人数，最低限度为看到自己的名字显示。
#进入房间操作的反馈
sendmessagedict['51'] = None                                                          #成功，会在房间内告示该玩家已进入了房间
sendmessagedict['52'] = u'该房间还未被创建'
sendmessagedict['53'] = u'你早已经在此房间内'
#退出房间操作的反馈
sendmessagedict['61'] = None                                                         #成功，会在房间内告示该玩家已退出了房间
sendmessagedict['62'] = sendmessagedict['33']

def hand_user_conn(usr,headcmd,data): #21点游戏还没有做 其实无论什么行为，到了客户端那边只要显示数据就行，不用分析命令标识？
	global sendmessagedict
	global roomdict
	global userlist
	msg = [None,None]
	if headcmd == '01': #注册用户
		index = data.find('|')
		msg[0] = data[:index]
		msg[1] = data[index+1:]
		cmd = None
		if userpwddict.has_key(msg[0]):
			cmd = '12'  #用户已注册
		else:
			userpwddict[msg[0]] = msg[1]
			cmd = '11'  #注册成功
			print u'%s 注册成功，密码为：%s !' %(msg[0],msg[1])
		if cmd != None:
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)

	if headcmd == '02': #登录用户
		index = data.find('|')
		msg[0] = data[:index]
		msg[1] = data[index+1:]
		cmd = None
		ingusername=False
		for i in userlist:
			if msg[0] == i.username:
				ingusername = True
				break
		if not userpwddict.has_key(msg[0]):
			cmd = '04'  #用户未注册
		elif ingusername == True:
			cmd = '03'  #用户已在线
		elif msg[1] != userpwddict[msg[0]]:
			cmd = '02'  #密码错误
		else:
			cmd = '01' #登录成功
			sendmessagedict[cmd] = u'%s 用户上线了' %msg[0]
			usr.username = msg[0]
			userlist.append(usr)
			print u'%s 登录成功，密码为：%s !' %(msg[0],msg[1])
		if cmd != None:
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			if cmd == '01': #成功则群发告示
				usr.notice_hall(alldata)
			else:#否则就告诉该用户失败信息
				usr.send_message(alldata)

	if headcmd == '03': #创建房间
		if roomdict.has_key(data):
			cmd = '22' #房间已经被注册
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else:
			usr.create_room(data)
			cmd = '21' #房间创建成功
			print u'%s 创建了房间 %s !' %(usr.username,data)
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.notice_hall(alldata)

	if headcmd == '04': #进入房间
		if not roomdict.has_key(data):
			cmd = '52' #该房间未被创建
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		elif usr.room == roomdict[data]:
			cmd = '53' #原本就在此房间内
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #进入房间成功
			usr.enter_room(data)
			cmd = '51'
			print u'%s 进入了房间 %s !' %(usr.username,data)
			sendmessagedict[cmd] = '%s 进入了此房间' %usr.username
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.notice_room(alldata)

	if headcmd == '05': #退出房间
		if usr.room == None:
			cmd = '62'
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #退出房间成功
			usr.exit_room(usr.room.ID)
			cmd = '61'
			print u'%s 退出了房间 %s !' %(usr.username,usr.room.ID)
			sendmessagedict[cmd] = u'%s 退出了此房间' %usr.username
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.notice_room(alldata)
			
	if headcmd == '11': #群发消息
		cmd = '31'
		sendmessagedict[cmd] = u'%s 说：%s ' %(usr.username,data)
		alldata = sendMessage(cmd,sendmessagedict[cmd])
		print '%s 群发消息 %s' %(usr.username,data)
		usr.notice_hall(alldata)

	if headcmd == '12': #基于房间的群发消息
		if usr.room == None:
			cmd = '33'
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #基于房间的群发消息成功
			cmd = '32'
			sendmessagedict[cmd] = u'%s 说：%s ' %(usr.username,data)
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			print '%s 在房间 %s 内说：%s ' %(usr.username,usr.room.ID,data)
			usr.notice_room(alldata)

	if headcmd == '13': #私聊
		index = data.find('|')
		msg[0] = data[:index]
		msg[1] = data[index+1:]
		dstuser = None
		for user in userlist:
			if user.username == msg[0]:
				dstuser = user
				break
		if dstuser == None: #不在线
			cmd = '35'
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #在线
			cmd = '34'
			sendmessagedict[cmd] = u'%s 说：%s'  %(usr.username,msg[1])
			alldata = sendMessage(cmd,sendmessagedict[cmd])
			usr.private_send(dstuser,alldata)

	if headcmd == '20': #查看自己所在的房间
		if usr.room == None:
			cmd = '42'
		else:
			cmd = '41'
			sendmessagedict[cmd] = u'您所在的房间为：%s ' %usr.room.ID
		alldata = sendMessage(cmd,sendmessagedict[cmd])
		usr.send_message(alldata)

	if headcmd == '21': #请求查看已创建的房间
		roomsname = ''
		for k in roomdict.keys():
			roomsname += roomdict[k].ID + ' |'
		if roomname == '':
			cmd = '43'
		else:
			cmd = '42'
			sendmessagedict[cmd] = roomsname[:-1]
		alldata = sendMessage(cmd,sendmessagedict[cmd])
		usr.send_message(alldata)
	if headcmd == '22': #请求查看总的在线的用户
		username = ''
		for u in userlist:
			username += u.username + ' |'
		cmd = '44'
		sendmessagedict[cmd] = username[:-1]
		alldata = sendMessage(cmd,sendmessagedict[cmd])
		usr.send_message(alldata)

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
			exit(1)
			
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

class DealMessage:
	def __init__(self):
		self.alldata_buffer = ''                     #该套接字接收缓冲区
		self.oncedata_buffer = ''                    #用于保存该连接一次完整的数据(不包括头部分)
		self.flag = False                            #头部分是否已被处理
		self.head_str=''                             #头部两个字节，也就是命令标识
		self.data_body_len = 0                       #一次完整的数据部分的长度
		self.recive_len = 0                            #数据部分已经接收到的长度


	def recvMessage(self,sock):
		tmp_buffer = sock.recv(1024)
		self.alldata_buffer += tmp_buffer

		if not tmp_buffer:
			return None

		while True:
			if self.flag:  #头部已被处理
				need_len = self.data_body_len - self.recive_len
				if len(self.alldata_buffer) < need_len:
					self.recive_len += len(self.alldata_buffer)
					self.oncedata_buffer += self.alldata_buffer
					self.alldata_buffer = ''
					break
				else:
					self.oncedata_buffer += self.alldata_buffer[0:need_len]
					self.alldata_buffer = self.alldata_buffer[need_len:]
					head_str = self.head_str[:]
					data_mess = self.oncedata_buffer[:]
					self.oncedata_buffer = ''
					self.recive_len = 0
					self.head_str = ''
					self.data_body_len = 0
					self.flag = False
					return head_str, data_mess
			else:   #头部未被处理
				datalen = len(self.alldata_buffer)
				#print datalen
				if datalen >= 6:
					self.head_str = self.alldata_buffer[0:2]
					self.data_body_len = (struct.unpack('<I',self.alldata_buffer[2:6]))[0]
					#print self.data_body_len
					self.flag = True
					self.alldata_buffer = self.alldata_buffer[6:]
					#print self.alldata_buffer
					self.recive_len = 0
					self.oncedata_buffer = ''
					if len(self.alldata_buffer) >= self.data_body_len:
							self.oncedata_buffer = self.alldata_buffer[:self.data_body_len]
							#print self.oncedata_buffer
							self.alldata_buffer = self.alldata_buffer[self.data_body_len:]
							head_str = self.head_str[:]
							data_mess = self.oncedata_buffer[:]
							self.oncedata_buffer = ''
							self.recive_len = 0
							self.head_str = ''
							self.data_body_len = 0
							self.flag = False
							return head_str, data_mess
					else:
						break
				else:
					break

		return None





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
		self.sock_to_dealmessage = {}
		print u'waiting for connection...'
		
	def epoll_wait(self):
		self._events = self.epoll.poll()

	def epoll_handler(self,event,sock,fd):
		if event & select.EPOLLIN:
			#data = sock.recv(1024)
			alldata = self.sock_to_dealmessage[sock].recvMessage(sock)
			
			if alldata: #有数据，返回的为元组
				self.message_queues[sock].put(alldata)
				self.epoll.modify(fd,select.EPOLLOUT|select.EPOLLET|select.EPOLLONESHOT)
		elif event & select.EPOLLOUT:
				try:
					alldata = self.message_queues[sock].get_nowait()
				except Queue.Empty:
					try:
						self.epoll.modify(fd,select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
					except:
						pass
				else:
					usr = self.fd_to_usr[fd]
					hand_user_conn(usr,alldata[0],alldata[1]) #元组下标0为命令标识，下标1为具体数据
					try:
						self.epoll.modify(fd,select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
					except:
						pass

	def handler_event(self):
		for fd,event in self._events:
			socket = self.fd_to_socket[fd]
			if socket == self.socket:
				connect,addr = self.handlersocket.accept_connect()
				self.sock_to_dealmessage[connect] = DealMessage()
				user = User(connect)
				self.message_queues[connect] = Queue.Queue()
				self.fd_to_usr[connect.fileno()] = user  
				self.epoll.register(connect.fileno(),select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
				self.fd_to_socket[connect.fileno()] = connect
			elif event & select.EPOLLHUP or event & select.EPOLLERR:
				self.epoll.unregister(fd)
				usr = fd_to_usr[fd]
				userlist.remove(usr)
				del self.fd_to_socket[fd]
				del self.sock_to_dealmessage[socket]
				del self.message_queues[socket]
				del self.fd_to_usr[fd]
				cmd = '00'
				alldata = sendMessage(cmd,u'%s 用户下线了' %usr.username)
				usr.logout_hall(alldata)
			else:
				self.pool.word_add(self.epoll_handler,event,socket,fd)

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

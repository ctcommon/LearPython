#!/usr/bin/env python
#coding:utf-8

import random
import socket
import select
import Queue
import sys
import struct
import threading,time
import datetime
import threadpool
import signal
import traceback
import DealMessage

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
		self.OnTime = 0
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
			self.exit_room(ID)
		roomdict[ID].enter_room(self)
		self.room = roomdict[ID]
	
	def notice_hall(self,mess_):
		for usr in userlist:
			usr.send_message(mess_)

	def notice_room(self,mess_):
		if self.room: 
			self.room.notice_room(mess_)
	
	def initOnTime(self,path):
		f = open(path,'a')
		f.write(self.username + '|0\n')
		f.close()
	def startOnLine(self):
		self.OnTime = datetime.datetime.now()
	def LogOnTime(self,path):
		total_time = (datetime.datetime.now() - self.OnTime).seconds
		print '%s this time online: %d'%(self.username,total_time)
		f = open(path,'r')
		index = 0
		lines = f.readlines()
		for line in lines:
			if self.username == line[0:line.find('|')]:
				total_time += eval(line[line.find('|')+1:])
				upmess = self.username + '|' + str(total_time) + '\n'
				lines[index] = upmess
				break
			index += 1
		f.close()
		f = open(path,'w')
		for line in lines:
			f.write(line)
		f.close() 	
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



#服务端要发送的反馈
sendmessagedict = {}
#登录操作的反馈
sendmessagedict['01'] = u'用户登录成功'
sendmessagedict['02'] = u'密码错误'
sendmessagedict['03'] = u'用户已在线'
sendmessagedict['04'] = u'用户未注册'
sendmessagedict['05'] = u'用户名不合法，必须为数字(不能为开头)、字母、下划线'        #这个只需在客户端验证有效性即可
sendmessagedict['06'] = None  #这个用于登录成功时更新所有在线成员gui的在线成员列表
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

path = r'online_time.txt'
game_num = {}
room_answer = {}
answer_valid = {}
def hand_user_conn(usr,headcmd,data): #21点游戏还没有做 其实无论什么行为，到了客户端那边只要显示数据就行，不用分析命令标识？
	global sendmessagedict
	global roomdict
	global userlist
	global path
	global pool
	global game_num
	global room_answer
	global answer_valid
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
			usr.username = msg[0]
			usr.initOnTime(path)
			print u'%s 注册成功，密码为：%s !' %(msg[0],msg[1])
		if cmd != None:
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
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
			usr.startOnLine()
			cmd = '01' #登录成功
			sendmessagedict[cmd] = u'%s 用户上线了' %msg[0]
			usr.username = msg[0]
			#userlist.append(usr)
			print u'%s 登录成功，密码为：%s !' %(msg[0],msg[1])
			alldata = DealMessage.sendMessage(cmd,usr.username)
			usr.send_message(alldata)
			alldata = DealMessage.sendMessage('06',msg[0])
			usr.notice_hall(alldata)
			time.sleep(0.5)
			userlist.append(usr)
			username = ''
			for u in userlist:
				username += u.username + '|'
			sendmess = username[:-1]
			alldata = DealMessage.sendMessage('44',sendmess)
			usr.send_message(alldata)
			time.sleep(0.5)
			roomname = ''
			for r in roomdict.keys():
				roomname += roomdict[r].ID+'|'
			sendmess = roomname[:-1]
			alldata = DealMessage.sendMessage('43',sendmess)
			usr.send_message(alldata)
		if cmd != None and cmd != '01':
			#否则就告诉该用户失败信息
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)

	if headcmd == '03': #创建房间
		if roomdict.has_key(data):#need deal
			cmd = '22' #房间已经被注册
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else:
			usr.create_room(data)
			cmd = '21' #房间创建成功
			print u'%s 创建了房间 %s !' %(usr.username,data)
			alldata = DealMessage.sendMessage(cmd,data)
			usr.notice_hall(alldata)
			answer_valid[data] = False
			#send 21game mess every 30 seconds
			def game(usr):
				while True:
					while int(datetime.datetime.now().second) % 45 != 0:
						time.sleep(1)
					if usr.room:
						ps_mess = '21 games is beginning...(answer use the following four number within 20 senconds)\n'
						game_num[usr.room.ID] = [None,None,None,None]
						for i in range(len(game_num[usr.room.ID])):
							game_num[usr.room.ID][i] = str(random.randint(1,10))
							ps_mess += game_num[usr.room.ID][i]+ ' '
						alldata = DealMessage.sendMessage('32','%s|%s: %s\n' %(usr.room.ID,'system',ps_mess))
						usr.notice_room(alldata)
						answer_valid[usr.room.ID] = True
						time.sleep(20)
						if usr.room:
							answer_valid[usr.room.ID] = False
							if room_answer[usr.room.ID] != []:
								send_mess = 'winner is ' + room_answer[usr.room.ID][0]+'\n'
								alldata = DealMessage.sendMessage('32','%s|%s: %s' %(usr.room.ID,'system',send_mess))
								usr.notice_room(alldata)
							else:
								send_mess = 'nobody win'
								alldata = DealMessage.sendMessage('32','%s|%s: %s' %(usr.room.ID,'system',send_mess))
								usr.notice_room(alldata)
							room_answer[usr.room.ID] = []
							game_num[usr.room.ID] = []
			pool.word_add(game,usr)
	
	if headcmd == '70':
		if answer_valid[usr.room.ID] == False: #need deal
			return 
		valid_oper = ['+','-','*','/','(',')']
		numlist = []
		tmp = ''
		for ch in data:
			if ch not in valid_oper:
				tmp += ch
			else:
				if tmp != '':
					numlist.append(tmp)
					tmp = ''
		if tmp != '':
			numlist.append(tmp)
		
		if set(numlist) != set(game_num[usr.room.ID]):
			return
		try:
			eval(data)
		except:
			return
		res = eval(data)
		if res > 21:
			return
		if room_answer[usr.room.ID] == []:
			room_answer[usr.room.ID] = [usr.username,res]
		elif room_answer[usr.room.ID][1] < res:
			room_answer[usr.room.ID] = [usr.username,res]
			


	if headcmd == '04': #进入房间
		if not roomdict.has_key(data):
			cmd = '52' #该房间未被创建
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		elif usr.room == roomdict[data]:
			cmd = '53' #原本就在此房间内
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #进入房间成功
			usr.enter_room(data)
			room_answer[usr.room.ID] = []
			cmd = '51'
			print u'%s 进入了房间 %s !' %(usr.username,data)
			sendmessagedict[cmd] = '%s 进入了此房间' %usr.username
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.notice_room(alldata)

	if headcmd == '05': #退出房间 need deal
		if usr.room == None:
			cmd = '62'
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #退出房间成功
			print u'%s 退出了房间 %s !' %(usr.username,usr.room.ID)
			usr.exit_room(usr.room.ID)
			
	if headcmd == '11': #群发消息
		cmd = '31'
		sendmessagedict[cmd] = u'%s： %s\n' %(usr.username,data)
		alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
		print '%s 群发消息 %s' %(usr.username,data)
		usr.notice_hall(alldata)

	if headcmd == '12': #基于房间的群发消息
		if usr.room == None:
			cmd = '33'
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			usr.send_message(alldata)
		else: #基于房间的群发消息成功
			cmd = '32'
			sendmessagedict[cmd] = u'%s|%s： %s\n' %(usr.room.ID,usr.username,data)
			alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
			print '%s 在房间 %s 内说：%s ' %(usr.username,usr.room.ID,data)
			usr.notice_room(alldata)

	if headcmd == '13': #私聊
		index = data.find('|')
		msg[0] = data[:index] #私聊对象
		print msg[0]
		msg[1] = data[index+1:] #私聊消息
		cmd = '13'
		sendmessagedict[cmd] = u'%s|%s：%s\n'  %(usr.username,usr.username,msg[1])
		alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
		print len(userlist)
		for usr in userlist:
			print usr.username
			if usr.username == msg[0].strip():
				usr.send_message(alldata)
				break

	if headcmd == '21': #请求查看已创建的房间
		roomsname = ''
		for k in roomdict.keys():
			roomsname += roomdict[k].ID + '|'
		if roomname == '':
			cmd = '43'
		else:
			cmd = '42'
			sendmessagedict[cmd] = roomsname[:-1]
		alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
		usr.send_message(alldata)
	if headcmd == '22': #请求查看总的在线的用户
		username = ''
		for u in userlist:
			username += u.username + '|'
		cmd = '44'
		sendmessagedict[cmd] = username[:-1]
		alldata = DealMessage.sendMessage(cmd,sendmessagedict[cmd])
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
			
			if not alldata:
				self.epoll.unregister(fd)
				usr = self.fd_to_usr[fd]
				usr.LogOnTime(path)
				userlist.remove(usr)
				del self.fd_to_socket[fd]
				del self.sock_to_dealmessage[sock]
				del self.message_queues[sock]
				del self.fd_to_usr[fd]
				cmd = '00'
				alldata = DealMessage.sendMessage(cmd,usr.username)
				usr.notice_hall(alldata)
				usr.logout_hall()
			elif alldata: #有数据，返回的为元组
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
				self.sock_to_dealmessage[connect] = DealMessage.DealMessage()
				user = User(connect)
				self.message_queues[connect] = Queue.Queue()
				self.fd_to_usr[connect.fileno()] = user  
				self.epoll.register(connect.fileno(),select.EPOLLIN|select.EPOLLET|select.EPOLLONESHOT)
				self.fd_to_socket[connect.fileno()] = connect
			elif event & select.EPOLLHUP or event & select.EPOLLERR:
				self.epoll.unregister(fd)
				usr = fd_to_usr[fd]
				usr.LogOnTime(path)
				userlist.remove(usr)
				del self.fd_to_socket[fd]
				del self.sock_to_dealmessage[socket]
				del self.message_queues[socket]
				del self.fd_to_usr[fd]
				cmd = '00'
				alldata = DealMessage.sendMessage(cmd,usr.username)
				usr.notice_hall(alldata)
				usr.logout_hall()
			else:
				self.pool.word_add(self.epoll_handler,event,socket,fd)

def initOnTime():
	global path
	global userpwddict
	userpwddict = {'netease1':'123','netease2':'123','netease3':'123','netease4':'123'}
	f = open(path,'w')
	for k in userpwddict.keys():
		f.write(k+'|0\n')
	f.close()
pool = threadpool.PoolManage(10)
def main():
	initOnTime()
	signal.signal(signal.SIGPIPE, signal.SIG_IGN)
	#pool = threadpool.PoolManage(10)
	handlersocket = epollhandlersocket(9999,10,pool)
	while True:
		handlersocket.epoll_wait()
		handlersocket.handler_event()	
	handlersocket.socket.close()

if __name__ == '__main__':
	main()


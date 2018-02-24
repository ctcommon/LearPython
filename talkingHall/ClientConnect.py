#!/usr/env/bin python
#coding:utf-8


import socket
import Tkinter
import time
import threading
import ClientGui
import DealMessage

class ClientConnect:
	def __init__(self,IP,PORT,C):
		self.IP = IP
		self.PORT = PORT
		self.client = C
		self.s = None
		self.deal = DealMessage.DealMessage()
			
	def dealrecvmess(self,headcmd,datamess):
		self.client.stop_flag = headcmd
		print headcmd+'\n'  
		if headcmd == '31':  # 大厅消息
			self.client.main_app.datingtext.insert(Tkinter.END, datamess)
		if headcmd == '32':  # 房间消息  这里需要处理，每个客户应当保存自己所在的房间信息，或者在服务端写进房间信息
			index = datamess.find('|')
			room_name = datamess[0:index]  # 得到房间名称
			print room_name
			datamess = datamess[index + 1:]
			print 'name mess'+datamess
			if room_name in self.client.room_app:
				self.client.room_app[room_name].main_text.insert(Tkinter.END, datamess)
		if headcmd == '13': # 私人消息
			index = datamess.find('|')
			per_name = datamess[0:index].strip() # 得到用户名称
			print per_name
			datamess = datamess[index + 1:]
			if self.client.person_app.has_key(per_name): # 已经有私聊窗口
				print 'hasname' + ' '+per_name
				self.client.person_app[per_name].main_text.insert(Tkinter.END, datamess)
			else:
				print 'noname' +' '+per_name
				self.client.main_app.new_person = per_name
				self.client.main_app.after_idle(self.client.main_app.create_new_person)
				time.sleep(1)
				self.client.person_app[per_name].main_text.insert(Tkinter.END, datamess)
		if headcmd == '44': #所有上线用户
			on_user = datamess.split('|')
			for u in on_user:
				if u != '':
					self.client.main_app.all_player.insert(Tkinter.END,u)
		if headcmd == '43': #所有房间
			on_room = datamess.split('|')
			for u in on_room:
				if u != '':
					self.client.main_app.allroom.insert(Tkinter.END,u)
		if headcmd == '21': # 创建新房间
			self.client.main_app.allroom.insert(Tkinter.END, datamess)
		if headcmd == '06':  # 用户登录
			print datamess
			self.client.main_app.all_player.insert(Tkinter.END, datamess)
		if headcmd == '00':  # 用户退出
			for i in range(self.client.main_app.all_player.size()):  # 删除退出用户
				if self.client.main_app.all_player.get(i) == datamess:
					print self.client.main_app.all_player.get(i)
					self.client.main_app.all_player.delete(i)
					break
			
	def lis(self,s):
		while 	True:
			data =self.deal.recvMessage(s)
			if not data:
				break
			elif	data:
				print data
				self.dealrecvmess(data[0],data[1])
						
	def connection(self):
		if self.s:
			return 
		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect((self.IP,self.PORT))
		except:
			raise
		self.s = s
		self.t = threading.Thread(target=self.lis,args=(s,))
		self.t.setDaemon(True)
		self.t.start()
			
	def send_mess(self,headcmd,datamess):
		send_data = DealMessage.sendMessage(headcmd,datamess)
		self.s.send(send_data)
	def CloseConnection(self):
		if self.s:
			self.s.shutdown(True)

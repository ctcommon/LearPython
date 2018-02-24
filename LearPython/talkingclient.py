#!/usr/env/bin python
#coding:utf-8

import sys
import struct
import socket
import threading,time

reload(sys)
sys.setdefaultencoding('utf-8')

def sendMessage(headcmd,datamess):
	send_data = str(headcmd)+struct.pack('<I',len(datamess.encode('utf-8'))) + datamess
	return send_data

#global variable
isNormal=True
other_usr=''

def recieve_msg(senddata,s):
	global isNormal,other_usr
	#print 'Please waiting other user login...'
	headcmd = senddata[0]
	datamess = senddata[1]
	#s.send('login|%s' %username)
	send_data = sendMessage(headcmd,datamess)
	#print send_data
	s.send(send_data)
	while(isNormal):
		data = s.recv(1024)
		msg = data.split('|')
		if msg[0] == 'login':
			print u'user[%s]  has already logged in,start to chat' %msg[1]
			other_usr = msg[1]
		else:
			print msg[0]

def NameValue(name): #用户名和密码都至少为6位
	if len(name) >= 6:
		for i in name:
			if not (i.isalnum() or i == '_'):
				return False
		return True
	return False

guidstr = u'请登录或注册  01:注册用户 02:用户登录  q*:退出进程  按下其他键无效'
Flag = False
def regisOrsign():
	global Flag
	str = ''
	while True:
		print guidstr
		cmd = raw_input()
		if cmd == '01':
			while True:
				print u'q*:停止此次注册'
				username = raw_input(u'请输入你的用户名：')
				if username == 'q*':
					break
				elif not NameValue(username):
					print u'用户名无效，只能为数字、字母和下划线'
					continue
				else:
					print u'q*:停止此次注册'
					pwd = raw_input(u'请输入你的密码,至少6位数:')
					if pwd == 'q*':
						break
					str += username+'|'+pwd
					return '01',str
		elif cmd == '02':
			while True: #和01打代码一样，可以提取出来重复调用
				print u'q*:停止此次登录'
				username = raw_input(u'请输入你的用户名：')
				if username == 'q*':
					break
				elif not NameValue(username):
					print u'用户名无效，只能为数字、字母和下划线'
					continue
				else:
					print u'q*:停止此次登录'
					pwd = raw_input(u'请输入你的密码，至少为6位数：')
					if pwd == 'q*':
						break
					str += username+'|'+pwd
					Flag = True
					return '02',str
		elif cmd == 'q*':
			exit(1)
		else:
			print u'输入无效'
			contine
			

def main():
	global isNormal,other_usr
	try:
		print 'please input your name:'
		userpwd = regisOrsign() 
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(("127.0.0.1",9999))
		t = threading.Thread(target = recieve_msg,args=(userpwd,s))
		t.start()
	except:
		print 'connection excepttion'
		isNormal = False
	finally:
		pass
	while isNormal:
		#if not Flag:
		userpwd = regisOrsign()
		senddata = sendMessage(userpwd[0],userpwd[1])
	#	else:
		#	senddata == 'q'
		s.send(senddata)
	try:			
		s.close()
	except:
		pass
	
if __name__ == '__main__':
	main()

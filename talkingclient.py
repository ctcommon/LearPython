#!/usr/env/bin python
#coding:utf-8


import sys
import socket
import threading,time

reload(sys)

#global variable
isNormal=True
other_usr=''

def recieve_msg(username,s):
	global isNormal,other_usr
	#print 'Please waiting other user login...'
	s.send('login|%s' %username)
	while(isNormal):
		data = s.recv(1024)
		msg = data.split('|')
		if msg[0] == 'login':
			print u'user[%s]  has already logged in,start to chat' %msg[1]
			other_usr = msg[1]
		else:
			print msg[0]
			
def main():
	global isNormal,other_usr
	try:
		print 'please input your name:'
		usrname = raw_input()
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(("127.0.0.1",9999))
		t = threading.Thread(target = recieve_msg,args=(usrname,s))
		t.start()
	except:
		print 'connection excepttion'
		isNormal = False
	finally:
		pass
	while isNormal:
		msg=raw_input()
		if msg=="exit":
			isNormal = False
		s.send(msg)
				
	s.close()
	
if __name__ == '__main__':
	main()
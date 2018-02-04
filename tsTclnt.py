from socket import *

PORT = 21567
BUFSIZ = 1024

tcpCliSock = socket(AF_INET,SOCK_STREAM)
tcpCliSock.connect(('127.0.0.1'),PORT)

while True:
	data = raw_input('> ')
	if not data:
		break
	tcpCliSock.send(data)
	data = tcpCliSock.recv(BUFSIZ)
	if not data:
		break
	print data
tcpCliSock.close()

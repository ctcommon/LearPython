from socket import *
from time import ctime

PORT = 21567
BUFSIZ = 1024

tcpSerSock = socket(AF_INET,SOCK_STREAM)
tcpSerSock.bind(('127.0.0.1',PORT))
tcpSerSock.listen(5)

while True:
	print 'waiting for connection...'
	tcpCliSock, addr = tcpSerSock.accept()
	print '...connected from:',addr

	while True:
		data = tcpCliSock.recv(BUFSIZ)
		if not data:
			break
		tcpCliSock.send('[%s] %s' %(ctime(),data))
	tcpCliSock.close()
tcpSerSock.close()

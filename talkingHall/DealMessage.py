#!/usr/bin/python
#coding:utf-8



#when client want to quit,press 'quit',and add '00' do cmd makepackage send to cserver
#except quit need do something make strong 
import sys
import struct

reload(sys)
sys.setdefaultencoding('utf-8')





def sendMessage(headcmd,datamess):
		send_data = str(headcmd)+struct.pack('<I',len(datamess.encode('utf-8')))+datamess
		return send_data


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
			#need deal
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

#!/usr/bin/env python
#coding:utf-8
'''
栈类：
1、用于判定是列表的时候，将'{'和'}'变为'['和']'
2、转换为字典的时候借助栈让列表里的nil变为none
3、为没有key的字典增加数字key，都需要用到栈
'''
class Stack:
	def __init__(self):
		self._array = []
		
	def pop(self):
		self._array.pop()
		
	def push(self, item):
		self._array.append(item)
		
	def top(self):
		return self._array[-1]
	
	def clear(self):
		self._array = []
	def empty(self):
		return self._array == []
		
class ParerError(Exception):
    pass
	
class PyLuaTblParser(object):
	def __init__(self,str=''):
		if  len(str)!=0 and not isinstance(str,basestring):
			raise ParerError("string error")
		self._spec_stop = [',','{','}',';','=','[',']']
		self._spec_hash = {r'\a': '\a', r'\b': '\b', r'\f': '\f', r'\n': '\n',
                         r'\r': '\r', r'\t': '\t', r'\v': '\v', r'\\': '\\',
                         r'\'': '\'',r'\"': '\"', r'\[': '[', r'\]': ']'}
		self._rever_spec_hash = dict((v, k) for k, v in self._spec_hash.iteritems())
		self._str = str
		self._pos = 0
		self._ch = None
		self._dict_list_str = []
		self._list_str = []
		self._new_list_str = []
		self._lua_table_str = ''
		
	
	
	def _SkipSpace(self,str_,index,flag = 1): #忽略空格 
		if(flag == 1):
			while str_[index].isspace():
				index += 1
				if index >= len(str_):
					return index
		else:
			while str_[index].isspace():
				index -= 1
		return index
	
		   
		
	def _MakeWords(self,str,index,char='['):  #对'['和']'或'"'和'"'对里的字符作字符串
		tmp = char
		stop_flag = '"'
		if char == '[':
			index += 1
			index = self._SkipSpace(str,index)
			if str[index] != '"':
				stop_flag = ']'
			tmp += str[index]
		index += 1
		while True:
			if str[index] is None:
				raise ParerError("string error")
			elif str[index] == stop_flag:
				tmp += str[index]
				if char == '[':
					if stop_flag == '"':
						index += 1
						index = self._SkipSpace(str,index)
						tmp += str[index]
				break
			elif str[index] in '\'\"':
				tmp += str[index]
			elif str[index] == '\\' and index+1 < len(str): 
				spec = ('\\' + str[index+1])
				if self._spec_hash.has_key(spec):
					spec = self._spec_hash[spec]
				tmp += spec
				index += 1
			else:
				tmp += str[index]
			index += 1
		self._list_str.append(tmp)
		return index
	def _KeyIsValid(self,key):
		if len(key) !=0 :
			if not (key[0].isalpha() or key[0] == '_'):
				return False
			for i in key[1:]:
				if not (i.isalnum() or i == '_'):
					return False
			return True
		return False
	def _oper(self,str_): #_私有方法oper读取测试的字符串并将除','号外的字符串以及括号和等号进行列表分化
		char = self._NextValidChar(str_)
		if char == None:
			return self._list_str
		i = self._pos-1
		if len(str_)>0 and str_[i] != '{':
			raise ParerError("string error")
		i += 1
		self._list_str = ['{']
		while i < len(str_):
			self._pos = i
			char = self._NextValidChar(str_)
			i = self._pos-1
			if i >= len(str_):
				return self._list_str
			j = self._SkipSpace(str_,i-1,0)
			if (str_[i] == '[' and str_[j] != '=')or str_[i] == '"':
				i = self._MakeWords(str_,i,str_[i])
			elif str_[i] == ' ':
				i += 1
				continue
			else: #对其他类型的字符作字符串，以'='，','，'{'，'}'为标记
				tmp = ''
				def push_back(c = ','):
					if len(tmp) != 0 and (not tmp.isspace()):
						try : 
							int(tmp.strip())
							self._list_str.append(tmp.strip())
						except ValueError:
							try:
								float(tmp.strip())
								self._list_str.append(tmp.strip())
							except ValueError:
								self._list_str.append('"'+tmp.strip()+'"')
					if c != ',' and c != ';':
						self._list_str.append(c);
				while True:
					if i >= len(str_):
						break
					if str_[i] in self._spec_stop:
						push_back(str_[i])
						break
					else:
						tmp += str_[i]
					i+=1
			i+=1
		if self._list_str[-1] != '}':
			raise ParerError("string error")
		return self._list_str
		
	def _BrakcetKeyValid(self,key):
		if len(key) == 0:
			return '',False
		if key[-1] != ']':
			return '',False
		i = 1
		i = self._SkipSpace(key,i)  
		j = len(key)-1
		j = self._SkipSpace(key,j-1,0)
		tmp = key[i:j+1].strip()
		if key[i] != '"' and key[j] != '"':
			try : 
				int(tmp)
				return tmp,True
			except ValueError:
				try:
					float(tmp)
					self._list_str.append(tmp.strip())
					return tmp,True
				except ValueError:
					return '',False
		elif key[i] != '"' or key[j] != '"':
			return '',False
		else:
			return tmp,True
			
	
		
	def _TransListStr(self,list_str):
		self._new_list_str = []
		for i in range(len(list_str)):
			if i+1 < len(list_str) and list_str[i+1] == '=':
				tmp = ''
				if list_str[i][0] == '[':
					tmp,Flag = self._BrakcetKeyValid(list_str[i])
					if Flag:
						self._new_list_str.append(tmp)
					else:
						raise ParerError("string error")
				elif self._KeyIsValid(list_str[i]):
						self._new_list_str.append(list_str[i])
				else:
					raise ParerError("string error")
			else:
				ch = list_str[i]
				self._new_list_str.append(ch)
		return self._new_list_str
		

		
			
						
	def _NextChar(self,str_):
		if self._pos >= len(str_):
			self._ch = None
			return None
		self._ch = str_[self._pos]
		self._pos += 1
		return self._ch
		
		
	def _SkipInValidC(self,str_):
		char = self._NextChar(str_)
		while char is not None and char.isspace():
			char = self._NextChar(str_)
		if char is not None:
			self._pos -= 1
			 	
	def _KeyIsValid(self,key):
		key = key[1:len(key)-1]
		if len(key) !=0 :
			if not (key[0].isalpha() or key[0] == '_'):
				return False
			for i in key[1:]:
				if not (i.isalnum() or i == '_'):
					return False
			return True
		return False
		
	def _IsEqualC(self,str_,char):
		if self._ch and self._ch == char:
			self._NextChar(str_)
			self._ch = str_[self._pos]
			return True
		return False
	
	def _SkipComment(self,str_):
		if self._IsEqualC(str_,'-'):
			if self._IsEqualC(str_,'-'):
				if self._IsEqualC(str_,'['):
					bracket_num = 0
					while self._ch and self._IsEqualC(str_,'='):
						bracket_num+= 1
					if self._IsEqualC(str_,'['):
						self._SkipMutiNum(str_,bracket_num)
					else:
						self._SkipSingleNum(str_)
				else:
					self._SkipSingleNum(str_)
				return True
			else:
				self._pos -= 1
		else:
			return False
	
	def _NextValidChar(self,str_):
		self._SkipInValidC(str_)
		while self._SkipComment(str_):
			self._SkipInValidC(str_)
		return self._NextChar(str_)

		   
	def _SkipSingleNum(self,str_):
		char = self._NextChar(str_)
		while char and char!= '\n':
			char = self._NextChar(str_)
			
	def _OperBracketString(self,str_,endChar):
		ret_str = '"'
		mark = endChar
		while True:
			char = self._NextChar(str_)
			if char is None:
				raise ParerError('a string must end with \' or \"')
			elif char == mark:
				break
			elif char in '\'\"':
				ret_str += char
			elif char == '\\': 
				ret_str += '\\' + self._NextChar(str_)
			else:
				ret_str += char
		ret_str += '"'
		return ret_str
		
		
	def _SkipMutiNum(self,str_,num):
		char = self._NextChar(str_)
		while char is not None:
			if char in '\'\"':
				self._pos -= 1
				index,string = self._OperBracketString(str_,char)
			elif char == ']':
				next_char = self._NextChar(str_)
				count = num
				while next_char == '=' and count >0:
					count -=1
					self._NextChar(str_)
				if  (count == 0 and self._ch == ']') or next_char is None:
					return
				elif next_char == ']':
					continue
			char = self._NextChar(str_)

											
	
	#在是列表的时候，将'{'和'}'转换为'['和']'
	def _TransBracket(self,str):
		try:
			string_stack = Stack()
			index_stack = Stack()
			for i in range(len(str)):
				if str[i] == "{":
					string_stack.push(str[i])
					index_stack.push(i)
				elif str[i] == "=":
					string_stack.push(str[i])
				elif str[i] == "}":
					if string_stack.top() != "=":
						index = index_stack.top()
						if(index != 0):
							str[index]= "["
							str[i] = "]"
						index_stack.pop()
						string_stack.pop()
					else:
						while string_stack.top() != "{":
							string_stack.pop()
						string_stack.pop()
						index_stack.pop()
			return str
		except IndexError:
			raise ParerError("string error")
		
	#将列表里的nil转变为None
	def _TransNilToNone(self,list_str):
		try:
			new_list_str = []
			string_stack = Stack()
			i=0
			while i < len(list_str):
				if list_str[i] == '{' or list_str[i] == '[':
					string_stack.push(list_str[i])
					new_list_str.append(list_str[i])
				elif list_str[i] == '=':
					new_list_str.append('=')
				elif i+2 < len(list_str) and list_str[i+1] == '=' and list_str[i+2] == '"nil"':
					i = i+2
				elif list_str[i] == '"nil"' and i+1 < len(list_str) and list_str[i+1] != '=':
					if string_stack.top() == '[':
						new_list_str.append('None')
					else:
						new_list_str.append(list_str[i])
				elif list_str[i] == '"false"'and i+1 < len(list_str) and list_str[i+1] != '=':
					new_list_str.append('False')
				elif list_str[i] == '"true"'and i+1 < len(list_str) and list_str[i+1] != '=':
					new_list_str.append('True')
				elif list_str[i] == '}' or list_str[i] == ']':
					new_list_str.append(list_str[i])
					string_stack.pop()
				else:
					new_list_str.append(list_str[i])
				i += 1
			return new_list_str
		except IndexError:
			raise ParerError("string error")
		
	#为没有key的加上数字key，并且将nil忽略
	def _TransListToStr(self,str_):
		try:
			new_list_str = [str_[0]]
			string_stack = Stack()
			string_stack.push(str_[0])
			string_stack.push(1)
			i=1
			while i < len(str_):
				if type(string_stack.top()) == type(1):
					if(str_[i] == '"nil"'):
						key_val = string_stack.top()+1
						string_stack.pop()
						string_stack.push(key_val)
						i += 1
						continue
					elif (str_[i] != '}' and str_[i] != '=' and str_[i-1] != '=' 
						and i+1 < len(str_) and str_[i+1] != '='):
						new_list_str.append(str(string_stack.top()))
						key_val = string_stack.top()+1
						string_stack.pop()
						string_stack.push(key_val)
						new_list_str.append('=')
					
				if str_[i] == '{' or str_[i] == '[':
					string_stack.push(str_[i])
					if str_[i] == '{':
						string_stack.push(1)
				elif str_[i] == '}' or str_[i] == ']':
					if str_[i] == '}':
						string_stack.pop()
					string_stack.pop()
				new_list_str.append(str_[i])
				i += 1
			return new_list_str
		except IndexError:
			raise ParerError("string error")
			
	def _Transstr(self,string):
		string_hash = {'False':False,'True':True,'None':None}
		if string_hash.has_key(string):
			return string_hash[string]
		else:
			try : 
				int(string)
				return int(string)
			except ValueError:
				try:
					float(string)
					return float(string)
				except ValueError:
					return string[1:len(string)-1]
					
	def _MakeList(self,index,_str):
		string_stack = Stack()
		while index < len(_str):
			if _str[index] == '{':
				index , dict_ = self._TransToDict(index,_str)
				string_stack.top().append(dict_)
			elif _str[index] == '[':
				string_stack.push(_str[index])
				string_stack.push([])
			elif _str[index] == ']':
					tmp_ = string_stack.top()
					string_stack.pop()
					string_stack.pop()
					if string_stack.empty():
						return index,tmp_
					string_stack.top().append(tmp_)
			else:
				string_stack.top().append(self._Transstr(_str[index]))
			index += 1
					

	def _TransToDict(self,index,_str):
		string_stack = Stack()
		i=index
		dict_ = {}
		while i < len(_str):
			if i+2 < len(_str) and _str[i+1] == '=' and _str[i+2] != '{':
				if _str[i+2] == '[':
					j,list_ = self._MakeList(i+2,_str)
					if string_stack.top() != '{':
						string_stack.top().update(dict({self._Transstr(_str[i]):list_}))
						dict_3 = string_stack.top()
					else:
						string_stack.push(dict({self._Transstr(_str[i]):list_}))
						dict_3 = string_stack.top()
					i = j-2
				elif string_stack.top() != '{':
					string_stack.top().update(dict({self._Transstr(_str[i]):self._Transstr(_str[i+2])}))
					dict_3 = string_stack.top()
				else:
					string_stack.push(dict({self._Transstr(_str[i]):self._Transstr(_str[i+2])}))
					dict_3 = string_stack.top()
				i += 2
			elif _str[i] == '{':
				string_stack.push(_str[i])
			elif _str[i] == '}':
				tmp_ = {}
				dict_2 = {}
				if string_stack.top() != '{':
					tmp_.update(string_stack.top())
					string_stack.pop()
					string_stack.pop()
					if not string_stack.empty() and string_stack.top() != '{':
						if string_stack.top() == '=':
							string_stack.pop()
							key = self._Transstr(string_stack.top())
							string_stack.pop()
							dict_2 = dict({key:tmp_})
						if string_stack.top() != '{':
							string_stack.top().update(dict_2)
							dict_3 = string_stack.top()
						else:
							string_stack.push(dict_2)
					elif string_stack.empty():
						return i,tmp_
					else:
						string_stack.pop() 
				else:
						string_stack.pop() 
			else:
				string_stack.push(_str[i])  
			i += 1
		return i, dict_
	def _start(self,str_):
		self._pos = 0
		str_list = self._oper(str_)
		self._TransListStr(str_list)
		list_str = self._TransBracket(self._new_list_str[:])
		new_list_str = self._TransNilToNone(list_str)
		self._dict_list_str = self._TransListToStr(new_list_str)
		
		
	def load(self,str_):
		if(len(str_) == 0):
			raise ParerError("string error")
		self._start(str_)
	def dumpDict(self):
		i,p1 = self._TransToDict(0,self._dict_list_str[:])
		self._dict = p1
		return p1
			
	def __getitem__(self, item):
		if len(self._str)==0 or (self._str and self._dict):
			return self._dict[item]
		else:
			raise ParerError("string error")
			
	def update(self, d):
		if len(self._str)==0 or (self._str and self._dict):
			return self._dict.update(d)
		else:
			raise ParerError("string error")
	def _TranOriChar(self,ch):
		if self._rever_spec_hash.has_key(ch):
			return self._rever_spec_hash[ch]
		return ch
	def _TranOriString(self,str_):
		if len(str_) > 2 and (str_[0] == '"' or str_[0] =='\''):
			i = 1
			tmp = '"'
			while i < len(str_)-1:
				tmp += self._TranOriChar(str_[i])
				i+=1
			tmp += '"'
			return tmp
		else:
			return str_
	def _TransLuaList(self,list_str):
		new_list_str = list_str[:]
		for i in range(len(new_list_str)):
			new_list_str[i] = self._TranOriString(new_list_str[i])
		return new_list_str
	def dump(self):
		string_stack = Stack()
		#print self._dict_list_str
		new_list_str = self._TransLuaList(self._dict_list_str)
		#print new_list_str
		str_ = ''
		i=0
		while i < len(new_list_str):
			if new_list_str[i] == '{':
				str_ += '{\n'
				string_stack.push(new_list_str[i])
			elif new_list_str[i] == '[':
				str_ += '{'
				string_stack.push(new_list_str[i])
			elif new_list_str[i] == '=':
				str_ += '= '
			elif i+1 < len(new_list_str) and new_list_str[i+1] == '=':
				str_ += ('[' + new_list_str[i] + ']')
			elif new_list_str[i] == '}' or new_list_str[i] == ']':
				string_stack.pop()
				if i == len(new_list_str)-1 or (i+1 < len(new_list_str) and new_list_str[i+1] == '}'):
					str_ += '}\n'
				elif string_stack.top() == '{':
					str_ += '},\n'
				else:
					str_ += '},'
			else:
				if new_list_str[i] == 'None' or new_list_str[i] == '"None"' :
					new_list_str[i] = 'nil'
				elif new_list_str[i] == 'True' or new_list_str[i] == '"True"':
					new_list_str[i] = 'true'
				elif new_list_str[i] == 'False'or new_list_str[i] == '"False"' :
					new_list_str[i] = 'false'
				if(string_stack.top() == '[' and i+1 < len(new_list_str) and new_list_str[i+1] == ']'):
					str_ += new_list_str[i]
				elif string_stack.top() == '[':
					str_ += (new_list_str[i]+',')
				elif (string_stack.top() == '{' and i+1 < len(new_list_str) and new_list_str[i+1] == '}'):
					str_ += (new_list_str[i] + '\n')
				else:
					str_ += (new_list_str[i] + ',\n')
			i+=1
		self._lua_table_str = str_
		return self._lua_table_str[:]
		
	def dumpLuaTable(self, FileName):
		fp = open(FileName, 'w')
		fp.write(self.dump())
		fp.close()
		
		
	def loadLuaTable(self, FileName):
		fp = open(FileName, 'r')
		str_ = fp.read()
		self._start(str_)
		fp.close()
	def ReMoveNoneedKey(self,d):
		if isinstance(d,dict):
			for i in d.keys():
				if not isinstance(i, (int, float, str)):
					del d[i]
				if isinstance(d,dict):
					self.ReMoveNoneedKey(d[i])
				elif isinstance(d[i],list):
					for j in d[i]:
						if isinstance(j,dict):
							self.ReMoveNoneedKey(j)
					
	def _TransList(self,l):
		self._lua_table_str += '{'
		if isinstance(l,list):
			for j in range(len(l)):
				if isinstance(l[j],dict):
					self._TransDict(l[j])
				elif l[j] == None:
					str_ = 'nil'
					self._lua_table_str += str_ + ','
				elif isinstance(l[j],str):
					str_ = self._TransString(l[j])
					str_ = '"' + str_ + '"' 
					if str_ == '"False"':
						str_ = 'false'
					elif str_ == '"True"':
						str_ = 'true'
					self._lua_table_str += str_ + ','
				elif isinstance(l[j],list):
					self._TransList(l[j])
				elif isinstance(l[j],(float,int)):
					str_ = str(l[j])
					self._lua_table_str += str_ + ','
		self._lua_table_str += '}'
		
	def _TransString(self,s):
		if isinstance(s,str):
			str_ = ''
			for i in s:
				str_ += self._TranOriChar(i)
			return str_
		
	def _TransDict(self,d):
		self._lua_table_str += '{'
		for i in d.keys():
			if isinstance(i,str):
				str_ = self._TransString(i)
				str_ = r'["' + str_ + r'"]'
				self._lua_table_str += str_ + '='
			elif isinstance(i,int):
				str_ = r'[' + str(i) + r']'
				self._lua_table_str += str_ + '='
			if isinstance(d[i],list):
				self._TransList(d[i])
			elif isinstance(d[i],str):
				str_ = self._TransString(d[i])
				str_ = r'"' + str_ + r'"'
				if str_ == '"False"':
						str_ = 'false'
				elif str_ == '"True"':
					str_ = 'true'
				self._lua_table_str += str_ + ','
			elif isinstance(d[i],(float,int)):
				self._lua_table_str += str(d[i]) + ','
			elif isinstance(d[i],dict):
				self._TransDict(d[i])
		self._lua_table_str += '}'	
		
	def loadDict(self,d):
		self.ReMoveNoneedKey(d)
		self._lua_table_str = ''
		self._TransDict(d)
		s = self._lua_table_str
		self.load(s)

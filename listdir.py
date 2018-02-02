#!/usr/bin/env python
#coding:utf-8


import os
from time import sleep
from Tkinter import *

class DirList(object):
	def clrDir(self,ev=None):
		self.cwd.set('')  #什么变量拥有set方法
	
	def setDirAndGo(self,ev=None):  #双击文本项的时候，会将其设为当前并将其背景色设置为红色然后调用doLS函数。
		self.last = self.cwd.get() 
		self.dirs.config(selectbackground='red')
		check = self.dirs.get(self.dirs.curselection()) 
		if not check:
			check = os.curdir
		self.cwd.set(check)
		self.doLS()

	def doLS(self,ev=None):
		error = ''
		tdir = self.cwd.get()
		if not tdir: tdir = os.curdir
		if not os.path.exists(tdir):
			error = tdir + ': no such file'
		elif not os.path.isdir(tdir):
			error = tdir + ': not a directory'

		if error:
			self.cwd.set(error)
			self.top.update()
			sleep(2)
			if not (hasattr(self,'last') and self.last):
				self.last = os.curdir
			self.cwd.set(self.last)
			self.dirs.config(selectbackground='LightSkyBlue')
			self.top.update()
			return

		self.cwd.set('FETCHING DIRECTORY CONTENTS...')
		self.top.update()
		dirlist = os.listdir(tdir)
		dirlist.sort()
		os.chdir(tdir)

		self.dirl.config(text=os.getcwd())
		self.dirs.delete(0,END)
		self.dirs.insert(END,os.curdir)   #添加一个文本项
		self.dirs.insert(END,os.pardir)
		for eachFile in dirlist:
			self.dirs.insert(END,eachFile)
		self.cwd.set(os.curdir)
		self.dirs.config(selectbackground='LightSkyBlue')  #文本项被选择的时候，背景色为天空蓝

	
	def __init__(self,initdir=None):
		self.top = Tk()
		self.label = Label(self.top,text='Directory Lister v1.1')
		self.label.pack()
                
		#如果设置一个textvariable属性为一个StringVar(IntVar,DoubleVar)对象，当这个值被重新设置的时候，组件上的显示文字会自动编程新的值
		self.cwd = StringVar(self.top)

		#font用于设置显示的字体类型以及字体大小,此标签为当前目录的绝对路径
		self.dirl = Label(self.top,fg='blue',font=('Helvetica',12,'bold'))
		self.dirl.pack()
		
		
		#Frame就是屏幕上的一块矩形区域，多是用来作为容器来布局窗体
		self.dirfm = Frame(self.top)
		#在矩形区域内设置一个滚动条，位置为最右边垂直填充
		self.dirsb = Scrollbar(self.dirfm)
		self.dirsb.pack(side=RIGHT,fill=Y)
		#列表框控件，可包含一个或多个文本项，一般都是Scrollbar和Listbox结合使用以达到一种组件的动作会引发另一种组件的动作，只需要在Listbox的
		#命令选项中设置为scrollbar的set方法，以及设置其本身的yview（见81行）
		self.dirs = Listbox(self.dirfm,height=15,
				width=50,yscrollcommand=self.dirsb.set)
		#绑定意味着将一个回调函数与按键、鼠标操作或一些其它事件连接起来，当用户发起这类事件时，回调函数就会执行。当双击Listbox的任意条目时，就会
		#调用setDirAndGo函数
		self.dirs.bind('<Double-1>',self.setDirAndGo)  #通过使用bind方法，Listbox列表项可以与回调函数setDirAndGo连接起来
		self.dirsb.config(command=self.dirs.yview) #Scrollbar通过调用config方法与Listbox连接起来
		self.dirs.pack(side=LEFT,fill=BOTH)
		self.dirfm.pack()
		
		#Entry是Tkinter用来接收字符串输入的控件，该控件允许用户输入一行文字。如果输入的文字太长，文字会向后滚动
		self.dirn = Entry(self.top,width=50,
					textvariable=self.cwd)  #设置textvariable会不断更新显示文本
		#将其与回调函数doLS绑定在一起，那么在点击相应的条目并通过Entry接收到字符串时或者是在Entry当中输入了字符串之后，会调用doLS然后显示目录列表
		self.dirn.bind('<Return>',self.doLS)  #此绑定表示doLS和回车键绑定在一起，那么当在Entry当中输入了目录名称之后，按回车键也会调用doLS 
		self.dirn.pack()

		#每次进行button或滚动条之前都会先设置一个Frame?
		self.bfm = Frame(self.top)
		self.clr = Button(self.bfm,text='Clear',command=self.clrDir,
				activeforeground='white',
				activebackground='blue')
		self.ls = Button(self.bfm,text='List Directory',
				command=self.doLS,
				activeforeground='white',
				activebackground='green')
		self.quit = Button(self.bfm,
				text='Quit',
				command=self.top.quit,
				activeforeground='white',
				activebackground='red')
		self.clr.pack(side=LEFT)
		self.ls.pack(side=LEFT)
		self.quit.pack(side=LEFT)
		self.bfm.pack()

		if initdir:
			self.cwd.set(os.curdir)
			self.doLS()

def main():
	d = DirList(os.curdir)
	mainloop()

if __name__ == '__main__':
	main()

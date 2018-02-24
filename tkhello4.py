#!/usr/bin/env python
#coding:utf-8

'''
这个简单的例子额外调用Scale控件。这里Scale用于与Label控件进行交互。Scale滑块是用来控制Label控件中文字字体大小的工具。滑块的位置值越大，字体越大；反之亦然
其核心是resize函数的回调，该函数会依附于Scale控件，当Scale控件滑块移动时，这个函数就会被激活，用来调整Label控件中的文本大小
'''
from Tkinter import *

def resize(ev=None):
	label.config(font='Helvetica -%d bold' %scale.get())

top = Tk()


label = Label(top,text='Hello World!',font='Helvetical -12 bold')
label.pack(fill=Y,expand=1)

scale = Scale(top,from_=10,to=40,orient=HORIZONTAL,command=resize)
scale.set(12) #初始设置为12
scale.pack(fill=X,expand=1)

quit = Button(top,text='QUIT',command=top.quit,activeforeground='white',
			activebackground='red')
quit.pack()

mainloop()

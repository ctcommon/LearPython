#!/usr/bin/env python
#coding:utf-8
'''
此实例应用了偏函数，感觉类似于C++的偏特化模版，就是将原函数的某些参数设置固定制作一个新的函数，
适用于很多调用对象反复调用的都是相同参数的情况。本例的应用有很多按钮拥有相同的前景色和背景色
对于这种只有细微差别的按钮，每次都使用相同的参数来创建相同的实例是一种浪费。因为其只有文本有一点不同，所以适用偏函数。
'''
from functools import partial as pto  #将偏函数模块partial导入，并在本模块中改为别名pto
from Tkinter import Tk,Button,X
from tkMessageBox import showinfo,showwarning,showerror

WARN = 'warn'
CRIT = 'crit'
REGU = 'regu'

SIGNS = {
	'do not enter':CRIT,
	'railroad crossing':WARN,
	'55\nspped limit':REGU,
	'wrong way':CRIT,
	'merging traffic':WARN,
	'one way':REGU,
	}

critCB = lambda: showerror('Error','Error Button Pressed!')
warnCB = lambda: showwarning('Warning','Warning Button Pressed!')
infoCB = lambda: showinfo('Info','Info Button Pressed!')

top = Tk()
top.title('Road Signs')
Button(top,text='QUIT',command=top.quit,
	bg='red',fg='white').pack()

'''
使用了两阶偏函数。第一阶模板化了Button类和根窗口top。这表示每次调用Mybutton函数的时候，就会调用Button类，并将top作为它的第一个参数。
第二阶偏函数会使用第一阶的制作的偏函数Mybutton函数，并对其进行模板化。当用户创建一个严重类型的按钮CritButton就会调用包含适当的按钮回
调函数、前景色和背景色的MyButton
'''
MyButton = pto(Button,top) 
CritButton = pto(MyButton,command=critCB,bg='white',fg='red')
WarnButton = pto(MyButton,command=warnCB,bg='goldenrod1')
ReguButton = pto(MyButton,command=infoCB,bg='white')

'''
使用一个Python可求值字符串，该字符串由正确的按钮名、传给按钮标签的文本参数以及pack()操作组成。每个按钮都会通过eval()函数进行实例化
'''

for eachSign in SIGNS:
	signType = SIGNS[eachSign]
	cmd = '%sButton(text=%r%s).pack(fill=X,expand=True)' %(signType.title(),eachSign,'.upper()' if signType == CRIT else '.title()')
	eval(cmd)

top.mainloop()

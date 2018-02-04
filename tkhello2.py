#!/usr/bin/env python
#coding:utf-8

import Tkinter

top = Tkinter.Tk()
quit =  Tkinter.Button(top,text='Hello World!',command=top.quit) #给按钮安装一个回调函数，当按钮被按下（并释放）后，整个程序就会退出
quit.pack()
Tkinter.mainloop()

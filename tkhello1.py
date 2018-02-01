#!/usr/bin/env python
#coding:utf-8


import Tkinter

top = Tkinter.Tk()  #创建了一个顶层窗口
label = Tkinter.Label(top,text='Hello World!') 
label.pack()  #让Packer来管理和显示控件
Tkinter.mainloop()   #最后调用mainloop()运行这个GUI应用

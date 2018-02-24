#!/usr/bin/env python
#coding:utf-8

import Tkinter
top = Tkinter.Tk()

hello = Tkinter.Label(top,text='Hello World!')
hello.pack()

#按钮的背景为红色，前景（一般指按钮的标题）为白色
quit = Tkinter.Button(top,text='QUIT',command=top.quit,bg='red',fg='white')
#fiil参数告诉Packer让QUIT按钮占据剩余的水平空间，而expand参数则会引导它填充整个水平可视空间，将按钮拉伸到左右窗口边缘
quit.pack(fill=Tkinter.X,expand=1)

Tkinter.mainloop()

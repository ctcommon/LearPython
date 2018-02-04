#!/usr/bin/env python3
#coding:utf-8

'''
抽象工厂模式，什么是工厂？可以理解为是用于生产事务的就叫工厂，而抽象工厂用于
创建复杂的对象。这些对象由许多小对象组成。例如本次例子，两个工厂DiagramFactory
以及SvgDiagramfactory(此工厂以DiagramFactory工厂为基类)。用于创建两种不同格式的文本
内部创建方框，文本等的接口都是一样的，然后用一个create_diagram(factory)，以工厂为参数
通过引用不同的工厂进而能够创建不同类型的文本。然而本例还有些地方待改进：SvgDiagramFactory
和DiagramFactory的代码基本上是一模一样，就是返回的类型不一样，这样就产生了无谓的重复代码
实质上，两个工厂的实现的renturn 接口可以一样，只要将其放在各自的命名空间内防止名字冲突，即不要放在顶层，这样接口可以继承调用，只是需要不同的类类型而已。改进的见diagram2.py文件
'''

import os
import sys
import tempfile  #tempfile米块允许你快速地创建名称唯一的临时文件供使用，用相关函数创建的临时文件，关闭后会自动删除

SVG_SCALE = 20

SVG_TEXT = """<text x="{x}" y="{y}" text-anchor = "left" \
		font-family="sans-serif" font-size="{fontsize}">(text)</text>"""

SVG_RECTANGLE = """<rect x ="{x}" y="{y}" width="{width}" \
		height="{height}" fill="{fill}" stroke="{stroke}"/>"""

SVG_START = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE syq PUBLIC "-//W3C//DTD SVG 20010904//EN"
	"http://www.w3.org/TR/2001/REC-SVG-20010904//DTD//svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg"
	xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
	width="{pxwidth}px" height="{pxheight}px">"""

SVG_END = "</svg>\n"

class SvgText:
	def __init__(self,x,y,text,fontsize):
		x *= SVG_SCALE
		y *= SVG_SCALE
		fontsize *= SVG_SCALE // 10
		'''
		这里的locals()会将复制形式的局部变量和形参以字典的形式返回。而**locals()在
		format函数调用里的意思是将locals()返回的字典解包传递给format函数。比如调入
		的形参为x=1,y=2,text="",fontsize = 5，通过locals调用会变为x:1,y:2,text:""等
		字典的形式，然后调用format(**locals())就是解包，将字典变为x=1,y=2,text=""
		fontsize=5之后传递给format作为其形参，然后将x,y,text,fontsize的值传递进给
		字符串SVG_TEXT当中{x},{y},{fontsize}当中
		'''
		self.svg = SVG_TEXT.format(**locals())

class SvgRectangle:
	def __init__(self,x,y,width,height,fill,stroke):
		x *= SVG_SCALE
		y *= SVG_SCALE
		width *= SVG_SCALE
		height *= SVG_SCALE
		self.svg = SVG_RECTANGLE.format(**locals())

class SvgDiagram:
	def __init__(self,width,height):
		pxwidth = width*SVG_SCALE
		pxheight = height*SVG_SCALE
		self.diagram = [SVG_START.format(**locals())]
		outline = SvgRectangle(0,0,width,height,"lightgreen","black")
		self.diagram.append(outline.svg)

	def add(self,component):
		self.diagram.append(component.svg)

	def save(self,filenameOrFile):
		file = None if isinstance(filenameOrFile,str) else filenameOrFile
		try:
			if file is None:
				file = open(filenameOrFile,"w",encoding="utf-8")
				#join函数是用于将序列中的元素以指定的字符（这里是'\n'）连接生成一个新的字符串
				file.write("\n".join(self.diagram))
				file.write("\n"+SVG_END)
		finally:
			if isinstance(filenameOrFile,str) and file is not None:
				file.close()

class Text:
	def __init__(self,x,y,text,fontsize):
		self.x = x
		self.y = y
		self.rows = [list(text)]

BLANK = " "
CORNER = "+"
HORIZONTAL = "-"
VERTICAL = "|"

class Diagram:
	def __init__(self,width,height):
			self.width = width
			self.height = height
			self.diagram = _create_rectangle(self.width,self.height,BLANK)

	def add(self,component):
		for y, row in enumerate(component.rows):
			for x,char in enumerate(row):
				self.diagram[y+component.y][x+component.x] = char

	def save(self,filenameOrFile):
		file = None if isinstance(filenameOrFile,str) else filenameOrFile
		try:
			if file is None:
				file = open(filenameOrFile,"w",encoding="utf-8")
			for row in self.diagram:
				print("".join(row),file=file)
		finally:
			if isinstance(filenameOrFile,str) and file is not None:
				file.close()

def _create_rectangle(width,height,fill):
	rows = [[fill for _ in range(width)] for _ in range(height)]
	for x in range(1,width-1):
		rows[0][x] = HORIZONTAL
		rows[height-1][x] = HORIZONTAL
	for y in range(1,height-1):
		rows[y][0] = VERTICAL
		rows[y][width-1] = VERTICAL
	for y,x in ((0,0),(0,width-1),(height-1,1),(height-1,width-1)):
		rows[y][x] = CORNER
	return rows

class Rectangle:
	def __init__(self,x,y,width,height,fill,stroke):
		self.x = x
		self.y = y
		self.rows = _create_rectangle(width,height,BLANK if fill == "white" else "%")

class DiagramFactory:
	def make_diagram(self,width,height):
		return Diagram(width,height)

	def make_rectangle(self,x,y,width,height,fill="white",stroke="black"):
		return Rectangle(x,y,width,height,fill,stroke)

	def make_text(self,x,y,text,fontsize=12):
		return Text(x,y,text,fontsize)

class SvgDiagramFactory(DiagramFactory):
	def make_diagram(self,width,height):
		return SvgDiagram(width,height)
	
	def make_rectangle(self,x,y,width,height,fill="white",stroke="black"):
		return SvgRectangle(x,y,width,height,fill,stroke)

	def make_text(self,x,y,text,fontsize=12):
		return SvgText(x,y,text,fontsize)

def create_diagram(factory):
	diagram = factory.make_diagram(30,7)
	rectangle = factory.make_rectangle(4,1,22,5,"yello")
	text = factory.make_text(7,3,"Abstract Factory")
	diagram.add(rectangle)
	diagram.add(text)
	return diagram

def main():
	if len(sys.argv) > 1 and sys.argv[1] == "-P":
		create_diagram(DiagramFactory()).save(sys.stdout)
		create_diagram(SvgDiagramFactory()).save(sys.stdout)
		return
	textFilename = os.path.join(tempfile.gettempdir(),"diagram.txt")
	svgFilename = os.path.join(tempfile.gettempdir(),"diagram.svg")

	txtDiagram = create_diagram(DiagramFactory())
	txtDiagram.save(textFilename)
	print("wrote",textFilename)

	svgDiagram = create_diagram(SvgDiagramFactory())
	svgDiagram.save(svgFilename)
	print("wrote",svgFilename)

if __name__ == "__main__":
	main()

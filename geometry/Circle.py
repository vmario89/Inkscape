#!/usr/bin/env python
#coding: UTF-8
import sys,os,math
sys.path.append("/Applications/Inkscape.app/Contents/Resources/extensions")
import inkex
class Circle():
	def __init__(self,_c,_r):
		self.radius=_r
		self.center=_c
	def __str__(self):
		return "Circle: center:"+str(self.center)+" radius:"+str(self.radius)+"\n"
	def __repr__(self):
		return "Circle: center"+str(self.center)+" radius:"+str(self.radius)+"\n"
	def isHit(p):
		distance=(center-p).length()
		if(distance<radius):
			return True
		return False
	#static関数
	@classmethod
	def toSVGObject(cls,x,y,r,color,strokewidth):
		att={"cx":str(x),"cy":str(y),"r":str(r),"fill":color,"stroke-width":str(strokewidth)}
		return inkex.etree.Element("circle",att)

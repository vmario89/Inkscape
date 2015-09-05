#!/usr/bin/env python
#coding: UTF-8
import sys,os,math
sys.path.append("/Applications/Inkscape.app/Contents/Resources/extensions")
import inkex
class Minus():
	def __init__(self,_x,_y,_r):
		self.x=_x
		self.y=_y
		self.r=_r

	def isHit(p):
		distance=(center-p).length()
		if(distance<radius):
			return True
		return False
	#static関数
	def appendToSVG(self,color,svg):
		attbackcicle={"cx":str(self.x),"cy":str(self.y),"r":str(self.r),"fill":"white",
		"stroke-width":"0"}
		attcicle={"cx":str(self.x),"cy":str(self.y),"r":str(self.r),"fill":color,"fill-opacity":"0.6",
		"stroke-width":str(max(1,self.r/4)),"stroke":color}
		#横線
		atthline={"x1":str(self.x-self.r),"y1":str(self.y),
		"x2":str(self.x+self.r),"y2":str(self.y),"stroke":color}
		svg.append(inkex.etree.Element("circle",attbackcicle))
		svg.append(inkex.etree.Element("circle",attcicle))
		svg.append(inkex.etree.Element("line",atthline))

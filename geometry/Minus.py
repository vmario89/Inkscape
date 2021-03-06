#!/usr/bin/env python3

import math
import inkex
from lxml import etree

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

	def appendToSVG(self,color,svg):
		attbackcicle={"cx":str(self.x),"cy":str(self.y),"r":str(self.r),"fill":"white",
		"stroke-width":"0"}
		attcicle={"cx":str(self.x),"cy":str(self.y),"r":str(self.r),"fill":color,"fill-opacity":"0.6",
		"stroke-width":str(max(1,self.r/4)),"stroke":color}

		atthline={"x1":str(self.x-self.r),"y1":str(self.y),
		"x2":str(self.x+self.r),"y2":str(self.y),"stroke":color}
		svg.append(etree.Element("circle",attbackcicle))
		svg.append(etree.Element("circle",attcicle))
		svg.append(etree.Element("line",atthline))

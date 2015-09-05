#!/usr/bin/env python
# coding: UTF-8
# standard library
import sys
import os
# local library
import inkex
import simplestyle
import simplepath
import simpletransform
import voronoi
import cubicsuperpath
from PIL import Image
inkex.localize()


class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def __lt__(self,other):
		return (self.x*self.y<other.x*other.y)
	def __le__(self,other):
		return (self.x*self.y<=other.y*other.y)
	def __gt__(self,other):
		return (self.x*self.y>other.x*other.y)
	def __ge__(self,other):
		return (self.x*self.y>=other.x*other.y)
	def __eq__(self,other):
		return (self.x==other.x) and (self.y==other.y)
	def __ne__(self,other):
		return (self.x!=other.x) or (self.y!=other.y)

	def __str__(self):
		return "("+str(self.x)+","+str(self.y)+")"



class PointsFromImage(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)

		# {{{ Additional options

		self.OptionParser.add_option(
			"--tab",
			action="store",
			type="string",
			dest="tab")
		self.OptionParser.add_option(
            '--threshold',
            action='store',
            type='string',
            default='10',
            dest='threshold',
            help='threshold of detect edge')
		self.OptionParser.add_option(
            '--interval',
            action='store',
            type='string',
            default='10',
            dest='interval',
            help='interval of put points')
		self.pointstyle={}
		#}}}

	# {{{ Clipping a line by a bounding box
	def dot(self, x, y):
		return x[0] * y[0] + x[1] * y[1]

	def intersectLineSegment(self, line, v1, v2):
		s1 = self.dot(line, v1) - line[2]
		s2 = self.dot(line, v2) - line[2]
		if s1 * s2 > 0:
			return (0, 0, False)
		else:
			tmp = self.dot(line, v1) - self.dot(line, v2)
			if tmp == 0:
				return (0, 0, False)
			u = (line[2] - self.dot(line, v2)) / tmp
			v = 1 - u
			return (u * v1[0] + v * v2[0], u * v1[1] + v * v2[1], True)

	def clipEdge(self, vertices, lines, edge, bbox):
		#bounding box corners
		bbc = []
		bbc.append((bbox[0], bbox[2]))
		bbc.append((bbox[1], bbox[2]))
		bbc.append((bbox[1], bbox[3]))
		bbc.append((bbox[0], bbox[3]))

		#record intersections of the line with bounding box edges
		line = (lines[edge[0]])
		interpoints = []
		for i in range(4):
			p = self.intersectLineSegment(line, bbc[i], bbc[(i + 1) % 4])
			if (p[2]):
				interpoints.append(p)

		#if the edge has no intersection, return empty intersection
		if (len(interpoints) < 2):
			return []

		if (len(interpoints) > 2):  #happens when the edge crosses the corner of the box
			interpoints = list(set(interpoints))  #remove doubles

		#points of the edge
		v1 = vertices[edge[1]]
		interpoints.append((v1[0], v1[1], False))
		v2 = vertices[edge[2]]
		interpoints.append((v2[0], v2[1], False))

		#sorting the points in the widest range to get them in order on the line
		minx = interpoints[0][0]
		maxx = interpoints[0][0]
		miny = interpoints[0][1]
		maxy = interpoints[0][1]
		for point in interpoints:
			minx = min(point[0], minx)
			maxx = max(point[0], maxx)
			miny = min(point[1], miny)
			maxy = max(point[1], maxy)

		if (maxx - minx) > (maxy - miny):
			interpoints.sort()
		else:
			interpoints.sort(key=lambda pt: pt[1])

		start = []
		inside = False  #true when the part of the line studied is in the clip box
		startWrite = False  #true when the part of the line is in the edge segment
		for point in interpoints:
			if point[2]:  #The point is a bounding box intersection
				if inside:
					if startWrite:
						return [[start[0], start[1]], [point[0], point[1]]]
					else:
						return []
				else:
					if startWrite:
						start = point
				inside = not inside
			else:  #The point is a segment endpoint
				if startWrite:
					if inside:
						#a vertex ends the line inside the bounding box
						return [[start[0], start[1]], [point[0], point[1]]]
					else:
						return []
				else:
					if inside:
						start = point
				startWrite = not startWrite

	#}}}

	#{{{ Transformation helpers

	def invertTransform(self, mat):
		det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
		if det != 0:  #det is 0 only in case of 0 scaling
			#invert the rotation/scaling part
			a11 = mat[1][1] / det
			a12 = -mat[0][1] / det
			a21 = -mat[1][0] / det
			a22 = mat[0][0] / det

			#invert the translational part
			a13 = -(a11 * mat[0][2] + a12 * mat[1][2])
			a23 = -(a21 * mat[0][2] + a22 * mat[1][2])

			return [[a11, a12, a13], [a21, a22, a23]]
		else:
			return [[0, 0, -mat[0][2]], [0, 0, -mat[1][2]]]

	def getGlobalTransform(self, node):
		parent = node.getparent()
		myTrans = simpletransform.parseTransform(node.get('transform'))
		if myTrans:
			if parent is not None:
				parentTrans = self.getGlobalTransform(parent)
				if parentTrans:
					return simpletransform.composeTransform(parentTrans, myTrans)
				else:
					return myTrans
		else:
			if parent is not None:
				return self.getGlobalTransform(parent)
			else:
				return None


	#}}}
	def addEllipse(self,group,x,y):
		ellipse=inkex.etree.Element(inkex.addNS('ellipse', 'svg'))
		ellipse.set('cx',str(x))
		ellipse.set('cy',str(y))
		ellipse.set('rx','2')
		ellipse.set('ry','2')
		ellipse.set('style', simplestyle.formatStyle(self.pointstyle))
		group.append(ellipse)
	def effect(self):

		#{{{ Check that elements have been selected
		fp=open("log.txt","w")
		fp.write("threshold"+self.options.threshold+'\n')

		#}}}


		#{{{ Handle the transformation of the current group

		svg = self.document.getroot()
		children =svg.getchildren()
		self.pointstyle={
			'stroke': 'red',
			'stroke-width': str(self.unittouu('0px')),
			'fill': 'red'
		}

		img=None

		width_in_svg=1
		height_in_svg=1
		href=''
		for child in children:
			if child.tag=="{http://www.w3.org/2000/svg}g":
				ccc=child.getchildren()
				for c in ccc:
					if c.tag=="{http://www.w3.org/2000/svg}image":
						href=c.attrib["{http://www.w3.org/1999/xlink}href"]
						width_in_svg=c.attrib['width']
						height_in_svg=c.attrib['height']

			elif child.tag=="{http://www.w3.org/2000/svg}image":
				href=child.attrib["{http://www.w3.org/1999/xlink}href"]
				if "file://" in href:
					href=href[7:]
				width_in_svg=child.attrib['width']
				height_in_svg=child.attrib['height']
			elif href=='':
				continue
			fp.write('in inkscape:'+str(width_in_svg)+'x'+str(height_in_svg)+'\n')
			fp.write('href:'+href+"\n")
			img = Image.open(href).convert('L')

		if img==None:
			inkex.errormsg(_("Please import Image"))
			return

		groupPoints = inkex.etree.SubElement(svg, inkex.addNS('g', 'svg'))
		width = img.size[0]
		height= img.size[1]
		points=[]
		scale_x=float(width_in_svg)/float(width)
		scale_y=float(height_in_svg)/float(height)
		fp.write('width='+str(width)+', height='+str(height)+'\n')
		fp.write('scale_x='+str(scale_x)+', scale_y='+str(scale_y)+'\n')
		step_x=int(width*float(self.options.interval)/100.0)
		step_y=int(height*float(self.options.interval)/100.0)
		fp.write('step_x='+str(step_x)+", step_y="+str(step_y)+'\n')
		linestyle = {
			'stroke': 'red',
			'stroke-width': str(self.unittouu('0px')),
			'fill': 'red'
		}
		for x in range(0,width,step_x):
			for y in range(0,height,step_y):
				color=img.getpixel((x,y))
				#fp.write('x='+str(x)+' y='+str(y)+' '+str(color)+',\n')
				if color > int(self.options.threshold):
					self.addEllipse(groupPoints,scale_x*x,scale_y*y)
					# points.append(Point(x,y))
					# ellipse=inkex.etree.Element(inkex.addNS('ellipse', 'svg'))
					# ellipse.set('cx',str(x))
					# ellipse.set('cy',str(y))
					# ellipse.set('rx','2')
					# ellipse.set('ry','2')
					# ellipse.set('style', simplestyle.formatStyle(linestyle))
					# groupPoints.append(ellipse)
			#fp.write('\n')
		# if len(points)<=0:
		# 	inkex.errormsg(_(u"点が一個も出来ませんでした。閾値を見直してみましょう"))
		# 	return
		# cmds=[]
		# cmds.append(['M',[points[0].x,points[0].y]])
		# for pt in points[1:]:
		# 	cmds.append(['L',[pt.x,pt.y]])
		# path = inkex.etree.Element(inkex.addNS('path', 'svg'))
		# #TODO パスを作る、or ellipse作る
		# path.set('d',simplepath.formatPath(cmds))

		# path.set('style', simplestyle.formatStyle(linestyle))


		#}}}
		fp.close()



if __name__ == "__main__":
	e = PointsFromImage()
	e.affect()


# vim: expandtab shiftwidth=2 tabstop=2 softtabstop=2 fileencoding=utf-8 textwidth=99

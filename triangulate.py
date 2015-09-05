#!/usr/bin/env python
#coding: UTF-8
import sys,os,math

sys.path.append("/Applications/Inkscape.app/Contents/Resources/extensions")
#sys.path.append('/Library/Python/2.7/site-packages')
import inkex,cubicsuperpath,simplepath,simplestyle
from PIL import Image
import numpy
ALL=".//"
XMLNS="{http://www.w3.org/2000/svg}"
XLINK="{http://www.w3.org/1999/xlink}"
gVerts=[]
gTriangles=[]
gTree=[]
class Vertex():
	post=None
	pre=None
	def __init__(self,_x,_y):
		self.x=_x
		self.y=_y
	def __sub__(self,r):
		return Vertex(self.x-r.x,self.y-r.y)
	def __str__(self):
		return "("+str(self.x)+","+str(self.y)+")"
	def __repr__(self):
		return "("+str(self.x)+","+str(self.y)+")"
	def __eq__(self,p):
		return (self.x==p.x) && (self.y==p.y)
	def dot(self,p):
		return self.x*p.x+self.y*p.y
	def length(self):
		return math.hypot(self.x,self.y)
class Segment():
	#動かしたらいけない線分かどうか
	fixed=False
	def __init__(self,_begin,_end):
		self.begin=_begin
		self.end=_end
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
class Triangle():
	#Segmentを渡す
	def __init__(self,_a,_b,_c):
		self.a=_a
		self.b=_b
		self.c=_c
	def __repr__(self):
		return "Triangle:("+str(self.a)+","+str(self.b)+","+str(self.c)+")"
	#aを中心とした重心座標です
	# @return u b方向へどのくらい
	# @return v c方向へどのくらい
	def barycentric(self,p):
		#重心座標を使う方法
		#http://www.blackpawn.com/texts/pointinpoly/default.html
		ca = self.c-self.a
		ba = self.b-self.a
		pa = p-self.a

		#内積を計算
		dotca = ca.dot(ca)
		dotcba = ca.dot(ba)
		dotcpa = ca.dot(pa)
		dotba = ba.dot(ba)
		dotbpa = ba.dot(pa)

		#重心座標の計算
		invDenom = 1 / (dotca * dotba - dotcba * dotcba);

		u = (dotba * dotcpa-dotcba*dotbpa)*invDenom
		v = (dotca * dotbpa - dotcba * dotcpa) * invDenom
		return u,v
	#三角形の内側に点があるかどうか
	def isContain(self,p):
		u,v=self.barycentric(p)
		inkex.errormsg("\n u="+str(u)+" v="+str(v))
		#u=v=0ならば三角形のある点と同じ点
		#三角形の中に点があるかどうかチェック
		return (u > 0) and (v > 0) and (u + v < 1)
	def parseSVG(self):
		return str(self.a.x)+","+str(self.a.y)+","+str(self.b.x)+","+str(self.b.y)+","+str(self.c.x)+","+str(self.c.y)

	def circumcircle(self):
		#各辺の長さを求める
		ab=(self.a-self.b).length()
		bc=(self.b-self.c).length()
		ca=(self.c-self.a).length()
		s=(ab+bc+ca)/2.0;
		area=math.sqrt(s*(s-ab)*(s-bc)*(s-ca));
		maxlength=0
		if(maxlength<ab):
			maxlength=ab;longestEdge=2
		if(maxlength<bc):
			maxlength=bc;longestEdge=0;
		if(maxlength<ca):
			maxlength=ca;longestEdge=1

		if longestEdge==0:
				ha=2*area/bc;
				angleB=math.asin(ha/ab);
				angleC=math.asin(ha/ca);
				angleA=math.pi-angleB-angleC;
		if longestEdge== 1:
				hb=2*area/ca;
				angleA=math.asin(hb/ab);
				angleC=math.asin(hb/bc);
				angleB=math.pi-angleC-angleA;
		if longestEdge== 2:
				hc=2*area/ab;
				angleB=math.asin(hc/bc);
				angleA=math.asin(hc/ca);
				angleC=math.pi-angleA-angleB;

		A = math.sin(2.0*angleA);
		B = math.sin(2.0*angleB);
		C = math.sin(2.0*angleC);
		center=Vertex((self.a.x * A + self.b.x * B + self.c.x * C) / (A+B+C),
			(self.a.y * A + self.b.y * B + self.c.y * C) / (A+B+C));
		rad=bc / math.sin(angleA) / 2.0
		return Circle(center,rad);

#三角形ノード
class Node():
	def __init__(self,_t):
		self.triangle=_t
		self.children=[]
		#三角形の外接円
		self.circle=_t.circumcircle()
		inkex.errormsg(u"初期化 "+str(len(self.children)))
	def __repr__(self):
		return "Node:(Me="+str(self.triangle)+"children:"+str(len(self.children))+")\n"
	def add(self,child):
		self.children.append(child)
#幾何クラスに詰める pointsは２次元配列
# retrun nodes
def pack(points):
	#最初の４点は輪郭とわかっている
	segments=[]
	#外枠部分
	inkex.errormsg(u"外枠:"+str(points))
	lastv=Vertex(points[0][0],points[0][1])
	verts=[lastv]
	gVerts.append(lastv)
	for p in points[1:4]:
		v=Vertex(p[0],p[1])
		gVerts.append(v)
		segment=Segment(lastv,v)
		segment.fixed=True
		segments.append(segment)
		v.pre=segment
		lastv.post=segment
		lastv=v
	#三角形を作る
	inkex.errormsg(u"gVerts:"+str(gVerts))
	nodes=[Node(Triangle(gVerts[0],gVerts[1],gVerts[2]))]
	nodes.append(Node(Triangle(gVerts[2],gVerts[3],gVerts[0])))
	#自分で描いたパス部分
	for p in points[4:]:
		v=Vertex(p[0],p[1])
		gVerts.append(v);
		segment=Segment(lastv,v)
		segments.append(segment)
		v.pre=segment
		lastv.post=segment
		lastv=v
	return segments,nodes
#三角形分割
def devide(tri,p):
	#点が
	u,v=tri.barycentric(p)
	#三角形の点とpが一致してるパターン
	if u==0.0 or v==0.0 or u==1.0 or v==1.0:
		return None
	inkex.errormsg(u"u="+str(u)+" v="+str(v))
	#点は完全に内側で３分割するパターン
	if (u > 0) and (v > 0) and (u + v < 1):
		inkex.errormsg(u"\t★★★devide:"+str(tri)+" p:"+str(p)+u"★★★")
		a=Triangle(tri.a,tri.b,p)
		b=Triangle(tri.b,tri.c,p)
		c=Triangle(tri.c,tri.a,p)
		return [a,b,c]
	#三角形の辺の上にpがあるパターン
	if (u+v)==1.0:
		b=Triangle(tri.a,tri.b,p)
		c=Triangle(tri.a,tri.c,p)
		return [a,b]
#三角形の外接円の中に点があるかどうか調べる
def checkInsideCircle(node,p):
	for v in gVerts:
		if(v==p):
			continue
		if(node.circle.isHit(v)):
			flipEdge(node,v):#エッジがフリップして子供が２人生まれる
#エッジがフリップして子供が２人生まれる
# v...新しい点
def flipEdge(node,v):


def delauney(node):
	inkex.errormsg(u"★★inside Delauney="+str(node))
	insidenum=0
	for v in gVerts:
		inkex.errormsg(u"頂点"+str(v)+u"と三角形"+str(node.triangle)+u"のテスト")
		tris=devide(node.triangle,v)
		if tris ==None:
			continue
		for t in tris:
			insidenum+=1
			inkex.errormsg(u"新しい子供"+str(t))
			c=Node(t)
			node.add(c)
			gTree.append(delauney(c))
		break#devide出来る頂点1個見つけたら抜けましょう

	if insidenum==0:
		inkex.errormsg(u"\t\tdelauney戻り値:"+str(node))
		#葉っぱだけ拾って結果に入れる
		if(len(node.children)==0):
			gTriangles.append(node.triangle)
	return node


#三角形分割 points:点群
def triangulate(points):
	s,nodes=pack(points)
	#結果を格納するところ
	inkex.errormsg("Nodes="+str(nodes))
	for n in nodes:
		inkex.errormsg(u"外側n="+str(n))
		delauney(n)
	#葉っぱだけ拾う
	inkex.errormsg(u"Nodeの結果:"+str(gTree))

	return gTriangles,gTree

class TriangleEffect(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
	#エフェクトの挙動を書きます
	def effect(self):
		# メインのルート要素であるSVGを取得
		svg = self.document.getroot()
		inkex.errormsg(str(svg))
		image=svg.find(ALL+XMLNS+"image")
		width=inkex.unittouu(image.attrib["width"])
		height=inkex.unittouu(image.attrib["height"])
		#width  = inkex.unittouu(svg.get('width'))
		#height = inkex.unittouu(svg.attrib['height'])
		#初期化の点
		points=[[0,0],[width,0],[width,height],[0,height]]

		inkex.errormsg(u"画像属性" + str(image.attrib))
		url=image.attrib[XLINK+"href"]
		inkex.errormsg((u"画像" + str(url)))
		#file.//の部分を取り除く
		im = Image.open(url[7:])
		color=im.getpixel((0,0))
		inkex.errormsg((u"色:" + str(color)))
		path=svg.find(ALL+XMLNS+"path")
		if path == None:
			inkex.errormsg(u"パスを書いてください！！")
		#パスの頂点座標を取得
		vals=simplepath.parsePath(path.get('d'))
		for cmd,vert in vals:
			#たまに空のが入ってるため、それ対策
			if len(vert) != 0:
				inkex.errormsg((u"頂点:" + str(vert)))
				points.append(vert)

		trignales,nodes = triangulate(points)
		inkex.errormsg(u"三角形分割の結果"+str(trignales))
		i=0
		for t in trignales:
			onedarray=t.parseSVG()
			attributes={"points":str(onedarray),
			"style":"fill:"+simplestyle.formatColor3i(color[0],color[1],color[2])+";stroke:white;stroke-width:3",
			"fill-opacity":"0.5"}
			polygon =inkex.etree.Element("polygon",attributes)
			svg.append(polygon)
		#for n in nodes:
		#	circle=n.circle
		#	inkex.errormsg(u"円:"+str(circle))
		#	attributes={"cx":str(circle.center.x),"cy":str(circle.center.y),"r":str(circle.radius),
		#	"stroke":"yellow","stroke-width":"3","fill-opacity":"0.0"}
		#	circle =inkex.etree.Element("circle",attributes)
		#	svg.append(circle)

		inkex.errormsg(str(polygon))

# エフェクトインスタンスを作って、適用します
effect = TriangleEffect()
effect.affect()

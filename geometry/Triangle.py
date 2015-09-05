#!/usr/bin/env python
#coding: UTF-8
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
	def toSVG(self):
		return str(self.a.x)+","+str(self.a.y)+","+str(self.b.x)+","+str(self.b.y)+","+str(self.c.x)+","+str(self.c.y)
	#頂点a,b,cの並びは時計回りかどうか
	def isClockWise(self):
		circle=self.circumcircle()
		center=circle.center
		aTob=self.b-self.a
		aToc=self.c-self.a
		#外積を求めて向きを求めよう
		cross=aTob.cross(aToc)

		inkex.errormsg(" cross"+str(cross))
		if(cross>0):
			return True
		return False#反時計回り
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

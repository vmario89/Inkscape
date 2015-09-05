#!/usr/bin/env python
#coding: UTF-8
import sys,os,math
import codecs
sys.path.append("/Applications/Inkscape.app/Contents/Resources/extensions")
sys.path.append('../geometry')
#sys.path.append('/Library/Python/2.7/site-packages')
import inkex,cubicsuperpath,simplepath,simplestyle
from PIL import Image
import numpy
from Circle import Circle
from Vertex import Vertex
from Triangle import Triangle
from Plus import Plus
from Minus import Minus
ALL=".//"
def fixTo360(radian):
	if radian <0:
		return math.pi*2.0+radian
	return radian
def widenDir(start,end):
	d21x = end.x - start.x;
	d21y = end.y - start.y;
	return fixTo360(-math.atan2(d21x, d21y));
def lineDir(start,end):
	d21x = end.x - start.x;
	d21y = end.y - start.y;
	#inkex.errormsg("d21y "+str(d21y)+" d21x "+str(d21x)+" d21y/d21x"+str(d21y/d21x))
	rad=math.atan2(d21y, d21x);
	#inkex.errormsg(u"線の方向"+str(math.degrees(rad)))
	return fixTo360(rad)

#radian<0は来ないという想定です
def invert(radian):
	return radian-math.pi
def fixWithin90(radian):
	if math.fabs(radian)>math.pi/2.0:#±90(順方向)になってほしい
		return invert(radian)
	return radian
def fixOver90(radian):
	if math.fabs(radian)<math.pi/2.0:
		return invert(radian)
	return radian
def fixWithinAb180(radian):
	if math.fabs(radian)<math.pi:
		return radian
	if radian <0:
		return math.pi*2.0+radian
	return radian-math.pi*2.0

def printRadian(fp,message,radian):
	fp.write(message+":"+str(math.degrees(radian))+"\n")
def stripline(bone,linewidth,logname):
		fp = codecs.open(logname, "w", "utf_8" )
		i = 0;
		segmentNum = len(bone)-1;
		elementNum=(segmentNum*2+2)*5;
		outVertexArray = []
		#1線分につき４頂点　+終点に足した余分な分
		vertexIdx = 0;
		#最初の頂点
		start =bone[0];
		end =bone[1];
		lastRad=0
		lastUsedRad=0
		radY = widenDir(start,end)
		lineRad=lineDir(start,end)
		fp.write(u"0番目の頂点")
		printRadian(fp,u"lineRad",lineRad)

		originalRad=radY

		#曲がる方向を示す
		cornerDir=radY-lastRad
		printRadian(fp,u"radY",radY)
		diffRad=0
		printRadian(fp,u"diffRad:",diffRad)
		printRadian(fp,u"radY-lineRad:",radY-lineRad)
		printRadian(fp,u"sin(radY-lineRad:)",math.sin(radY-lineRad))

		adjustedRad=radY
		printRadian(fp,u"最初の描画角度",adjustedRad)
		fp.write("\n")
		direction=True
		lastRad=radY;

		lastUsedRad=adjustedRad
		LEFT=Vertex(linewidth,0)
		RIGHT=Vertex(-linewidth,0)
		#変数
		v=Vertex(0,0)
		v.set(LEFT)
		v.rotate(adjustedRad)
		flag = False #if radY< 0 else False
		outVertexArray.append([start+v,flag])


		v.set(RIGHT)
		v.rotate(adjustedRad)
		flag = True# if radY< 0 else False
		outVertexArray.append([start+v,flag])

		for i in range(1,segmentNum):
			start =bone[i]
			end =bone[i+1]
			originalRad = widenDir(start,end)
			radY=(originalRad+lastRad)*0.5#0〜360度の値
			fp.write(str(i)+u"番目の頂点")
			diffRad=(originalRad-lastRad)
			if math.fabs(math.fabs(diffRad)-math.pi)<=(45.0*math.pi/180.0):#Uターン時のとんがり三角形を消すため
				printRadian(fp,u"Uターン地点の補正:diffRad",diffRad)
				fp.write(u"差分"+str(math.fabs(math.fabs(diffRad)-math.pi)))
				radY=originalRad

			printRadian(fp,u"radY:",radY)
			printRadian(fp,u"diffRad:",diffRad)
			printRadian(fp,u"radY-lineRad:",radY-lineRad)
			printRadian(fp,u"sin(radY-lineRad:)",math.sin(radY-lineRad))
			#ねじれ防止
			if math.sin(radY-lineRad)>0:
				radY=invert(radY)

			lineRad=lineDir(start,end)

			printRadian(fp,u"lineRad:",lineRad)
			adjustedRad=radY
			printRadian(fp,u"diffRad:",diffRad)
			squareRad=lineDir(start,end)
			#printRadian(u"squareRad",squareRad)
			printRadian(fp,u"変換後描画角度:",radY)
			v.set(LEFT)
			#1〜√2 の範囲になってほしい
			coef=(1+0.41421356237*math.fabs(math.sin(diffRad*0.5)))
			fp.write("coef="+str(coef))
			v.x*=coef
			v.rotate(adjustedRad)
			flag = False
			outVertexArray.append([start+v,flag])
			v.set(RIGHT)
			v.x*=coef
			v.rotate(adjustedRad)
			flag = True
			outVertexArray.append([start+v,flag])
			lastRad=originalRad;
			lastUsedRad=adjustedRad
			fp.write("\n")
		#最後の締めくくり
		fp.write(str(i)+u"番目の頂点")
		adjustedRad=originalRad
		printRadian(fp,u"最後の描画角度:",originalRad)
		v.set(LEFT)
		v.rotate(adjustedRad)
		flag = False# if originalRad< 0 else False
		outVertexArray.append([end+v,flag])
		v.set(RIGHT)
		v.rotate(adjustedRad)
		flag = True# if originalRad< 0 else False
		outVertexArray.append([end+v,flag])
		fp.close()
		return outVertexArray

class StripLineEffect(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		#ユーザーから受け取ったパラメータの読み込み
		self.OptionParser.add_option("-f", "--linewidth",
						action="store", type="string",
						dest="linewidth", default="10",
						help=u"線の太さ")
		#ログファイル名
		self.OptionParser.add_option("-g", "--logfilename",
						action="store", type="string",
						dest="logfilename", default="10",
						help=u"ログファイルの名前")
	#エフェクトの挙動を書きます
	def effect(self):
		linewidth=int(self.options.linewidth)
		# メインのルート要素であるSVGを取得
		svg = self.document.getroot()
		pathlist=svg.findall(ALL+"{"+inkex.NSS['svg']+"}path")

		for path in pathlist:
			if path == None:
				inkex.errormsg(u"パスを書いてください！！")
			#パスの頂点座標を取得
			vals=simplepath.parsePath(path.get('d'))
			bone=[]
			for cmd,vert in vals:
				#たまに空のが入ってるため、それ対策
				if len(vert) != 0:
					bone.append(Vertex(vert[0],vert[1]))
			outVertexArray=stripline(bone,linewidth,self.options.logfilename)

			pointer=0
			for t in range(len(outVertexArray)-2):
				tri=Triangle(outVertexArray[pointer][0],outVertexArray[pointer+1][0],outVertexArray[pointer+2][0])

				stripstr=tri.toSVG()
				color2="blue"
				if outVertexArray[pointer][1]:
					color="blue"
				else:
					color="red"
				pointer+=1
				attributes={"points":stripstr,
				"style":"fill:"+color2+";stroke:"+color2+";stroke-width:"+str(linewidth/3),"fill-opacity":"0.5"}
				pth =inkex.etree.Element("polygon",attributes)
				svg.append(pth)
			pointer=0
			#＋−を示す点を描く
			for t in range(len(outVertexArray)):

				if outVertexArray[pointer][1]:
					point=Plus(outVertexArray[pointer][0].x,outVertexArray[pointer][0].y,linewidth/3)
					color="blue"
				else:
					point=Minus(outVertexArray[pointer][0].x,outVertexArray[pointer][0].y,linewidth/3)
					color="red"
				if pointer==0:
					color="#6f0018"#暗い赤
				point.appendToSVG(color,svg)
				#svg.append(Circle.toSVG(outVertexArray[pointer][0].x,outVertexArray[pointer][0].y,linewidth/3,color,0))
				pointer+=1
			pointer=0
			pathstr="M "
			for t in range(len(outVertexArray)):
				pathstr+=str(outVertexArray[pointer][0].x)+" "+str(outVertexArray[pointer][0].y)+" "
				pointer+=1

			att3={"d":pathstr,"r":"1","fill":"none","stroke-width":"1","stroke":"white"}
			pt=inkex.etree.Element("path",att3)

# エフェクトインスタンスを作って、適用します
effect = StripLineEffect()
effect.affect()

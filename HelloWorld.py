#!/usr/bin/env python
#coding: UTF-8
# 上の２行はおまじない的に必要なコードです。
import sys,os
#sys.path.append('/usr/share/inkscape/extensions')
#sys.path.append(os.path.dirname(sys.argv[0]))  #?
sys.path.append("/Applications/Inkscape.app/Contents/Resources/extensions")
# inkscapeのモジュールを使うためにinkexをインポートします
import inkex
import gettext
_ = gettext.gettext
# simplestyleモジュールはスタイルのパースをするのに使います
from simplestyle import *
inkex.errormsg(_(u"エラーメッセージテスト"))
class HelloWorldEffect(inkex.Effect):
	"""
	Inkscape effect 拡張のサンプル
	 "Hello World!" の文字が真ん中に配置された新しいレイヤーを作ります
	"""
	def __init__(self):
		"""
		コンストラクタ
		Defines the "--what" option of a script.
		"""
		# 基底クラスのコンストラクタを呼びます
		inkex.Effect.__init__(self)

		# Define string option "--what" with "-w" shortcut and default value "World".
		self.OptionParser.add_option('-w', '--what', action = 'store',
		  type = 'string', dest = 'what', default = 'World',
		  help = 'What would you like to greet?')

	def effect(self):
		"""
		エフェクトの挙動を書きます
		Overrides base class' method and inserts "Hello World" text into SVG document.
		"""
		# Get script's "--what" option value.
		what = self.options.what

		# メインのルート要素であるSVGを取得
		svg = self.document.getroot()
		# or alternatively
		# svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]

		# SVGの属性をゲットのやり方、２通りあります SVGタグにあるwidth属性をゲット
		width  = inkex.unittouu(svg.get('width'))
		height = inkex.unittouu(svg.attrib['height'])
		g=inkex.etree.SubElement(svg, 'g')
		img=inkex.etree.SubElement(g,"image")
		inkex.errormsg(_(u"画像"+str(img)))
		# 新しいレイヤーを作ります
		layer = inkex.etree.SubElement(svg, 'g')
		layer.set(inkex.addNS('label', 'inkscape'), 'Hello %s Layer' % (what))
		layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

		#SVGにテキスト要素を作ります
		text = inkex.etree.Element(inkex.addNS('text','svg'))
		text.text = 'Hello %s!' % (what)

		# テキストの位置をドキュメントの真ん中に置きます
		text.set('x', str(width / 2))
		text.set('y', str(height / 2))
		# テキストの配置をCSSで真ん中寄せにします
		style = {'text-align' : 'center', 'text-anchor': 'middle'}
		text.set('style', formatStyle(style))

		# 要素を一つにします
		layer.append(text)

# エフェクトインスタンスを作って、適用します
effect = HelloWorldEffect()
effect.affect()

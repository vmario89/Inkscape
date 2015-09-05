# インストールの仕方
## 環境
[Inkscape0.91以上](https://inkscape.org/ja/)がインストールされているPC
### スクリプトを置く場所 Macの場合
> /Users/ユーザー名/.config/inkscape/extensions

に`delauney_from_path.py`と`delauney_from_path.inx` を置いてinkscapeを立ち上げ直します
これでインストールは完了です。

## Polygonal Mosaicの作り方
まずinkscapeで画像を開きます
> File->Open->画像を選ぶ

画像はlinkにします。embed形式の画像（画像データをSVGに埋め込む）はまだ非対応です。

デフォルトで次のようにfile://がついていたら動きません。
`file:///Users/ユーザー名/Pictures/画像ファイル.jpg`
次のように直してください。file://の部分を取り除きます
`/Users/ユーザー名/Pictures/画像ファイル.jpg`


です。
Pathツールを使って点を打ちます

点を打っていきます。
パスは閉じないようにしてください。
複数のPathがあってokです

描いたパスをすべて選択した状態で
このスクリプトメニューの場所はinkscapeのメニューの
> Extenstions->Generate from Path->★Delauney from path

を実行します

#### 上手に作るコツ
* 画像全体を四角いパスで囲む
* 輪郭だけではなく隆起させたいところ、凹ませたいところにも点を打つ


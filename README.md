# 大阪方言アクセント生成器

東京方言のアクセントラベル (OpenJTalk の自動推定によるもの) から大阪方言のアクセントラベルを自動的に生成するためのプログラム．

大阪方言アクセントは，以下のリンクのルールに従って導出されています．

https://hackmd.io/@Kzyfn/S1Mcaa9NK

必要なライブラリ

```
pyopenjtalk
numpy
pandas
```

# 使用方法

```python translator.py [ラベルがほしいテキスト]```

## 出力例:
1 が H ラベル， 0 が L ラベルを表す．

```
$ python translator.py 公園を走る
公園を走る
[1.0, 1.0, 1.0, 1.0, 1, 1.0, 1.0, 1.0]
```


```
$ python translator.py "楽しそうなのでやりたいです"
楽しそうなのでやりたいです
辞書がありません．東京方言アクセントラベルを返します．接続助詞: ので
[1.0, 1.0, 1.0, 1.0, 0.0, 0, 1.0, 0.0, 1.0, 1.0, 0, 0, 0, 0]
```


## 備考
21/11/15 現在，全ての助詞・助動詞のアクセントラベルを用意することはできておらず，一部の助詞・助動詞で東京方言アクセントラベルをそのまま返すような挙動をします．(時間があれば改良予定))

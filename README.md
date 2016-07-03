# word2vec
有一天，小明和他的快樂夥伴想要到海邊玩...
- 小明 : 炎炎夏日，不就應該到海邊尋找**陽光**、**沙灘**、**比基尼**嗎？
- 夥伴1 : 但是週末颱風要來了耶，海邊很危險吧
- 夥伴2 : 對呀...難不成要去衝浪嗎？大家找家餐廳聚聚就好？
- 小明 : 不如我們來訂一家有陽光、沙灘、比基尼的餐廳吧！
- 眾人 : ...蛤？
- 小明 : 這交給 **EZTABLE** 不就得了？

##### 這是一篇關於如何透過情境搜尋餐廳的文章，太長可以直接 END 看結果。

# 專案緣起
不知道大家最近有沒有看到一篇 PTT 上的文章？作者對約 X 信進行語義分析，內容專業到讓人無法直視，看的當下就覺得：哇！原來語意分析還有這種應用的方式！程式語言是用來幫忙解決問題的好工具，能把它應用到生活大小事上真的很棒！這篇文章燃起了我心中對文字探勘的熱情，剛好最近有個比賽會需要這方面的技術~~（才不是因為 PIXNET HACKTHON 的比賽入選機率極低而抱著不服輸的心態呢！）~~

由於本身對資料分析很有興趣，尤其是圖像分析和語意分析，因為他們能夠應用的範疇很廣，而且已經不知不覺地影響著這個世界的運行，例如無人車駕駛、Alphago、SkyRec、IBM Waston 等等。這個領域的知識又深又廣，既然要朝這個方向持續邁進，平常就要有所累積。公司正在朝著將情境與餐廳建立連結轉型，正好和我有興趣的領域有所重疊，所以對於這個專案我也有比平常玩玩還認真的使命感，於是便花了星期六和星期日的上午把做了一些有趣的東西。

# 工具介紹
大多數的公司使用 Solr, Elasticsearch 建置搜尋引擎，更甚者直接嵌入 Google 搜尋列，前者運用的方法是 TF-IDF，簡單來說就是...。但是這個方法有著天生難以克服的缺點...。
也因此想要透過搜尋引擎搜尋情境、模糊搜尋就要使用別種技術，Word2Vec 就是一個很適合的工具，他的原理如下：

# 操作流程
**1. 收集連結**：收集公司合作餐廳的食記連結，並且把餐廳資訊與餐廳食記連結輸出成文字檔，檔案內沒有提供連結。

執行`python getUrl.py`

**2. 爬網站 & 擷取資訊**：過濾非 Pixnet 連結透過 requests 結合 multiprocessing 爬網站的 Html。使用 PyQuery 擷取網站標題與內容，並且存到 Sqlite。

執行`python getBlog.py`

**3. 斷詞**：使用 Jieba 對文字進行預處理，轉換成 Word2Vec 能夠訓練的格式。

執行`python cut.py`

**4. 訓練**：透過在 gensim 中實作的 Word2Vec，設定參數對資料進行訓練，產生詞向量與模型。（直接使用 52nlp 提供的檔案）

執行`python train_word2vec_model.py training_sentence.txt model_name.model vector_name.vector`

# 注意事項
在專案中主要遇到兩個困難：
1. 處理中文字遇到的編碼問題：Unicode、UTF-8 與 ASCII 之間錯綜複雜的關係，不同套件的輸入的接口要求的編碼可能不一樣。
2. 使用 multiprocess 要小心：原因還沒有弄清楚，只要在 `the_function` 裡面加入了 pyquery 或是 sqlite 的 function 就會 crash，但是放 requests 就沒事。

```python
from multiprocessing import Pool
p = Pool(5)
results = p.map(the_fucntion, inputs)
```
# 專案成果

1. 先載入 gemsim 套件與剛剛訓練好的 model
```python
import gensim
# print result
def ps(result):
  if result:
  for e in result:
    print e[0], e[1]
# load fresh model
  model = gensim.models.Word2Vec.load("articles_rname.model")
```
接下來就可以開始玩啦！我很愛吃水餃，但是昨天才剛吃過，有沒有什麼類似的料理可以推薦給我呢？
```python
>>> result = model.most_similar(u"水餃",topn=5)
>>> ps(result)
叉燒包 0.732798755169
蔥油餅 0.717539072037
三鮮 0.706256866455
餃子 0.703786492348
包子 0.694874405861
```
詞向量有個特性是可以透過相加減獲得有趣的結果，例如：國王 - 男人 + 女人 ~= 皇后。以此類推，如果當我們想要知道泰式之於瓦城，就像是義式之於什麼餐廳，就可以這樣計算：  瓦城 - 泰式 + 義式 =  ?
```python
>>> result = model.most_similar(positive=u"義式 瓦城".split(" "), negative=[u"泰式"],topn=5)
>>> ps(result)
義大利餐廳 0.754565596581
NINI 0.750810861588
帕莎 0.707847952843
廚子市場 0.703588843346
蒂娜 0.700719475746
```
得出來的結果是在義式餐廳中，風格與瓦城最像的前五名餐廳。但是，在這裡我們發現了一個問題，「義大利餐廳」是哪一家？答案是義大皇家酒店的義大利餐廳，NINI 呢？原來是 Le NINI 樂尼尼義式餐廳，帕莎和蒂娜應該要合起來叫做帕蒂娜莎，產生問題的原因是之前在處理餐廳名稱的時候不夠謹慎。目前會先用 mapping 的方式找回原本的餐廳名稱。

接下來我們要進入重頭戲，情境搜尋了！
```python
>>> result = model.most_similar(u"夏天 海灘 餐廳".split(" "), topn=5)
>>> ps(result)
皮椅 0.694285988808
LOUNGE 0.688326239586
HALEAKALA 0.68235886097
仿舊 0.674678146839
小徑 0.662850260735
```
我們想要的結果是根據情境找到符合的餐廳，但是得出的結果只有2家餐廳，2個名詞，1個形容詞。因此我們必須建立涵蓋訓練集餐廳的 list，把這個 list 的詞向量拿出來與我們想要搜尋的情境詞向量進行相似度的計算。特別感謝 jimgoo 提供的 `most_similar_in_list` function，讓我可以直接使用。
```python
>>> print(rname_list[:5])
[u'Follow', u'Bellini', u'TABLE', u'Taverna', u'90']
>>> print(mapping(rname_list[:5]))
[u'Follow Lady 法蕾蒂', u'Bellini Pasta Pasta', u'TABLE JOE 喬桌子廚房', u'Taverna De  Medici 梅帝騎小酒館', u'90 a la sante 酒食歐風朝']

>>> result = model.most_similar_in_list(u"夏天 海灘".split(" "), topn=5, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
VG Cafe & Bistro 0.650945961475
HALEAKALA 夏威夷酒吧餐廳 0.615895032883
Eslite Tea Room 0.599678635597
URBAN331-台北慕軒飯店 0.579266548157
Destino 妳是我的命運 0.57857131958

>>> result = model.most_similar_in_list(u"消暑 下午 茶".split(" "), topn=3, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
Caldo Cafe咖朵咖啡 0.47723197937
Eslite Tea Room 0.468698769808
H-Bar 0.460396289825

>>> result = model.most_similar_in_list(u"正妹 店員".split(" "), topn=3, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
etage15-高雄Hotel dua 0.468320250511
Sunny Cafe 0.447554886341
Kevin Coffee 0.418976008892

>>> result = model.most_similar_in_list(u"音樂 悠閒".split(" "), topn=3, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
Mammoth lounge 0.670462846756
HALEAKALA 夏威夷酒吧餐廳 0.626639544964
RUBY CAFE 0.6229159832

>>> result = model.most_similar_in_list(u"工程師".split(" "), topn=3, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
American Steakhouse 0.802481234074
i sweet 0.785791814327
Silk Road Feast 絲路宴餐廳 0.776082456112

>>> result = model.most_similar_in_list(u"求婚 紀念".split(" "), topn=3, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
Ton Up Cafe 0.62010884285
TABLE JOE 喬桌子廚房 0.608335494995
URBAN331-台北慕軒飯店 0.606325864792

>>> result = model.most_similar_in_list(u"酒 餐廳 美式 跨年".split(" "), topn=3, restrict_vocab=rname_list)
>>> ps([[mapping(rname[0]), rname[1]] for rname in result])
bar & restaurant a³ 新義式餐廳 0.665651142597
MW 時尚義法料理&酒品 0.665459275246
Le Bar 吧 戶外餐廳 0.644170224667
```


# 特別感謝
python 有很多好用的套件，像是中文斷詞有 jieba，word2vec 有 gensim，用起來上手很快，而且還有熱心的大大們不吝分享與教學

# -*- coding: utf-8 -*-

import logging
import os.path
import sys
import jieba
import sqlite3
import re

MOVEPATTERN = re.compile(ur'搬家', re.UNICODE)
RNAMEPATTERN = re.compile(ur'\w+',re.UNICODE)

# Filter punct in English or Chinese: https://github.com/fxsjy/jieba/issues/169
punct = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…~/ －＊➜■─★☆=@<>◉é''')
# for str/unicode
filterpunt = lambda s: ''.join(filter(lambda x: x not in punct, s))

query_type_mapping = {
	"rname": "SELECT DISTINCT r_name, b_content FROM blogs",
	"btitle": "SELECT DISTINCT b_title, b_content FROM blogs"
}

def processText(string):
	new_string = ''
	if string:
		new_string = ''.join(map(filterpunt, string.strip()))
	return new_string


if __name__ == '__main__':
	program = os.path.basename(sys.argv[0])
	logger = logging.getLogger(program)

	logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
	logging.root.setLevel(level=logging.INFO)
	logger.info("running %s" % ' '.join(sys.argv))

	# jieba for traditional Chinese 
	jieba.set_dictionary('/Library/Python/2.7/site-packages/jieba/data/dict.txt.big')
	# custom dictionary for remaining these restaurant names
	jieba.load_userdict('/Users/Feelings/Programming/eztable/word2vec/ENV/lib/python2.7/site-packages/jieba/data/userdict.txt')
	
	# connect db
	conn = sqlite3.connect('blog.db')
	c = conn.cursor()

	"""TYPES OF TRAINING DATA:
		rname: rname + bcontent (default)
		btitle: btitle + bcontent
	"""
	coupus_type = "rname"
	query = query_type_mapping[coupus_type]
	output = open("articles_{}.txt".format(coupus_type), "w")
	i = 0

	for row in c.execute("""{}""".format(query)):
		if coupus_type == "rname":
			title = re.match(RNAMEPATTERN, row[0])
			title = title.group() if title else ""

			article = processText(row[1]) if MOVEPATTERN.search(row[1]) is None else ""
			article_words = jieba.lcut(article)

			corpus_words = [title] + article_words
		elif coupus_type == "btitle":
			title = processText(row[0])
			article = processText(row[1]) if MOVEPATTERN.search(row[1]) is None else ""

			title_words = jieba.lcut(title)
			article_words = jieba.lcut(article)

			corpus_words = title_words + article_words
		else:
			try:
				raise TypeError("Corpus")
			except TypeError:
				print 'Please check the corpus type again.'
				raise

		i += 1
		if i % 500 == 0:
			logger.info("Saved " + str(i) + " articles")
		if title and article:
			output.write((u" ".join(corpus_words) + u"\n").encode('utf-8'))

	output.close()
	logger.info("Finished Saved " + str(i) + " articles")
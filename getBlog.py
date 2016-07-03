# coding=UTF-8
import json
import csv
import ast
import requests
import sqlite3
import re
from pyquery import PyQuery
import time
import random
from multiprocessing import Pool

TEXTPATTERN = re.compile(r"[\'\"]")
PIXNETURLPATTERN = re.compile(r'.*blog/post/\d+')

PROXY = "http://www..."

# Use PyQuery parse html
def parseBlog(html):
	pq = PyQuery(html)
	result = {}
	result["title"] = getText(pq("#content .title").text()).encode('utf-8')
	result["content"] = getText(pq(".article-content").text()).encode('utf-8')
	return result

# clean text
def getText(text):
	new_text = ''
	if text:
		new_text = re.sub(TEXTPATTERN, "", text)
	return new_text

# Send request to get html
def getBlogContent(data):
	url_list = data[0]
	html_list = []

	for url in url_list:
		# set random sleep time to avoid being blocked
		timeToSleep = float(random.randint(15, 30)) / 300
		time.sleep(timeToSleep)
		proxy_url = PROXY

		print("fetching blog...{}".format(url))
		# Request html by proxy
		r = requests.get(proxy_url, params={"data":url})
		# Or by local
		# r = requests.get(url)
		r.encoding = 'utf-8'

		html = r.text
		html_list.append(html)
	return tuple([data, html_list])

if __name__ == '__main__':
	# Get blog links, rastaurant name and id 
	with open('rname_rid2.csv', 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ')
		blog_list = []
		for row in reader:
			url_list = [PIXNETURLPATTERN.search(url).group() for url in ast.literal_eval(row[0]) if PIXNETURLPATTERN.search(url)]
			row[0] = url_list
			blog_list.append(row)

	result_list = []
	startPoint = 0
	endPoint = 1

	p = Pool(5)
	# Send request to get html
	results = p.map(getBlogContent, blog_list[startPoint:endPoint])
	# Parse html and append to a list
	for data, html_list in results:
		for html in html_list:
			pq = PyQuery(html)
			result = {}
			data[1] = getText(data[1]) # restaurant name
			result["title"] = getText(pq("#content .title").text()) # blog title
			result["content"] = getText(pq(".article-content").text()) # blog content
			index = html_list.index(html) # blog index of the restaurant 
			url = data[0][index] # blog url
			b_id = "{}-{}".format(data[2], index) # r_id + blog index
			result_list.append(tuple([data[2], data[1], b_id, url, result["title"], result["content"]]))

	conn = sqlite3.connect('blog.db')
	conn.text_factory = str

	c = conn.cursor()
	# Create table if not exists
	c.execute('''CREATE TABLE IF NOT EXISTS blogs (r_id int, r_name text, b_id text, b_url text, b_title text, b_content text)''')
	# Batch insert data into DB
	c.executemany("""INSERT INTO blogs VALUES (?,?,?,?,?,?)""", result_list)
	conn.commit()

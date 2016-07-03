import csv
import requests
from multiprocessing import Pool
import time
import random

data_list = []
urlpattern = ""

with open("rname_rid.csv", "r") as f:
    reader = f.read().split("\n")
    for row in reader:
        data = {}
        new_row = row.split("\t")
        data["name"] = new_row[0]
        data["id"] = new_row[1]
        data_list.append(data)


def sendRequest(url):
	timeToSleep = float(random.randint(15, 30)) / 100
	time.sleep(timeToSleep)

	r = requests.get(url)
	return r.json()

def getUrl(data):
    id = data["id"]
    result = sendRequest(urlpattern.format(id))

    if result:
        url_list = []
        for row in result:
            url_list.append(row["url"])
            print("{} fetching...{}".format(id, row["url"].encode('utf-8')))
        data["url"] = url_list
        return data

if __name__ == '__main__':

    startPoint = 0
    endPoint = 3000
    p = Pool(5)

    blog_list = p.map(getUrl, data_list[startPoint:endPoint])
    blog_list = [blog for blog in blog_list if blog is not None]

    # Write blog links, rastaurant name and id 
    csvfile = open('input.csv', 'a')
    writer = csv.writer(csvfile, delimiter=' ')
    for blog in blog_list:
        writer.writerow(blog.values())
    csvfile.close()
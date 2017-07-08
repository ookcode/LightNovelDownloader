#!/usr/bin/python3
#coding=utf-8
import sys
if not sys.version_info[0] == 3:
	print("当前脚本只能在python3.x下运行，请更换您的python版本！")
	sys.exit()
	
import os
import urllib
import requests
import threading
import re
import json

ROOT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
BASE_URL = "http://q.dmzj.com"

HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

class Downloader:
	def __init__(self, novelId):
		self.session = requests.Session()
		self.session.headers = HEADERS
		
		self.novelId = novelId
		self.novelName = ""

	def start(self, minChapter = 0):
		response = self.session.get('{}/{}/index.shtml'.format(BASE_URL, self.novelId))
		if response.status_code != 200:
			return
		downloadThreads = []
		for line in response.text.split("\n"):
			if self.novelName == "":
				self.novelName = self._getWrapped(line, "var g_lnovel_name = '", "';")
			elif re.search('volume_list\[[0-9]+\]', line):
				title = self._getWrapped(line, '<div class="chapnamesub">', '</div><div class="chapname_div"')
				url = self._getWrapped(line, 'href="', '">下载到手机')
				if len(title) > 0 and len(url) > 0:
					t = threading.Thread(target=self._download,args=(title, url))
					downloadThreads.append(t)

		if len(downloadThreads) == 0:
			print("No.{} {} 被魔女干掉了。".format(self.novelId, self.novelName))
			return
		elif len(downloadThreads) < minChapter:
			print("No.{} {} 卷数太少被您过滤掉了。".format(self.novelId, self.novelName))
			return
		print("No.{} {} 开始下载".format(self.novelId, self.novelName))
		dirPath = os.path.join(ROOT_PATH, self.novelName)
		if not os.path.exists(dirPath):
			os.mkdir(dirPath)
		for t in downloadThreads:
			t.start()

	def _getWrapped(self, text, beginKey, endKey):
		match = re.findall('{}.*{}'.format(beginKey, endKey), text)
		if len(match) == 1:
			return match[0][len(beginKey) : -len(endKey)]
		return ""

	def _download(self, title, url):
		'''
		a:已经下载的数据块
		b:数据块的大小
		c:远程文件的大小
		'''
		def schedule(a, b, c):
			per = a * b / c
			if per > 1 :
				print("\t下载完成:", title)

		save_path = os.path.join(ROOT_PATH, self.novelName, title + ".txt")
		try:
			urllib.request.urlretrieve(url, save_path, schedule)
		except Exception as e:
			print("\t下载失败:", title)
		

class Searcher:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers = HEADERS

	def _searchBook(self, searchName):
		'''
		"author":
	    "image_url":
	    "lnovel_name":
	    "last_chapter_name":
	    "lnovel_url":
	    "last_chapter_url":
	    "full_name":
	    "fullc_name":
	    "types":
	    "status":
	    "description":
	    '''
		response = self.session.get('http://s.acg.dmzj.com/lnovelsum/search.php?s={}'.format(searchName))
		if response.status_code == 200:
			content = response.text
			prefix = "var g_search_data = "
			data = json.loads(content[len(prefix):-1])			
			for index, book in enumerate(data):
				print(index, "《" + book['full_name'] + "》")
				print("类型:", book['types'])
				print("作者:", book['author'])
			return data

	def start(self):
		selectNovelId = None
		searchName = input("请输入轻小说名称(输入n退出):")
		if searchName == "n":
			print("谢谢使用！")
			sys.exit()
		data = self._searchBook(searchName)
		if len(data) == 0 :
			print("呜呜，没有搜索到相关轻小说，建议缩短关键词进行搜索，记得考虑译名方式和繁简体哦！\n" + "-" * 40)
			self.start()
			return
		print("-" * 40)
		while(True):
			number = 0 if len(data) == 1 else int(input("请输入序号:"))
			if 0 <= number < len(data):
				print("您选择了","《" + data[number]['full_name'] + "》")
				mixUrl = data[number]['lnovel_url']
				beginPos = mixUrl.find('../') + 3
				endPos = mixUrl.find('/',beginPos)
				selectNovelId = int(mixUrl[beginPos : endPos])
				break
			else:
				print("输入有误！")

		downloader = Downloader(selectNovelId)
		downloader.start()

def main():
	print("0、搜索下载\t\t1、整站下载")
	print("-" * 40)
	while(True):
		number = int(input("请输入序号:"))
		if number == 0:
			search = Searcher()
			search.start()
			break
		elif number == 1:
			for novelId in range(1, 2500):
				downloader = Downloader(novelId)
				downloader.start(minChapter = 3)
			break
		else:
			print("输入有误！")

if __name__ == '__main__':
	main()

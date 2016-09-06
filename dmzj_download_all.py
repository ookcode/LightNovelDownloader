#!/usr/bin/python3
#coding=utf-8
import sys
if not sys.version_info[0] == 3:
	print("当前脚本只能在python3.x下运行，请更换您的python版本！")
	sys.exit()
	
import os
import urllib.request
import threading
import re
import json
import platform
from bs4 import BeautifulSoup

#脚本运行目录
ROOT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
#过滤低于此浏览量的小说
MIN_VISITER_COUNT = 1000000

class DMZJ:
	def __init__(self):
		self.downloadThreads = []
		self.baseUrl = "http://xs.dmzj.com"
		self.html = ""
		self.novelName = ""
		self.novelId = None
		self.minVisiterCount = MIN_VISITER_COUNT

	def _getHtml(self):
		url = self.baseUrl + "/" + str(self.novelId) + "/index.shtml"
		try:
			request = urllib.request.Request(url)
			response = urllib.request.build_opener().open(request)
		except Exception as e:
			return ""

		return response.read().decode('utf-8')

	def _analysis(self):
		try:
			soup = BeautifulSoup(self.html)
			self.novelName = str(soup.find(class_ = "novel_cover_text").find("h1").string)
			visiters = int(str(soup.find("span", class_ = "fontorange12").string)[:-1])
			if visiters >= self.minVisiterCount:
				log = open(os.path.join(ROOT_PATH,'log.md'), 'a+')
				for chapter in soup.find_all(class_="download_rtx"):
					title = list(chapter.find('li').strings)[1]
					url = chapter.find(class_="download_boxbg").find('a')["href"]
					#替换不符合目录命名规范的特殊字符
					if 'Windows' in platform.system():
						title = re.sub('[\/:*?"<>|]', ' ', title)
					else:
						title = title.replace('/','\\')
					#print(title, url)
					t = threading.Thread(target=self._download,args=(title,self.baseUrl + url))
					self.downloadThreads.append(t)
		except Exception as e:
			pass
		else:
			if visiters >= self.minVisiterCount:
				print(self.novelId, self.novelName,str(visiters) + "人阅读")
				return True
		return False

	def _download(self, title, url):
		'''
		a:已经下载的数据块
		b:数据块的大小
		c:远程文件的大小
		'''
		def schedule(a, b, c):
			per = a * b / c
			if per > 1 :
				print(title,"下载完成")
		try:
			save_path = os.path.join(ROOT_PATH, self.novelName, title + ".txt")
			urllib.request.urlretrieve(url, save_path, schedule)
		except Exception as e:
			print("下载失败", e)

	def clean(self):
		self.downloadThreads = []
		self.html = ""
		self.novelName = ""
		self.novelId = None

	def start(self, novelId):
		self.clean()
		self.novelId = novelId
		self.html = self._getHtml()
		if self._analysis():
			#print("-" * 40,"\n开始下载...")
			dirPath = os.path.join(ROOT_PATH, self.novelName)
			if not os.path.exists(dirPath):
				os.mkdir(dirPath)
			for t in self.downloadThreads:
				t.start()

def thread_func(novelId):
	downloader = DMZJ()
	downloader.start(novelId)

def main():
	threads = []
	for i in range(0,2500):
		t = threading.Thread(target=thread_func,args=(i,))
		threads.append(t)

	for t in threads:
		t.start()
		t.join()


if __name__ == '__main__':
	main()

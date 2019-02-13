import requests
import re
import subprocess
import os
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}


def GetVideoinfoURL(mainURL):
	response = requests.get(mainURL, headers=headers).text

	FrontpartVideoinfoURL = 'http://afbbs.afreecatv.com:8080/api/video/get_video_info.php?'

	pattern = re.compile("VodParameter\s=\s'(.*?)'", re.S)
	items = re.findall(pattern, response)
	LatterpartVideoinfoURL = str(items[0])

	CompleteVideoinfoURL = FrontpartVideoinfoURL + LatterpartVideoinfoURL
	return CompleteVideoinfoURL


def GetPlaylistURL(video_info_url):
	response = requests.get(video_info_url,headers=headers).text
	pattern = re.compile('duration=".*?"\skey="(.*?)"', re.S)
	items = re.findall(pattern, response)

	PlaylistURLList = []
	for item in items:
		slicelist = item.split('_')
		slicelistElement = slicelist[1]+'_'+slicelist[2]+'_'+slicelist[3]
		PlaylistURL = 'http://videofile-hls-ko-record-cf.afreecatv.com/video/_definst_/smil:vod/{}/{}/{}.smil/playlist.m3u8'.format(slicelist[0], slicelist[2][-3:],slicelistElement)
		PlaylistURLList.append(PlaylistURL)
	""" print(PlaylistURLList) """
	return PlaylistURLList


def DownloadPlaylistFile(PlaylistURL,index):
	content = requests.get(PlaylistURL, headers=headers).content
	with open('playlist{}.m3u8'.format(index), 'wb') as f:
		f.write(content)
		f.close
		

def GetIndexURL(PlaylistURL, index):
	f = open('playlist{}.m3u8'.format(index), 'r')
	result = list()
	for line in open('playlist{}.m3u8'.format(index)):
		line = f.readline().strip('\n')
		result.append(line)
	f.close()
	print(str(result[3]))
	m3u8_url = str(result[3])
	return m3u8_url


def DownloadIndexFile(m3u8_url, index):
	content = requests.get(m3u8_url, headers=headers).content
	with open('index{}.m3u8'.format(index), 'wb') as f:
		f.write(content)
		f.close
	

def GetTSURL(m3u8_url, index):
	f = open('index{}.m3u8'.format(index), 'r')
	result = list()
	for line in open('index{}.m3u8'.format(index)):
		line = f.readline().strip('\n')
		result.append(line)
	f.close()
	last_number = result[-2][-7:-3]

	if last_number.isdigit() is True:
		pass
	else:
		last_number = result[-2][-6:-3]

	tsURLList = []
	last_number = int(last_number) + 1
	for i in range(0, last_number):
		ts_url = m3u8_url.replace('chunklist', 'media').replace('.m3u8', '_{}.ts'.format(i))
		tsURLList.append(ts_url)
	return tsURLList, last_number



def DownloadTSFile(downloadList, index):
		for url in downloadList:
			subprocess.call(['wget', '-c', url])
		subprocess.call(['ffmpeg', '-i', 'index{}.m3u8'.format(index), '-c', 'copy', '{}.mp4'.format(index)])
		
		for root, dirs, files in os.walk(os.getcwd()):
			for name in files:
				if name.endswith(".ts"):
					os.remove(os.path.join(root, name))
				if name.endswith(".m3u8"):
					os.remove(os.path.join(root, name))


def calculate_file_number():
	DIR = os.getcwd()
	number = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
	return number


def main():
	mainURL = input("input URL:")
	video_info_url = GetVideoinfoURL(mainURL)
	PlaylistURLList = GetPlaylistURL(video_info_url)

	index = 1
	for PlaylistURL in PlaylistURLList:
		DownloadPlaylistFile(PlaylistURL, index)
		m3u8_url = GetIndexURL(PlaylistURL, index)
		DownloadIndexFile(m3u8_url, index)
		tsURLList, last_number = GetTSURL(m3u8_url, index)

		downloadList = []
		for ts_url in tsURLList:
			downloadList.append(ts_url)
		
		DownloadTSFile(downloadList, index)
		index = index + 1
		
		""" initial_number = calculate_file_number()
		theory_all_number = initial_number + last_number
		practical_all_number = theory_all_number - 50 """

if __name__=='__main__':
	main()
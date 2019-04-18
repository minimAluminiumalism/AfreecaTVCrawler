import requests
import re
import subprocess
from bs4 import BeautifulSoup


class AfreecaSpider(object):
    def __init__(self):
        self.base_url = "http://vod.afreecatv.com/PLAYER/STATION/40965797"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        }
        self.video_info_url = "http://afbbs.afreecatv.com:8080/api/video/get_video_info.php?type=station&isAfreeca=true&autoPlay=true&showChat=true&expansion=true&{}&{}&{}&{}&{}&szPart=REVIEW&szVodType=STATION&szSysType=html5"
    
    def get_video_info_url(self):
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            video_info_url = soup.find("head").find("meta", {"name":"twitter:player"})["value"]
            
            patterns = re.compile("szBjId=(.*?)&.*?nStationNo=(.*?)&.*?nBbsNo=(.*?)&.*?nTitleNo=(.*?)&.*?szCategory=(.*?)&", re.S)
            elem_dict = {}
            elem_list = re.findall(patterns, video_info_url)
            elem_dict["szBjId"] = elem_list[0][0]
            elem_dict["nStationNo"] = elem_list[0][1]
            elem_dict["nBbsNo"] = elem_list[0][2]
            elem_dict["nTitleNo"] = elem_list[0][3]
            elem_dict["szCategory"] = elem_list[0][4]

            url_elem_list = []
            for key, value in elem_dict.items():
                url_elem_list.append("{}={}".format(key, value))
            video_info_url = self.video_info_url.format(url_elem_list[0], url_elem_list[1], url_elem_list[2], url_elem_list[3], url_elem_list[4])
            return video_info_url
        
        else:
            print(response.status_code, "failed to get video info.")
            return None


    def get_all_playlist(self, video_info_url):
        response = requests.get(video_info_url, headers=self.headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            items = soup.find("video", thumbnail="true").find_all("file")
            

            m3u8_playlist_list = []
            patterns = re.compile("http(.*?)m3u8", re.S)
            for item in items:
                url = re.findall(patterns, str(item))
                m3u8_playlist_list.append("http{}m3u8".format(url[0]))
            return m3u8_playlist_list
                
            
        else:
            print(response.status_code, "failed to get all playlist.")

    def run(self):
        video_info_url = self.get_video_info_url()
        m3u8_playlist_list = self.get_all_playlist(video_info_url)
        
        index = 1
        for m3u8_playlist in m3u8_playlist_list:
            subprocess.call(["python3", "m3u8_downloader.py"])
            index += 1


if __name__ == "__main__":
    AfreecaSpider().run()
        
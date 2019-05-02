import requests
import re
import subprocess
import json
import shutil
import os
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
            print(m3u8_playlist_list)
            return m3u8_playlist_list
                
            
        else:
            print(response.status_code, "failed to get all playlist.")

    def get_video_name(self):
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            name = soup.find("dt", id="title_name").text

            return name 
        else:
            print(response.status_code, " failed to get video name")


    def download_m3u8(self, m3u8_playlist):
        response = requests.get(m3u8_playlist, headers=self.headers).content
        with open("index.m3u8", "w") as f:
            f.write(response)
            f.close()

    def construct_config(self, m3u8_playlist, index, video_name):
        config_dict = {}
        config_dict["concat"] = True
        config_dict["output_file"] = "{}{}.mp4".format(video_name, index)
        config_dict["output_dir"] = "download"
        config_dict["uri"] = m3u8_playlist
        config_content = json.dumps(config_dict)
        with open("config.json", "w") as f:
            f.write(config_content)
            f.close()
        with open("config.json", "r+") as f:
            data = json.load(f)
            data["ignore_small_file_size"] = 0
            f.seek(0)
            json.dump(data, f)
            f.truncate()


    def move_files(self):
        current_path = os.getcwd()
        des_path = current_path + "/download"
        if os.path.isdir(des_path):
            #os.remove(des_path+"/index.m3u8")
            for item in os.listdir(des_path):
                shutil.move(des_path+"/{}".format(item), current_path)
            os.rmdir("download")


    def del_files(self, path):
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".ts"):
                    os.remove(os.path.join(root, name))
    
    
    def run(self):
        video_info_url = self.get_video_info_url()
        m3u8_playlist_list = self.get_all_playlist(video_info_url)
        video_name = self.get_video_name()

        path = os.getcwd()
  
        index = 1
        for m3u8_playlist in m3u8_playlist_list:
            self.download_m3u8(m3u8_playlist)
            self.construct_config(m3u8_playlist, index, video_name)
            subprocess.call(["python3", "m3u8_downloader.py"])
            self.move_files()
            subprocess.call(
			[
				'ffmpeg', '-protocol_whitelist',
				"concat,file,subfile,http,https,tls,rtp,tcp,udp,crypto",
				'-allowed_extensions', 'ALL', '-i', 'index.m3u8', '-c', 'copy',
				'{}{}.mp4'.format(video_name, index)
			]
            )
            subprocess.call(['rm', '-r', 'index.m3u8'])
            self.del_files(path)
            index += 1


if __name__ == "__main__":
    AfreecaSpider().run()
        
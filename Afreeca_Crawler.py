import requests
import re
import subprocess


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}


def get_onepage(url):
    response = requests.get(url, headers=headers).text
    return response


def parse_onepage(html):
    pattern = re.compile('rowKey=(.*?)_r', re.S)
    items = re.findall(pattern, html)
    elements = items[0].split('_')
    playlist_m3u8_url = 'http://videofile-hls-ko-record-cf.afreecatv.com/video/_definst_/smil:vod/{}/{}/{}_{}_{}.smil/playlist.m3u8'.format(
        elements[0], str(elements[2])[-3:], elements[1], elements[2], elements[3])
    return playlist_m3u8_url


def get_playlist_m3u8_file(playlist_m3u8_url):
    response = requests.get(playlist_m3u8_url).content
    
    with open('playlist.m3u8', 'wb') as f:
        f.write(response)
        f.close
        

def get_direct_m3u8_file():
    print('enter number to select' + '\n' + '1.playlist.m3u8' + '\n' + '2.index.m3u8')
    filename = input('Number:')
    a = str(filename)
    if a == '1':
        f = open('playlist.m3u8', 'r')
        result = list()
        for line in open('playlist.m3u8'):
            line = f.readline().strip('\n')
            result.append(line)
        f.close()
        print(str(result[3]))
        m3u8_url = str(result[3])
        return m3u8_url
    else:
        f = open('index.m3u8', 'r')
        result = list()
        for line in open('index.m3u8'):
            line = f.readline().strip('\n')
            result.append(line)
        f.close()
        last_number = result[-2][-6:-3]
        return last_number


def main():
    url = input('URL:')
    html = get_onepage(url)
    playlist_m3u8_url = parse_onepage(html)
    get_playlist_m3u8_file(playlist_m3u8_url)
    m3u8_url = get_direct_m3u8_file()
    merged_mp4_name = m3u8_url.split('/')[-1]
    response = requests.get(m3u8_url).content
    with open('index.m3u8', 'wb') as f:
        f.write(response)
        f.close
    last_number = int(get_direct_m3u8_file()) + 1
    for i in range(0, last_number):
        ts_url = m3u8_url.replace('chunklist', 'media').replace('.m3u8', '_{}.ts'.format(i))
        m3u8name = ts_url.split('/')
        m3u8content = requests.get(ts_url).content
        with open('{}'.format(m3u8name[-1]), 'wb') as f:
            f.write(m3u8content)
            f.close
            print(m3u8name[-1] + 'downloaded sucessfully!')
    
    subprocess.call(['ffmpeg', '-protocol_whitelist', "concat,file,subfile,http,https,tls,rtp,tcp,udp,crypto", '-allowed_extensions', 'ALL', '-i', 'index.m3u8', '-c','copy', '{}.mp4'.format(merged_mp4_name)])
    subprocess.call(['rm', 'playlist.m3u8', 'index.m3u8'])


if __name__ == '__main__':
    main()
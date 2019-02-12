import os

DIR = os.getcwd()
number = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
print(number)

""" http://bj.afreecatv.com/rlrlvkvk123/vods
http://vod.afreecatv.com/PLAYER/STATION/41278703 """
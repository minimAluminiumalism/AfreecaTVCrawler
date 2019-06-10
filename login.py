import requests
from bs4 import BeautifulSoup


login_url = "https://login.afreecatv.com/app/LoginAction.php"

form_data = {
    "szWork": "login",
    "szType": "json",
    "szUid": input("username: "),
    "szPassword": input("password: "),
    "isSaveId": "true",
    "szScriptVar": "oLoginRet",
    "szAction": ""
}

session = requests.Session()

login_in = session.post(login_url, data=form_data)
print(login_in.status_code)

m3u8_test_url = "http://afbbs.afreecatv.com:8080/api/video/get_video_info.php?type=station&isAfreeca=true&autoPlay=true&showChat=true&expansion=true&szBjId=feel0100&nStationNo=15430143&nBbsNo=36383631&nTitleNo=32986922&szCategory=00210000&szPart=REVIEW&szVodType=STATION&szSysType=html5&_=1560154642839"
response = session.get(m3u8_test_url)
print(response.text)
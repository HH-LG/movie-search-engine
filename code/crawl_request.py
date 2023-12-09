# -*- coding: utf-8 -*-

import random
from time import sleep
import requests
from bs4 import BeautifulSoup
import csv
from pygraph.classes.digraph import digraph

URL_SET = set()
REVIEW_NUM = 10
DATA_PATH = '../data/'

user_agents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
def get_headers():
    headers = {
        "User-Agent":
            random.choice(user_agents),
        "Connection":
            "keep-alive",
        "Referer":
            "https://www.douban.com"  # 站内访问
    }
    return headers

def request_douban(url, headers = get_headers()):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('被拦截了，休息一下')
            sleep(1200)
        else:
            break
    sleep(1)
    return response
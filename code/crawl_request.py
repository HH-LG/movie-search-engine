# -*- coding: utf-8 -*-
import random
from time import sleep
import requests
from bs4 import BeautifulSoup
import csv
from pygraph.classes.digraph import digraph
from urllib.parse import urlparse, urldefrag, urljoin

URL_SET = set()
REVIEW_NUM = 10
DATA_PATH = '../data/'
MOVIE_NUM = 2503

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
        if response.status_code == 200:
            break
        elif response.status_code == 404:
            print('没有找到页面:', url)
            break
        elif response.status_code == 500:
            print('服务器错误:', url)
            break
        elif response.status_code == 403 and response.text.find('检测到有异常请求') != -1:
            print('被拦截了，休息10分钟')
            sleep(600)
        else:
            print(response.status_code)
            print('其他错误:', url)
            break
    sleep(1)
    return response

def read_movie_url():
    url_list = []
    with open(DATA_PATH + 'movie_urls.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row['电影url']
            url_list.append(url)
    return url_list

def read_review_url():
    url_list = []
    with open(DATA_PATH + 'review_urls.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row['影评url']
            url_list.append(url)
    return url_list
# 特殊情况
# 1.相对链接
# 2.查询参数
def is_full_url(url):
    return url.startswith('http://') or url.startswith('https://')

# 3.锚点链接
def is_fragment_link(link):
    return '#' in link

def remove_fragment(url):
    url, _ = urldefrag(url)
    return url

# 4.javaScript链接
def is_javascript_link(link):
    return link.startswith('javascript:')

# 最后的检查：1.非法的连接
def is_valid_url(url):
    # 使用正则表达式或者urlparse来检查URL的有效性
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# 2.重复链接
def filter_links(links):
    # 使用set来去除重复的链接
    unique_links = set(links)

    # 过滤非法的链接
    valid_links = {link for link in unique_links if is_valid_url(link)}

    return valid_links

def get_related_links(url):
    data = request_douban(url)
    if data.status_code == 404:
        return 404
    soup = BeautifulSoup(data.text, "html.parser")
    links = []
    for link in soup.find_all("a"):
        link = link.get("href")
        try:
            if is_javascript_link(link):
                continue
            if is_fragment_link(link):
                link = remove_fragment(link)
            if not is_full_url(link):
                link = urljoin(url, link)
            if not is_valid_url(link):
                continue
            links.append(link)
        except Exception as e:
            if link is None:
                continue
            else:
                print(e)
    return links   
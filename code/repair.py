# 修复损坏的xml文件，添加标题
import xml.etree.ElementTree as ET
import random
from time import sleep
import requests
from bs4 import BeautifulSoup
import re

DATA_PATH = '../data/'
HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Connection":
        "keep-alive",
    "Referer":
        "https://www.douban.com"  # 站内访问
}

def add_title_to_xml(index, title):
    # 解析XML文件
    xml_path = DATA_PATH + 'movies/{}.xml'.format(index)
    tree = ET.parse(xml_path, ET.XMLParser(encoding='utf-8'))
    root = tree.getroot()

    # 在每个<review>标签后添加新的数据
    for i, review in enumerate(root.iter('review')):
        new_element = ET.Element('标题')
        new_element.text = title[i]
        review.insert(1, new_element)

    # 保存修改后的XML文件
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)

# 请求网页封装
def request_douban(url, headers = HEADERS):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('被拦截了，休息一下')
            sleep(1200)
        else:
            break
    sleep(1)
    return response

def crawl_title(url):
    response = request_douban(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        title = soup.select('div.main.review-item > div.main-bd > h2')
        for i, t in enumerate(title):
            title[i] = t.text.strip()
    except:
        title = []
    return title

def replacer(name, str):
    def replace_c_with_d(match):
        inner_text = match.group(1)  # 获取<a>和</a>之间的文本
        replaced_text = inner_text.replace('&', '&amp;')
        replaced_text = replaced_text.replace('<', '&lt;')  # 替换文本中的<
        replaced_text = replaced_text.replace('>', '&gt;')
        replaced_text = replaced_text.replace('"', '&quot;')   
        replaced_text = replaced_text.replace("'", '&apos;')
        return match.group(0).replace(inner_text, replaced_text)  # 替换<a>和</a>之间的文本
    return re.sub(r'<{}>(.*?)</{}>'.format(name, name), replace_c_with_d, str, flags=re.DOTALL)

def repair_xml(index):
    path = DATA_PATH + 'movies/{}.xml'.format(index)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    meta = ['电影名', '演员', '简介', '作者', '影评', '标题']
    for m in meta:
        content = replacer(m, content)

    # 将修改后的内容写回文件
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    '''
    delta = 1070
    error_list = []
    for index, url in enumerate(url_list[delta:]):
        if (index + 1) % 100 == 0:   # 每爬50部电影休息10分钟，主动休息，防止被封
            print('中场休息10分钟')
            sleep(600)
        index += delta
        print('crawling', index, '...', end='\r')
        url = url_list[index] + 'reviews'
        titles = crawl_title(url)
        try:
            add_title_to_xml(index, titles)
        except Exception as e:
            error_list.append(index)
            print('添加标题时出错：', index, url, e)
    '''
    for i in range(2503):
        print('repairing', i, end='\r')
        repair_xml(i)
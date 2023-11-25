from elasticsearch import Elasticsearch
import xml.etree.ElementTree as ET

es = Elasticsearch(['http://localhost:9200'], request_timeout=3600)
DATA_PATH = '../data/'

def create_index(name):
    # 创建索引
    es.indices.create(index=name, ignore=400)

def insert_movie(index):
    # 解析XML文件
    path = DATA_PATH + 'movies/{}.xml'.format(index)
    tree = ET.parse(path, ET.XMLParser(encoding='utf-8'))
    movie = tree.getroot()
    # 提取数据
    data = {
        '电影名': movie.find('电影名').text,
        '年份': movie.find('年份').text,
        '评分': movie.find('评分').text,
        '封面': movie.find('封面').text,
        '导演': movie.find('导演').text,
        '演员': movie.find('演员').text,
        '简介': movie.find('简介').text,
    }
    # 将数据插入到Elasticsearch的索引中
    es.index(index='movies', body=data)

if __name__ == '__main__':
    # 创建索引
    create_index('movies')
    create_index('reviews')
    # 插入数据
    for i in range(1, 11):
        insert_movie(i)

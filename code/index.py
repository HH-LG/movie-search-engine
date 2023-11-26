from elasticsearch import Elasticsearch
import xml.etree.ElementTree as ET

es = Elasticsearch(['http://localhost:9200'], request_timeout=3600)
DATA_PATH = '../data/'

def create_index(name):
    # 创建索引
    es.indices.create(index=name, ignore=400)

def search_index(name, str, num):
        # Define your search query
    search_query = {
        "query": {
            "multi_match": {
                "query": str,
                "fields": ["*"]
            }
        },
        "from": 0,
        "size": num
    }
    # 搜索
    response = es.search(index=name, body=search_query)
    # Print the titles of the returned documents
    for hit in response['hits']['hits']:
        print(hit['_source']['电影名'])

if __name__ == '__main__':
    # 创建索引
    create_index('movies')
    create_index('reviews')

    # 插入数据
    #for i in range(1, 11):
        #insert_movie(i)
    
    # 搜索
    search_index('movies', '战争 爱情', 30)
from elasticsearch import Elasticsearch
import xml.etree.ElementTree as ET

es = Elasticsearch(['http://localhost:9200'], request_timeout=3600)
DATA_PATH = '../data/'

def create_index(name):
    # 创建索引
    if not es.indices.exists(index=name):
        es.indices.create(index=name)

def get_skelton_query():
    skelton_query = {
        "query": {
            "function_score": {
                "query": {
                },
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "pagerank",
                            "modifier": "log1p",
                            "factor": 1.0,
                            "missing": 1
                        }
                    }
                ],
                "boost_mode": "multiply"
            }
        }
    }
    return skelton_query

def search_index(name, str, num):
    search_query = get_skelton_query()
    search_query["query"]["function_score"]["query"].update(
                {"multi_match": {
                    "query": str,
                    "fields": ["*"]
                }})
    # 搜索
    response = es.search(index=name, body=search_query)
    return response['hits']['hits']


if __name__ == '__main__':
    # 创建索引
    create_index('movies')
    create_index('reviews')

    # 插入数据
    #for i in range(1, 11):
        #insert_movie(i)
    
    # 搜索
    name = ['movies', 'reviews']
    response = search_index(name, '美丽人生', 20)
    for hit in response:
        try:
            print(hit['_source']['标题'], hit['_source']['url'])
        except:
            print(hit['_source']['电影名'], hit['_source']['url'])
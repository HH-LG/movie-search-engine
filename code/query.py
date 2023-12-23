# 实现高级查询，包括：站内查询、短语查询、通配查询
# 另外还有：查询日志、网页快照

from index import *

class Query:

    # 初始化
    def __init__(self):
        self.es = Elasticsearch(['http://localhost:9200'], request_timeout=3600)
        self.DATA_PATH = '../data/'
        
    # 站内查询
    def site_search(url):


    # 短语查询
    def phrase_search(field, phrase, query):
        query['query'].append(
        {
            "match_phrase": {
                field: phrase
            }
        })
        return query

    # 通配查询
    def wildcard_search(field, wildcard):
        response = es.search(
            body={
                "query": {
                    "wildcard": {
                        field: wildcard
                    }
                }
            }
        )
        return response['hits']['hits']

# 查询日志
def query_log(query):
    # 这个函数需要你自己实现，因为它取决于你的日志系统
    pass

# 网页快照
def webpage_snapshot(url):
    # 这个函数需要你自己实现，因为它取决于你的网页快照系统
    pass
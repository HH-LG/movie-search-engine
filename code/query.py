# 实现高级查询，包括：站内查询、短语查询、通配查询
# 另外还有：查询日志、网页快照

from elasticsearch import Elasticsearch
from index import get_query, es



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
class Query:

    # 初始化
    def __init__(self, str):
        self.str = str
        self.use_site_search = False
        # 有可能是短语查询或通配查询pharse, wildcard
        self.search_type = 'phrase'
        
    # 站内查询
    def site_search(self, url):
        self.use_site_search = True
        self.site = url

    # 短语查询
    def phrase_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'match_phrase':{'标题':self.str}}, 
            {'match_phrase':{'电影名':self.str}}
            ]}})
        return query
        

    # 通配查询
    def wildcard_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'wildcard':{'标题':self.str}}, 
            {'wildcard':{'电影名':self.str}}
            ]}})
        return query

    def search(self):
        # 暂定为20条
        indices = ['movies', 'reviews']
        #query = get_query(self.str, 20)
        query = ''
        if self.search_type == 'normal':
            query = get_skelton_query()
            query["query"]["function_score"]["query"].update(
                            {"multi_match": {
                                "query": self.str,
                                "fields": ["*"]
                            }})
        elif self.search_type == 'phrase':
            query = get_skelton_query()
            query = self.phrase_search(query)
            
        elif self.search_type == 'wildcard':
            query = get_skelton_query()
            query = self.wildcard_search(query)
        response = es.search(index=indices, body=query)
        return response['hits']['hits']


        

# 查询日志
def query_log(query):
    # 这个函数需要你自己实现，因为它取决于你的日志系统
    pass

# 网页快照
def webpage_snapshot(url):
    # 这个函数需要你自己实现，因为它取决于你的网页快照系统
    pass

if __name__ == '__main__':
    q = Query('平行')
    response = q.search()
    for hit in response:
        try:
            print(hit['_source']['标题'], hit['_source']['url'], hit['_score']*10**6)
        except:
            print(hit['_source']['电影名'], hit['_source']['url'], hit['_score']*10**6)

# 实现高级查询，包括：站内查询、短语查询、通配查询
# 另外还有：查询日志、网页快照

import collections
import datetime
from database import *
from index import get_skelton_query, es

class Query:

    # 初始化
    def __init__(self, str, user_id = -1, type = 'normal'):
        str_list = str.split(' ')
        if 'site:' in str_list[-1]:
            self.str = ' '.join(str_list[:-1])
            url = str_list[-1].split(':')[-1]
            self.site_search(url)
        else:
            self.str = str
            self.use_site_search = False
        # 有可能是短语查询或通配查询pharse, wildcard
        self.search_type = type
        self.user_id = user_id

        
    # 站内查询
    def site_search(self, url):
        self.use_site_search = True
        self.site = url

    # 短语查询
    def phrase_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'match_phrase':{'标题':self.str}}, 
            {'match_phrase':{'影评':self.str}}, 
            {'match_phrase':{'电影名':self.str}},
            {'match_phrase':{'简介':self.str}}
            ]}})
        return query
        

    # 通配查询
    def wildcard_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'wildcard':{'标题':self.str}}, 
            {'wildcard':{'影评':self.str}}, 
            {'wildcard':{'电影名':self.str}},
            {'wildcard':{'简介':self.str}} 
            ]}})
        return query

    # 模糊查询
    def fuzzy_search(self, query):
        query["query"]["function_score"]["query"].update(
                {"multi_match": {
                    "query": self.str,
                    "fields": ["*"],
                    "fuzziness": "AUTO"
                }})

        return query

    # 正则查询
    def regexp_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'regexp':{'标题':{
                       'value':self.str,
                       'flags': 'ALL',
                       'max_determinized_states': 10000,
                       'rewrite': 'constant_score'}}}, 
            {'regexp':{'影评':{
                       'value':self.str,
                       'flags': 'ALL',
                       'max_determinized_states': 10000,
                       'rewrite': 'constant_score'}}}, 
            {'regexp':{'电影名':{
                       'value':self.str,
                       'flags': 'ALL',
                       'max_determinized_states': 10000,
                       'rewrite': 'constant_score'}}},
            {'regexp':{'简介':{
                       'value':self.str,
                       'flags': 'ALL',
                       'max_determinized_states': 10000,
                       'rewrite': 'constant_score'}}}
            ]}})
        return query


    def search(self, start = 0, size = 10):
        # 暂定为10条
        indices = ['movies', 'reviews']
        # 获取查询语句
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
        elif self.search_type == 'fuzz':
            query = get_skelton_query()
            query = self.fuzzy_search(query)
        elif self.search_type == 'regexp':
            query = get_skelton_query()
            query = self.regexp_search(query)
        
        # 分页
        query['from'] = start
        query['size'] = size
        
        # 搜索
        response = es.search(index=indices, body=query)
        results = response['hits']['hits']
        cnt = response['hits']['total']['value']
        # 站内搜索
        if self.use_site_search:
            results = [hit for hit in results if self.site in hit['_source']['url']]
        return (results, cnt)

    # 查询日志
    def do_log(self):
        user_id = self.user_id
        
        type_str = self.search_type.upper()
        type_str = '[' + type_str + ']'

        if self.use_site_search:
            type_str = type_str + ' site:' + self.site
        
        query = type_str + ' ' + self.str
        timestamp = datetime.datetime.now()  # 查询的时间

        # 调用之前定义的insert_log函数来插入日志
        insert_query_log(user_id, query, timestamp)
        
def convert_into_results(response):
    results = list()
    for hit in response:
        result = dict()
        try:
            result['url'] = hit['_source']['url']
        except:
            print('url not found')

        result['cluster'] = hit['_source']['cluster']
        result['score'] = round(hit['_score']*10**6, 2)
        if '影评' in hit['_source'].keys():
            result['type'] = 'review'
            result['title'] = hit['_source']['标题']
            result['text'] = hit['_source']['影评']
            result['rating'] = hit['_source']['作者评分'] * 2
            result['author'] = hit['_source']['作者']
            result['time'] = ' '.join([hit['_source']['时间'][:10], hit['_source']['时间'][11:19]])
            result['useful'] = hit['_source']['有用数']
            result['useless'] = hit['_source']['没用数']
        else:
            result['type'] = 'movie'
            result['title'] = hit['_source']['电影名']
            result['text'] = hit['_source']['简介']
            result['rating'] = round(hit['_source']['评分'], 1)
            result['author'] = hit['_source']['导演']
            result['time'] = hit['_source']['年份'][:4]

        results.append(result)
    return results

def personized_results(results, favorite_clusters):

    if favorite_clusters is None:
        return results
    personized_res = list()
    for result in results:
        if result['cluster'] in favorite_clusters:
            result['score'] *= 1.2
            result['score'] = round(result['score'], 2)
            print(result['score'])
        personized_res.append(result)
    personized_results = sorted(personized_res, key=lambda x:x['score'], reverse=True)
    return personized_results

# 网页快照
def webpage_snapshot(url):
    pass

if __name__ == '__main__':
    create_user_table()
    create_query_log_table()
    #insert_user('admin', 'zhu203545')
    q = Query('图', 1)
    response, cnt = q.search()
    print(cnt)

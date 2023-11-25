from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'], request_timeout=3600)

doc = {
    'name': '杨晨',
    'age': '22'
}

# 在test索引id为3的位置插入一条数据
es.create(index='test_0', id='3', body=doc)

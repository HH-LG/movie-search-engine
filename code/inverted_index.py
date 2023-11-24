from elasticsearch import Elasticsearch

es = Elasticsearch(['https://hh:123456@localhost:7000'], request_timeout=3600)
# 创建一个索引为test的索引
doc = {
    'name': '杨晨',
    'age': '22'
}
# 在test索引id为3的位置插入一条数据
es.create(index='test',id='3', document=doc)

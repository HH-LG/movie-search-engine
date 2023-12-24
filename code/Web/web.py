import time
from flask import Flask, request, render_template
import jieba
import sys
sys.path.append('..')
from index import *
from database import get_most_common_queries
from query import Query, convert_into_results

TOP_QUERY_NUM = 10

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    pop_query = get_most_common_queries(TOP_QUERY_NUM)
    data = {}
    data['pop_query'] = pop_query
    return render_template('index.html', data=data)

@app.route('/result', methods=['GET','POST'])
def result():
    query = request.args.get('q')
    print(query)
    q = Query(query, 1)

    # 搜索
    start = time.time()
    response = q.search()
    end = time.time()

    results = convert_into_results(response)

    queryInfo = {}
    queryInfo['query'] = query
    queryInfo['number'] = 0
    queryInfo['time'] = end - start

        # 分词, highlightWords：高亮词汇
    seg_list = jieba.cut(query)
    highlightWords = " ".join(seg_list)
    queryInfo['highlightWords'] = highlightWords

    return render_template('result.html', results=results, queryInfo=queryInfo)


if __name__ == '__main__':
    app.run()
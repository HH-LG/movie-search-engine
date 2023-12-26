import time
from flask import Flask, request, render_template, redirect, url_for
import jieba
from gensim.models import Word2Vec
import sys
sys.path.append('..')
from index import *
from database import *
from query import Query, convert_into_results
from word2vec import get_similar_words

TOP_QUERY_NUM = 10
HISTORY_QUERY_NUM = 10

app = Flask(__name__)
has_login = False
model = Word2Vec.load('../model')

@app.route('/', methods=['GET', 'POST'])
def index():
    pop_query = get_most_common_queries(TOP_QUERY_NUM)
    data = {}
    data['pop_query'] = pop_query

    return render_template('index.html', data=data)

@app.route('/result', methods=['GET','POST'])
def result():
    global has_login, user_id, model

    query = request.args.get('q')
    if query is None:
        return redirect(url_for('index'))
    if has_login:
        q = Query(query, user_id)
    else:
        q = Query(query)

    # 搜索
    start = time.time()
    response = q.search()
    end = time.time()
    results = convert_into_results(response)

    queryInfo = {}
    queryInfo['query'] = query
    queryInfo['number'] = 0
    queryInfo['time'] = round(end - start, 2)

    # 分词, highlightWords：高亮词汇
    seg_list = jieba.cut(query)
    highlightWords = " ".join(seg_list)
    queryInfo['highlightWords'] = highlightWords

    queryInfo['has_login'] = False
    if has_login:
        queryInfo['has_login'] = True
        # 日志
        q.do_log()
        # 网页快照

        # 相关搜索
        try:
            seg_list = []
            for s in query.split(' '):
                seg_list += jieba.cut(s)
            similar_query = get_similar_words(model, seg_list, topn=8)  # 根据给定的条件推断相似词
            print(similar_query)

            similar_query1 = similar_query[:4]
            similar_query2 = similar_query[4:8]
            queryInfo['has_similar'] = True
            queryInfo['similar_query1'] = similar_query1  # 第一行
            queryInfo['similar_query2'] = similar_query2
        except Exception as e:
            print(e)
            queryInfo['has_similar'] = False
            print('没有相似查询')

        # 历史搜索
        queryInfo['history_query'] = get_query_log(user_id)[:HISTORY_QUERY_NUM]
    return render_template('result.html', results=results, queryInfo=queryInfo)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        insert_user(username, password)
    except:
        return "注册失败，用户名已被占用，请返回<a href='/'>主页</a>"
    return "注册成功：username: %s, password: %s" % (username, password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global has_login, user_id
    username = request.form.get('username')
    password = request.form.get('password')

    user = get_user(username)
    if password == user[2]:
        has_login = True
        user_id = user[0]
        return render_template('login.html')
        
    else:
        return "密码错误，请返回<a href='/'>主页</a>"
    


if __name__ == '__main__':
    app.run(debug=True)
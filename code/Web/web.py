import time
from flask import Flask, request, render_template, redirect, url_for, session
import jieba
import sys
sys.path.append('..')
from index import *
from database import *
from query import Query, convert_into_results

TOP_QUERY_NUM = 10
HISTORY_QUERY_NUM = 10

app = Flask(__name__)
app.secret_key = 'zhu203545'

@app.route('/', methods=['GET', 'POST'])
def index():
    pop_query = get_most_common_queries(TOP_QUERY_NUM)
    data = {}
    data['pop_query'] = pop_query

    return render_template('index.html', data=data)

@app.route('/result', methods=['GET','POST'])
def result():
    query = request.args.get('q')
    if query is None:
        return redirect(url_for('index'))
    if 'user_id' in session.keys():
        q = Query(query, session['user_id'])
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

    if 'has_login' in session.keys() and session['has_login']:
        queryInfo['has_login'] = True
        # 日志
        q.do_log()
        # 网页快照

        # 历史搜索
        print('there')
        queryInfo['history_query'] = get_query_log(session['user_id'])[:HISTORY_QUERY_NUM]
    return render_template('result.html', results=results, queryInfo=queryInfo)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        insert_user(username, password)
    except:
        return "注册失败，用户名已被占用"
    return "username: %s, password: %s" % (username, password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = get_user(username)
    if password == user[2]:
        session['has_login'] = True
        session['user_id'] = user[0]
        return render_template('login.html')
        
    else:
        return "密码错误"
    


if __name__ == '__main__':
    app.run(debug=True)
import time
from flask import Flask, request, render_template, redirect, url_for
import jieba
from gensim.models import Word2Vec
import sys
sys.path.append('..')
from index import *
from database import *
from query import Query, convert_into_results, personized_results
from word2vec import get_similar_words
from recommender import get3FavoriteCluster
import pickle

TOP_QUERY_NUM = 10
HISTORY_QUERY_NUM = 10
DATA_PATH = '../../data/'

app = Flask(__name__)
has_login = False
model = Word2Vec.load('../model')
# 使用 TF-IDF 将文本转换为向量
vectorizer = pickle.load(open(DATA_PATH + 'vectorizer.pkl', 'rb'))
kmeans = pickle.load(open(DATA_PATH + 'kmeans.pkl', 'rb'))

@app.route('/', methods=['GET', 'POST'])
def index():
    pop_query = get_most_common_queries(TOP_QUERY_NUM)
    data = {}
    data['pop_query'] = pop_query[:5]

    return render_template('index.html', data=data)

@app.route('/result', methods=['GET','POST'])
def result():
    start = time.time()
    global has_login, user_id, model

    # 获取查询词，查询类型
    query = request.args.get('q')
    if query is None:
        return redirect(url_for('index'))
    if has_login:
        q = Query(query, user_id)
    else:
        q = Query(query)
    queryType = request.args.get('queryType')
    if queryType is None:
        queryType = 'normal'
    q.search_type = queryType

    # 分页
    currentPage = dict()
    pageNumber = request.args.get('page')
    if pageNumber is None:
        pageNumber = 1
    else:
        pageNumber = int(pageNumber)
    currentPage['number'] = pageNumber
    


    # 搜索
    response, cnt = q.search(start=(pageNumber-1)*10, size=10)
    results = convert_into_results(response)

    queryInfo = {}
    queryInfo['query'] = query
    queryInfo['number'] = 0
    queryInfo['cnt'] = cnt
    queryInfo['pageTotal'] = cnt // 10 if cnt % 10 == 0 else cnt // 10 + 1
    queryInfo['queryType'] = queryType

    # 分词, highlightWords：高亮词汇
    seg_list = jieba.cut(query)
    highlightWords = " ".join(seg_list)
    queryInfo['highlightWords'] = highlightWords

    # 个性化推荐
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

    # 已经登录的用户，个性化查询
    queryInfo['has_login'] = False
    if has_login:
        queryInfo['has_login'] = True

        # 个性化查询
        favoriteClusters = get3FavoriteCluster(user_id, kmeans, vectorizer)
        results = personized_results(results, favoriteClusters)

        # 日志
        q.do_log()

        # 历史搜索
        queryInfo['history_query'] = get_query_log(user_id)[:HISTORY_QUERY_NUM]
    end = time.time()
    queryInfo['time'] = round(end - start, 2)
    return render_template('result.html', results=results, queryInfo=queryInfo, currentPage=currentPage)

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
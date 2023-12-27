# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from urllib.parse import urlunparse
from crawl_request import *
from database import *
import networkx as nx
import operator

# pagerank分析:通过调用库函数即可解决

def remove_query_params(url):
    parsed_url = urlparse(url)
    cleaned_url = parsed_url._replace(query="")
    return urlunparse(cleaned_url)

def read_links(col):
    url_list = []
    with open(DATA_PATH + 'links.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row[col]
            url_list.append(url)
    return url_list

def calculate_pagerank():
    from_links = read_links('from_url')
    to_links = read_links('to_url')
    from_links = [remove_query_params(url) for url in from_links]
    to_links = [remove_query_params(url) for url in to_links]
    all_links = set(from_links + to_links)
    print("[res]: 一共有", len(all_links), "个链接")

    # 创建有向图
    Graph = nx.DiGraph()
    Graph.add_nodes_from(all_links)
    for i in range(len(from_links)):
        Graph.add_edge(from_links[i], to_links[i])
    print("[log]: Add nodes and edges successfully!")
    
    pr = nx.pagerank(Graph, max_iter=40, alpha=0.01)  # 得到的是字典
    print("[log]: Pagerank successfully!")
    with open (DATA_PATH + 'pagerank.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['url', 'pagerank'])
        for url, pagerank in pr.items():
            writer.writerow([url, pagerank])
    print("[log]: Write pagerank successfully!")
    print("[res]: 最大PR值对应的节点：", max(pr.items(), key=operator.itemgetter(1))[0])
    print('[res]: pagerank 最大值为', max(pr.items(), key=operator.itemgetter(1))[1])

def column_exists(table, column):
    sql = f"SHOW COLUMNS FROM {table} LIKE '{column}'"
    result = cursor.execute(sql)
    return result > 0
    
def update_database():
    if not column_exists('movies', 'url'):
        sql = "ALTER TABLE movies ADD COLUMN url VARCHAR(255);"
        cursor.execute(sql)
    if not column_exists('movies', 'pagerank'):
        sql = "ALTER TABLE movies ADD COLUMN pagerank FLOAT;"
        cursor.execute(sql)
    if not column_exists('reviews', 'url'):
        sql = "ALTER TABLE reviews ADD COLUMN url VARCHAR(255);"
        cursor.execute(sql)
    if not column_exists('reviews', 'pagerank'):
        sql = "ALTER TABLE reviews ADD COLUMN pagerank FLOAT;"
        cursor.execute(sql)
    db.commit()
    # 得到url与pagerank的字典
    dict = {}
    with open(DATA_PATH + 'pagerank.csv', 'r', encoding='utf-8') as file:
        next(file)  # Skip the header
        for line in file:
            try:
                url, score = line.strip().split(',')
                score = float(score)
                dict.update({url: score})
            except:
                continue
    cursor.execute("SELECT id, 电影名 FROM movies")
    rows = cursor.fetchall()
    movie_urls = read_movie_url()
    for row in rows:
        id, name = row
        url = movie_urls[id-1]
        pagerank = dict.get(url)
        if pagerank is None:
            pagerank = 0
        cursor.execute("UPDATE movies SET pagerank = %s, url = %s WHERE id = %s", (pagerank, url, id))
        print(id, name, url, pagerank)
        

    cursor.execute("SELECT id, 标题 FROM reviews")
    rows = cursor.fetchall()
    review_urls = read_review_url()
    for row in rows:
        id, name = row
        url = review_urls[id-1]
        pagerank = dict.get(url)
        if pagerank is None:
            pagerank = 0
        cursor.execute("UPDATE reviews SET pagerank = %s, url = %s WHERE id = %s", (pagerank, url, id))
        print(id, name, url, pagerank)
    db.commit()

if __name__ == '__main__':
    #calculate_pagerank()
    update_database()



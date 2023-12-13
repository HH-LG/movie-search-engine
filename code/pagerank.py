# -*- coding: utf-8 -*-
from urllib.parse import urlunparse
from crawl_request import *
import matplotlib.pyplot as plt
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

if __name__ == '__main__':
    url = 'https://movie.douban.com/subject/1297359/?from=subject-page'
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
    
    pr = nx.pagerank(Graph, max_iter=30, alpha=0.85)  # 得到的是字典
    print("[log]: Pagerank successfully!")
    with open (DATA_PATH + 'pagerank.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['url', 'pagerank'])
        for url, pagerank in pr.items():
            writer.writerow([url, pagerank])
    print("[log]: Write pagerank successfully!")
    print("[res]: 最大PR值对应的节点：", max(pr.items(), key=operator.itemgetter(1))[0])
    print('[res]: pagerank 最大值为', max(pr.items(), key=operator.itemgetter(1))[1])

# -*- coding: utf-8 -*-
from crawl_request import *
from pygraph.classes.digraph import digraph
# pagerank分析:通过调用库函数review_url_list[index][i]即可解决



if __name__ == '__main__':
    url = "https://movie.douban.com/top250"
    list = get_related_links(url)

    url_header = ['from_url', 'to_url']
    with open(DATA_PATH + 'links.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=url_header)
        writer.writeheader()

    with open(DATA_PATH + 'links.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=url_header)
        for link in list:
            writer.writerow({'from_url': url, 'to_url': link})
        
    #dg = digraph()

    #dg.add_nodes(["A", "B", "C", "D", "E"])

    #dg.add_edge(("A", "B"))

    #pr = PRIterator(dg)
    #page_ranks = pr.page_rank()

    #print("The final page rank is\n", page_ranks)

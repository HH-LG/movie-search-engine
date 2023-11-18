# -*- coding: utf-8 -*-
# @Author  : tang
# @Time    : 2023/7/3 10:16

import requests
from bs4 import BeautifulSoup
import csv

# user-agent
request_header = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
        "Safari/537.36 Edg/114.0.1823.58",
    "Connection":
        "keep-alive",
    "Referer":
        "https://www.douban.com"  # 站内访问
}


# 进入详情页读取信息
def deal_hd(hd_div):
    homepage_a = hd_div.select('div.hd > a')[0]
    homepage_url = homepage_a.get('href').strip()
    response = requests.get(url=homepage_url, headers=request_header)
    status = response.status_code
    if status == 200:
        html_txt = response.text
        # 已经获取到响应文本，使用bs4解析html文本
        soup_in = BeautifulSoup(html_txt, 'lxml')
        # 开始处理详情页！
        header = soup_in.select('#content > h1')[0]
        # 电影名字
        movie_name_span = header.select('h1 > span')[0]
        movie_name = movie_name_span.getText().strip()
        # 电影年份
        movie_year_span = header.select('h1 > span.year')[0]
        movie_year = movie_year_span.getText().strip()
        # 电影封面
        cover_a = soup_in.select('#mainpic > a > img')[0]
        cover_url = cover_a.get('src').strip()
        # 导演
        director_span = soup_in.select('#info > span > span.attrs')[0]
        director = director_span.getText().strip()
        # 汇总返回
        hd_info = {
            '电影名': movie_name,
            '电影年份': movie_year,
            '电影封面': cover_url,
            '导演': director
        }
        return hd_info
    # 被拦截了
    return status


# 从列表页读取信息
def deal_bd(bd_div):
    # 影片得分
    rating_span = bd_div.select('div.star > span.rating_num')[0]
    rating = rating_span.getText().strip()
    # 评分人数
    rating_people_span = bd_div.select('div.star > span')[3]
    rating_people = rating_people_span.getText().strip()
    # 精彩评论  有可能不存在
    if len(bd_div.select('p.quote > span.inq')) != 0:
        quote_span = bd_div.select('p.quote > span.inq')[0]
        quote = quote_span.getText().strip()
    else:
        quote = 'null'
    # 汇总返回
    bd_info = {
        "得分": rating,
        "评价人数": rating_people,
        "精彩评论": quote
    }
    return bd_info


# 爬取知乎热榜× byd必须登录
# 爬豆瓣电影250
if __name__ == '__main__':
    dic_header = ['电影名', '电影年份', '电影封面', '导演', "得分", "评价人数", "精彩评论"]
    with open('douban_film_250.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=dic_header)
        writer.writeheader()
        for i in range(0, 250, 25):
            # 生成url
            url_str = "https://movie.douban.com/top250?start={}".format(i)
            # 发送请求
            resp = requests.get(url=url_str, headers=request_header)
            status_code = resp.status_code
            if status_code == 200:
                print("OK了家人们")
                html_text = resp.text
                # 已经获取到响应文本，使用bs4解析html文本
                soup = BeautifulSoup(html_text, 'lxml')
                # 获取到三个的div
                hd_divs = soup.select('div.item > div.info > div.hd')
                bd_divs = soup.select('div.item > div.info > div.bd')
                for hd_div, bd_div in zip(hd_divs, bd_divs):
                    # 遍历各个div
                    hd_info = deal_hd(hd_div)
                    bd_info = deal_bd(bd_div)
                    # 合并成一个字典
                    data = hd_info.copy()
                    data.update(bd_info)
                    writer.writerow(data)




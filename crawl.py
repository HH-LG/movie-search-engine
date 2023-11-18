from time import sleep
import requests
from bs4 import BeautifulSoup
import csv
# 最多爬取2500部电影
# 每个电影爬取100条影评
# user-agent
headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
        "Safari/537.36 Edg/114.0.1823.58",
    "Connection":
        "keep-alive",
    "Referer":
        "https://www.douban.com"  # 站内访问
}

URL_SET = set()
REVIEW_NUM = 100
def request_douban(url, headers=headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('被拦截了，休息一下')
        exit(0)
    sleep(5)
    return response

def crawl_reviews(url, num = REVIEW_NUM):
    for i in range(0, num, 20):
        url_review = url + '?start=' + str(i)
        response = request_douban(url_review)
        soup = BeautifulSoup(response.text, 'lxml')

        # 抓取影评
        review_links = soup.select('div.main.review-item > div.main-bd > h2 > a')
        for link in review_links:
            url_report = link['href']
            response = request_douban(url_report)
            soup = BeautifulSoup(response.text, 'lxml')
            # 作者
            author = soup.select('div.main > header.main-hd > a ')[0]
            print(author.text)
            # 评分

            # 影评
            review = soup.select('div.main > div.main-bd > div > div.review-content.clearfix > p')
            text = '\n'.join([p.text.strip() for p in review])
            print(text)
            break
        break

def crawl_and_get_related_urls(url):
    response = request_douban(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 爬电影名字

    # 爬评分

    # 导演

    # 爬演员

    # 爬简介
    intro = soup.find('div', class_='indent', id='link-report-intra')
    intro = intro.select_one('.all.hidden').text.replace(' ', '')
    print(intro)

    # 爬相关电影
    related_links = soup.select('div.recommendations-bd > dl > dt > a')
    for link in related_links:
        related_url = link['href']
        if related_url not in URL_SET:
            related_url = related_url.rstrip('?from=subject-page')
            URL_SET.add(related_url)

    # 爬影评
    reviews = url + 'reviews'
    crawl_reviews(reviews)


'''爬取豆瓣电影top250链接'''
def top250_crawer(url, sum):
    url_str = "https://movie.douban.com/top250?start={}".format(sum)
    response = request_douban(url_str)
    soup = BeautifulSoup(response.text, 'html.parser')
    movie_items = soup.find_all('div', class_='item')
    url_list = []
    for item in movie_items:
        # 加入相关电影的超链接
        a = item.find_all('a')
        url_list.append(a[1]['href'])
    return url_list
if __name__ == '__main__': 
    '''
    url = 'https://movie.douban.com/top250'
    sum =0
    # '遍历10页数据，250条结果'
    for a in range(10):
        if sum == 0 :
            top250_crawer(url,sum)
            sum +=25
        else:
            page = '?start='+str(sum)+'&filter='
            new_url = url+page
            top250_crawer(new_url,sum)
            sum +=25
    '''
    init_url = 'https://movie.douban.com/top250'
    sum = 0
    top_urls = top250_crawer(init_url, sum)
    URL_SET = set(top_urls)
    crawl_and_get_related_urls(top_urls[0])
    #for url in top_urls:
        #crawl_and_get_other_urls(url)


# movie-search-engine
final project for IR

项目的总体架构如下：

```bash
./
├─code  # 项目所有代码
│  ├─Web  # 网页图形化界面代码
│  │  ├─static
│  │  │  ├─css
│  │  │  ├─img
│  │  │  └─js
│  │  └─templates
│  └─__pycache__
├─data 
│  ├─movies  # 所有电影及影评的数据
│  └─pkl  # 保存的一些变量
└─img
```

## 网页抓取

相关代码：

```bash
./
│
└──code
   │  crawl.ipynb
   └─ crawl_request.py
```

首先利用request包对网页进行抓取，随后利用Beautifulsoup库进行网页解析，获取网页中的内容信息，抓取的网页为[豆瓣电影](https://movie.douban.com/)的电影信息以及影评信息。

抓取网页的起始点为[豆瓣电影250](https://movie.douban.com/top250)的全部250部电影。随后根据这些电影去爬取相关电影、影评将相关电影加入到队列中，重复这样的广度优先遍历过程。

最后，总计收集了电影及影评**25000+条**。将这些数据存储在`data`文件夹下，并保存到本地mysql数据库中。

下面是数据库的截图：

![数据库截图](./img/db.png)

## 建立索引

相关代码：
```bash
./
│
└──code
   │  index.py
   └─ database.py
```

利用elasticseach建立对于爬取到的锚文本、网页内容建立索引，并使用了logstash工具进行与数据库的自动同步。

下面稍微介绍一下我对于logstash的使用：

```bash
input {
    stdin {
    }
    jdbc {
      # 数据库  数据库名称为ESDB，表名为movies
      jdbc_connection_string => "jdbc:mysql://localhost:3306/ir_db"
      # 用户名密码
      jdbc_user => "root"
      jdbc_password => "******"
      # jar包的位置
      jdbc_driver_library => "D:/elasticsearch-8.11.1-windows-x86_64/logstash-8.11.1/mysql-connector-j-8.2.0.jar"
      # mysql的Driver
      jdbc_driver_class => "com.mysql.jdbc.Driver"
      jdbc_paging_enabled => "true"
      jdbc_page_size => "50000"
      # sql文件位置 没有可以不写
      #statement_filepath => "config-mysql/movies.sql"
      statement => "select * from movies"
      # 设置定时任务间隔  含义：分、时、天、月、年，全部为*默认含义为每分钟跑一次任务
      schedule => "* * * * *"
	  #索引的类型
      type => "movies"
    }
}

output {
    elasticsearch {
        hosts => "127.0.0.1:9200"
        # index名
		index => "movies"
		# 关联的数据库中有有一个id字段，对应索引的id号
        document_id => "%{id}"
    }
    stdout {
        codec => json_lines
    }
}
```

通过上面的config文件可以对于数据库进行自动同步，将数据库中的内容插入到elasticseach中，从而得到了对于电影以及影评的索引。


## 链接分析

相关代码：
```bash
./
│
└──code
   │  crawl.ipynb
   └─ pagerank.py
```

首先需要爬取网页的链接关系，我仍然是从[豆瓣250](https://movie.douban.com/top250)开始，分析每个网页中所有的链接，加入到全局的集合中，并将其中的新链接加入到**待爬取的队列**中，重复上面的过程，做广度优先遍历。

就这样，爬取了**200000+**网页链接关系。随后调用**networkx**库中的pagerank函数计算出每个网页的PageRank值，最后，将计算好的pagerank值存储到数据库中。

![计算到的pagerank](./img/pagerank.png)[]

相关的代码在crawl.ipynb以及pagerank.py中。

## 查询服务

相关代码
```bash
./
│
└──code
   │  database.py
   └─   query.py
```
通过elasticsearch的接口以及数据库接口为用户提供**站内查询、短语查询、通配查询、模糊查询、正则查询、查询⽇志**的查询服务。

各部分的功能介绍如下:
1. 站内查询：查询指定网站的文档
2. 短语查询：查询词为短语，不可分割
3. 通配查询：查询词中有匹配符，能匹配所有符号
4. 模糊查询：查询词可能有错误，搜索引擎可对其更改
5. 正则查询：查询语句为正则表达式
6. 查询日志：为用户记录查询历史记录

### 高级查询

在query.py中实现了前五种查询，使用了elasticsearch的接口。

```python
# code/query.py
class Query:

    # 初始化
    def __init__(self, str, user_id = -1, type = 'normal'):
        ''' ...some code here... '''
        
    # 站内查询
    def site_search(self, url):
        self.use_site_search = True
        self.site = url

    # 短语查询
    def phrase_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'match_phrase':{'标题':self.str}}, 
            {'match_phrase':{'电影名':self.str}}
            ]}})
        return query
        

    # 通配查询
    def wildcard_search(self, query):
        query["query"]["function_score"]["query"].update({'bool':{'should':[
            {'wildcard':{'标题':self.str}}, 
            {'wildcard':{'电影名':self.str}}
            ]}})
        return query
    
    ''' ...正则查询、模糊查询实现...'''
    ''' ...some code here... '''

    def search(self, start = 0, size = 10):
        ''' ...some code here... '''
```
上述代码通过调整发送到elasticsearch的查询语句api选项，从而实现了各个高级查询操作。

### 查询日志

在query.py以及database.py中实现了查询日志的记录，通过mysql记录了用户的查询内容、查询时间、查询结果、查询类型、用户id等信息。

日志记录效果如下：

![日志](./img/log.png)[]

```python
# code/database.py
def create_query_log_table():
    sql = """
        CREATE TABLE IF NOT EXISTS query_log (
            id INT(11) PRIMARY KEY AUTO_INCREMENT,
            user_id INT(11),
            query MEDIUMTEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    cursor.execute(sql)

# code/query.py
    # 查询日志
    def do_log(self):
        user_id = self.user_id
        
        type_str = self.search_type.upper()
        type_str = '[' + type_str + ']'

        if self.use_site_search:
            type_str = type_str + ' site:' + self.site
        
        query = type_str + ' ' + self.str
        timestamp = datetime.datetime.now()  # 查询的时间

        # 调用之前定义的insert_log函数来插入日志
        insert_query_log(user_id, query, timestamp)
```

当然，查询日志的实现少不了对于用户登录系统的实现，于是也建立了用户表，记录了用户的id、用户名、密码等信息。并通过与数据库进行交互在web网页中实现了用户的登录、注册的功能。

## 个性化查询

```bash
./
│
└──code
   │  recommend.ipynb
   └─   recommend.py
```

### 文本聚类分析

通过对于爬取到的影评以及电影进行文本聚类分析，可以得到每个影评和电影的主题，从而为用户提供更加精准的查询服务。

在recommend.ipynb中实现了对于影评的聚类分析，通过对于文本的分词、去停用词、词干提取、词向量化、降维、聚类等步骤，将影评聚类为20个类别。

这一部分的工作主要通过sklearn库来实现。

- 首先了sklearn中的TfidfVectorizer将文本的tfidf特征进行提取，PCA进行降维；
- KMeans进行聚类分析。
- 训练好模型后，将其保存在本地，以便后续使用。

最终文档的分类情况如下:

![kmeans聚类](./img/kmeans.png)[]

第一个数表示聚类编号，第二个数表示聚类中的文档数目。

### 用户偏好分析

通过对于用户的查询日志进行分析，可以得到用户的偏好，从而为用户提供个性化的查询服务。

- 首先，通过对于用户的查询日志进行分析，可以得到用户的查询偏好，即用户经常查询的关键词。这里我使用了jieba库进行分词，通过对于用户的查询日志进行分词。

- 随后用上一步训练好的词向量模型将其转化为向量，以及上一步得到的kmeans模型将其聚类，得到用户的查询偏好。将这些类别的分数相应的提高，从而为用户提供个性化的查询服务。

相关代码在recommend.py中，下面展示经过分析以后对于相同文档打分的改变：

用户搜索“乔布斯”之前，搜索“乔布斯”：

![乔布斯之前](./img/before.png)

用户搜索“乔布斯”之后，再次搜索“乔布斯”：

![乔布斯之后](./img/after.png)

我们可以看到，经过分析以后，前五名中的文档发生了改变，一些原来不在前五名的文档被推荐到了前五名。另外还可以看到分数变化，例如第一名“乔布斯”的分数从124.01提高到了148.81。


## Web图形化页面

```bash
./
│
└──code
   └─ Web
      └─ web.py
```
通过Flask框架并编写相应的html代码实现了网页的图形化界面，用户可以通过网页进行查询、登录、注册等操作。具体的代码在web.py中，不是重点，这里不再赘述。

下面是网页的截图：

网页主页：

![网页截图](./img/engine.png)

查询结果：

![查询结果](./img/result.png)

## 个性化推荐

```bash
./
│
└──code
   │
   └─ word2vec.py
```

通过对于用户的查询内容进行分析，从而得到与用户查询内容相似的电影/影评，为用户提供个性化的推荐服务。这部分的工作使用了`gensim.models `中的` word2vec, Word2Vec`模型。

- 首先，对于电影以及影评的文本进行分词、去停用词、词干提取、词向量化等步骤，得到每个电影/影评的词向量。

- 随后，通过计算用户查询内容的词向量与每个电影/影评的词向量的余弦相似度，得到与用户查询内容相似的电影/影评。

例如，在用户搜索阿飞时，相关推荐会推荐出“正传","花样年华”等提示词，用户可以点击这些提示词进行查询：

![推荐](./img/related.png)
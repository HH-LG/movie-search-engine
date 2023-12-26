# movie-search-engine
final project for IR

## 网页抓取

利用beautifulsoup4库进行网页抓取，抓取的网页为[豆瓣电影](https://movie.douban.com/)的电影信息以及影评信息。

抓取网页的起始点为[豆瓣电影250](https://movie.douban.com/top250)的前10页，每页25部电影，共250部电影。随后根据这些电影找到相关的电影、影评，每条电影的影评数量不超过10条。最后对于相关的电影重复上述过程，直到抓取到的电影数达到2500部。

最后，收集了2503部电影，共计影评数为23515条。将这些数据存储在`data`文件夹下，并保存到本地mysql数据库中。

下面是数据库的截图：

![数据库截图](./img/db.png)

## 建立索引

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

由此得到了对于电影以及影评的索引。


## 链接分析

首先需要爬取网页的链接关系，我仍然是从[豆瓣250](https://movie.douban.com/top250)开始，分析每个网页中所有的链接，加入到全局的集合中，并将其中的新链接加入到待爬取的队列中。

就这样，爬取了20万个网页链接关系。这些链接关系大都将把我爬到的电影以及影评链接覆盖了。随后调用库函数计算出每个网页的PageRank值，将其存储在数据库中。

相关的代码在craw.ipynb以及pagerank.py中。

## 查询服务





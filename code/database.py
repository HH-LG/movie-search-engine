import pymysql
import xml.etree.ElementTree as ET
import collections
# 建立数据库连接
db = pymysql.connect(
    host='localhost',		# 主机名（或IP地址）
    port=3306,				# 端口号，默认为3306
    user='root',			# 用户名
    password='zhu203545',	# 密码
    charset='utf8mb4'  		# 设置字符编码
)
# 创建游标对象
cursor = db.cursor()
db.select_db("ir_db")

DATA_PATH = '../data/'
MOVIE_NUM = 2503
def create_movie_table():
    sql = """
        CREATE TABLE IF NOT EXISTS movies (
            id INT(11) PRIMARY KEY AUTO_INCREMENT,
            电影名 VARCHAR(100) NOT NULL,
            年份 YEAR NOT NULL,
            评分 FLOAT,
            封面 TEXT,
            导演 TEXT,
            演员 TEXT,
            简介 TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    cursor.execute(sql)

def create_review_table():
    # 暂时写这些
    sql = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INT(11) PRIMARY KEY AUTO_INCREMENT,
            movie_id INT(11) ,
            电影名 VARCHAR(100) NOT NULL,
            标题 VARCHAR(150) NOT NULL,
            作者 VARCHAR(30) NOT NULL,
            时间 DATETIME NOT NULL,
            作者评分 DECIMAL,
            影评 MEDIUMTEXT NOT NULL,
            有用数 INT(11),
            没用数 INT(11),
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    cursor.execute(sql)

def create_user_table():
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT(11) PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    cursor.execute(sql)

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

def get_root(index):
    # 解析XML文件
    path = DATA_PATH + '/movies/{}.xml'.format(index)
    tree = ET.parse(path, ET.XMLParser(encoding='utf-8'))
    root = tree.getroot()
    return root

def insert_movie(index):
    # 解析XML文件
    movie = get_root(index)
    # 提取数据
    data = {
        '电影名': movie.find('电影名').text.replace('"', '\"'),
        '年份': movie.find('年份').text,
        '评分': movie.find('评分').text,
        '封面': movie.find('封面').text,
        '导演': movie.find('导演').text,
        '演员': movie.find('演员').text,
        '简介': movie.find('简介').text
    }
    if data['评分'] is None:
        data['评分'] = '0'
    if data['简介'] is not None:
        data['简介'] = data['简介'].replace('"', '\\"')
    # 将数据插入到mysql
    sql = """
        INSERT INTO movies (电影名, 年份, 评分, 封面, 导演, 演员, 简介)
        VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")
    """ %(data['电影名'], data['年份'], data['评分'], data['封面'], data['导演'], data['演员'], data['简介'])
    #print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print("插入失败{}".format(index))

def insert_review(index):
    # 解析XML文件
    root = get_root(index)
    # 电影名
    movie_name = root.find('电影名').text.replace('"', '\\"')
    # 遍历所有的review，解析xml
    for i, review in enumerate(root.iter('review')):
        # find all child elements
        author = review.find('作者').text.replace('"', '\\"')
        try:
            title = review.find('标题').text.replace('"', '\\"')
        except:
            title = ''
        try:
            author_rating = review.find('作者评分').text
            if author_rating is None:
                author_rating = '0'
        except:
            author_rating = '0'
        time = review.find('时间').text
        review_text = review.find('影评').text.replace('"', '\\"')
        try:
            useful = review.find('有用数').text
            if useful is None:
                useful = '0'
        except:
            useful = '0'
        try:
            useless = review.find('没用数').text
            if useless is None:
                useless = '0'
        except:
            useless = '0'

        # 提取数据
        data = {
            'movie_id': index + 1,
            '电影名': movie_name,
            '标题': title,
            '作者': author, 
            '时间': time,
            '作者评分': author_rating,
            '影评': review_text,
            '有用数': useful,
            '没用数': useless
        }       

        # sql语句
        sql = """
            INSERT INTO reviews (movie_id, 电影名, 标题, 作者, 时间, 作者评分, 影评, 有用数, 没用数)
            VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")
        """ %(data['movie_id'], data['电影名'], data['标题'], data['作者'], data['时间'], data['作者评分'], data['影评'], data['有用数'], data['没用数'])
        try:
            cursor.execute(sql)
        except Exception as e:
            print("插入失败，{}th 电影，{}th评论".format(index, i))
            print(e)
            print(sql)
            exit(-1)
    db.commit()

def insert_user(username, password):
    # sql语句
    sql = """
        INSERT INTO users(username, password)
        VALUES("%s", "%s")
    """ %(username, password)
    cursor.execute(sql)
    db.commit()

def get_user(username):
    # sql语句
    sql = """
        SELECT * FROM users
        WHERE username="%s"
    """ %(username)
    cursor.execute(sql)
    db.commit()
    return cursor.fetchone()

def insert_query_log(user_id, query, time):
    # sql语句
    sql = """
        INSERT INTO query_log(user_id, query, timestamp)
        VALUES("%s", "%s", "%s")
    """ %(user_id, query, time)
    try:
        cursor.execute(sql)
    except Exception as e:
        print(e)
        print(sql)
        exit(-1)
    db.commit()
    
def get_most_common_queries(n=5):
    # 获取所有的查询记录
    cursor.execute("SELECT query FROM query_log")
    queries = [item[0] for item in cursor.fetchall()]
    queries = [' '.join(q.split(' ')[2:]) if 'site:' in q.split(' ')[1] else ' '.join(q.split(' ')[1:]) for q in queries]
    # 使用collections.Counter来统计查询的频率，并使用most_common方法来获取最常见的查询
    counter = collections.Counter(queries)
    c = counter.most_common(n)
    l = [item[0] for item in c]
    return l

def get_query_log(user_id):
    # sql语句
    sql = """
        SELECT * FROM query_log
        WHERE user_id="%s" order by timestamp desc
    """ %(user_id)
    cursor.execute(sql)
    db.commit()
    queries = [item[2] for item in cursor.fetchall()]
    queries = [' '.join(q.split(' ')[2:]) if 'site:' in q.split(' ')[1] else ' '.join(q.split(' ')[1:]) for q in queries]
    return queries

if __name__ == '__main__':
    # 创建数据库
    create_movie_table()
    create_review_table()

    for i in range(MOVIE_NUM):
        insert_movie(i)
        insert_review(i)

    # 关闭游标和连接
    cursor.close()
    db.close()

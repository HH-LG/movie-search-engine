import pymysql
import xml.etree.ElementTree as ET
# 建立数据库连接
db = pymysql.connect(
    host='localhost',		# 主机名（或IP地址）
    port=3306,				# 端口号，默认为3306
    user='root',			# 用户名
    password='zhu203545',	# 密码
    charset='utf8'  		# 设置字符编码
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    """
    cursor.execute(sql)

def create_review_table():
    # 暂时写这些
    sql = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INT(11) PRIMARY KEY AUTO_INCREMENT,
            电影名 VARCHAR(100) NOT NULL,
            评分 DECIMAL,
            评论 TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    """
    cursor.execute(sql)

def insert_movie(index):
    # 解析XML文件
    path = DATA_PATH + '/movies/{}.xml'.format(index)
    tree = ET.parse(path, ET.XMLParser(encoding='utf-8'))
    movie = tree.getroot()
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
    # 将数据插入到Elasticsearch的索引中
    sql = """
        INSERT INTO movies (电影名, 年份, 评分, 封面, 导演, 演员, 简介)
        VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")
    """ %(data['电影名'], data['年份'], data['评分'], data['封面'], data['导演'], data['演员'], data['简介'])
    #print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("插入失败{}".format(index))

def insert_review(index):
    # 解析XML文件
    path = DATA_PATH + '/movies/{}.xml'.format(index)
    tree = ET.parse(path, ET.XMLParser(encoding='utf-8'))
    review = tree.getroot()
    # 提取数据
    data = {
        '电影名': review.find('电影名').text,
    }
    # 将数据插入到Elasticsearch的索引中
    sql = """
        INSERT INTO reviews (电影名, 评分, 评论)
        VALUES ("%s", "%s", "%s")
    """ %(data['电影名'], data['评分'], data['评论'])
    #print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("插入失败{}".format(index))

if __name__ == '__main__':
    # 创建数据库
    create_movie_table()
    #create_review_table()
    #for i in range(MOVIE_NUM):
        #insert_movie(i)
    #insert_movie(1241)
    # Parse XML file
    tree = ET.parse('../7.xml')
    root = tree.getroot()

    # Find all 'review' elements
    for review in root.findall('review'):
        # For each 'review', find and print all child elements
        author = review.find('作者').text
        title = review.find('标题').text
        author_rating = review.find('作者评分').text
        time = review.find('时间').text
        review_text = review.find('影评').text

        print("作者:", author)
        print("标题: ", title)
        print("作者评分: ", author_rating)
        print("时间: ", time)
        print("影评: ", review_text)


# 关闭游标和连接
cursor.close()
db.close()

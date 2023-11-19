import pymysql

# 连接数据库
db = pymysql.connect(host='localhost',
                     port=3306,
                     user='root',
                     password='zhu203545',
                     database='ir_db',
                     charset='utf8')
# 获取游标(操作数据库，执行sql语句，承载结果)
cur = db.cursor()
# 执行SQL语句
sql = '''create table movie(id int primary key auto_increment
            ,name varchar(30) not null)
'''
cur.execute(sql)
# 提交写操作，可将多次写操作一起提交
db.commit()
cur.close()
db.close()

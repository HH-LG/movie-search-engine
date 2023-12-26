import pymysql
import jieba
from gensim.models import word2vec, Word2Vec
from database import *

DATA_PATH = '../data/'
def get_dbtext(db):
    cursor = db.cursor()
    sql1 = "select 电影名 from movies"
    #sql2 = "select 标题 from reviews"

    try:
        cursor.execute(sql1)
        result = cursor.fetchall()
        #cursor.execute(sql2)
        #result += cursor.fetchall()
        if result is None:
            print('not found')
            return ' '
        else:
            return result
    except:
        db.rollback()
        print('查询失败')
    cursor.close()



def write_file():
    result = get_dbtext(db)
    with open(DATA_PATH + 'text.txt', 'wb') as f:
        for r in result:
            f.write(r[0].encode('utf-8'))

def cut_words():
    with open(DATA_PATH + 'text.txt', 'r', encoding='utf-8') as content:
        for line in content:
            # new_line = re.sub("[\s+\.\!\/_,$%^*(\"\']+|[+——！，。？、~@#￥%……&*（）,._，。/]+", "",line)
            seg_list = jieba.cut(line)
            with open(DATA_PATH + 'seg_text.txt', 'a', encoding='utf-8') as output:
                output.write(' '.join(seg_list))

def train():
    num_features = 300  # Word vector dimensionality
    min_word_count = 10  # Minimum word count
    num_workers = 16  # Number of threads to run in parallel
    context = 10  # Context window size
    downsampling = 1e-3  # Downsample setting for frequent words
    sentences = word2vec.Text8Corpus(DATA_PATH + "seg_text.txt")

    model = word2vec.Word2Vec(sentences, workers=num_workers,
                              vector_size=num_features, min_count=min_word_count,
                              window=context, sg=1, sample=downsampling)
    model.init_sims(replace=True)
    # 保存模型，供日后使用
    model.save("model")

def get_similar_words(model, words, topn=10):
    similar_words = model.wv.most_similar(words, topn=topn)
    similar_words = [word[0] for word in similar_words]
    print(similar_words)
    return similar_words

if __name__ == '__main__':
    #write_file()
    #cut_words()
    #train()
    model = Word2Vec.load('model')
    s =get_similar_words(model, ['肖申克','救赎'],topn=10)  # 根据给定的条件推断相似词
    print(s)
    query = '肖申克的救赎'
    seg_list = []
    for s in query.split(' '):
        seg_list += jieba.cut(s)
    print(get_similar_words(model, seg_list, topn=8))

from collections import Counter
from database import *
import pickle
import jieba    

DATA_PATH = '../data/'
HISTORY_REF_NUM = 100

def normalize(corpus):
    normalized_corpus = []
    for text in corpus:
        text = ' '.join(jieba.lcut(text))
        normalized_corpus.append(text)
    
    return normalized_corpus

def get3FavoriteCluster(user_id, kmeans, vectorizer):

    query_history = get_query_log(user_id)
    if query_history is None or len(query_history) == 0:
        return None
    query_history = query_history[:HISTORY_REF_NUM]
    query_history = normalize(query_history)

    query_vectors = vectorizer.transform(query_history)
    cluster_counts = Counter(kmeans.predict(query_vectors))


    favorite3Cluster = [item[0] for item in cluster_counts.most_common(3)]
    return favorite3Cluster


if __name__ == '__main__':
    # 使用 TF-IDF 将文本转换为向量
    vectorizer = pickle.load(open(DATA_PATH + 'vectorizer.pkl', 'rb'))
    kmeans = pickle.load(open(DATA_PATH + 'kmeans.pkl', 'rb'))
    print(get3FavoriteCluster(1, kmeans, vectorizer))

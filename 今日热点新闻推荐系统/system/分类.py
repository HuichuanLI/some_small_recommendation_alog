from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import feature_extraction
from os import listdir
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
import jieba
import os
import re
import shutil
import glob

labels = []  # 用于存储所有文本标题


def loadDataset():
    '''导入文本数据集，建立语料库'''
    all_file = listdir('./今日新闻/过滤')
    corpus = []
    typetext = open('./stop.txt', encoding='UTF-8')  # 加载停用词表
    texts = ['\u3000', '\n', '']
    for word in typetext:
        word = word.strip()
        texts.append(word)
    for i in range(0, len(all_file)):
        filename = all_file[i]
        filelabel = filename.split('.')[0]
        labels.append(filelabel)  # 所有文本标题
        file_add = './今日新闻/过滤/' + filename
        doc = open(file_add, encoding='utf-8').read()
        data = jieba.cut(doc)  # 对打开的文本进行分词
        data_adj = ""
        delete_word = []
        for item in data:  # 运用停用词表进行过滤
            if item not in texts:
                data_adj = data_adj + item + ' '
            else:
                delete_word.append(item)
        corpus.append(data_adj)
    return corpus


def transform(dataset, n_features=1000):
    '''将文本数据转化为词频矩阵'''
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=n_features, min_df=2, use_idf=True)
    X = vectorizer.fit_transform(dataset)

    return X, vectorizer


def train(X, vectorizer, true_k=10, minibatch=False, showLable=False):
    # 使用采样数据还是原始数据训练k-means，
    if minibatch:
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=False)
    else:
        km = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=1,
                    verbose=False)
    km.fit(X)
    y = km.fit_predict(X)
    for i in range(true_k):
        label_i = []
        fileNames = glob.glob('./今日新闻/分类/label_' + str(i) + '/' + r'\*')
        for filename in fileNames:
            os.remove(filename)  # 清除原分类文件夹下的文件
        for j in range(0, len(y)):
            if y[j] == i:
                label_i.append(labels[j])
                title = labels[j]
                shutil.copy('./今日新闻/' + title + '.txt', './今日新闻/分类/label_' + str(i) + '/' + title + '.txt')
                # 把符合分类条件的文本复制入对应分类文件夹
        print('label_' + str(i) + ':' + str(label_i) + '\n')

    if showLable:
        print("Top terms per cluster:")
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()  # 分类后文本中心词
        print(vectorizer.get_stop_words())
        for i in range(true_k):
            print("Cluster %F:" % i, end='  ')  # 输出类名
            for ind in order_centroids[i, :10]:
                print(' %s' % terms[ind], end='')  # 输出该类文本的前10个中心词
            print()
    result = list(km.predict(X))
    print('Cluster distribution:')
    print(dict([(i, result.count(i)) for i in result]))  # 输出分类组成，即每一类的文本个数
    return -km.score(X)


def test():
    '''测试选择最优参数'''
    dataset = loadDataset()
    print("%d documents" % len(dataset))
    X, vectorizer = transform(dataset, n_features=500)
    true_ks = []
    scores = []
    # 依次对不同k取值进行测试得到其轮廓系数，保存每次结果并以曲线图呈现
    for i in range(3, 80, 1):
        sl = 0
        for j in range(0, 10):  # 对每个k值进行多次kmeans聚类，得到轮廓系数的平均值
            score = train(X, vectorizer, true_k=i) / len(dataset)
            sl = sl + score
        print(i, score)
        true_ks.append(i)
        scores.append(sl / 10)
    # 画图
    plt.figure(figsize=(8, 4))
    plt.plot(true_ks, scores, label="error", color="red", linewidth=1)
    plt.xlabel("n_features")
    plt.ylabel("error")
    plt.legend()
    plt.show()


def out():
    '''在最优参数下输出聚类结果'''

    for i in range(47, 50):
        if os.path.exists('F:/今日新闻/分类/label_' + str(i) + '/'):
            shutil.rmtree('F:/今日新闻/分类/label_' + str(i) + '/')  # 删除分类预备多建立的分类文件夹

    dataset = loadDataset()
    X, vectorizer = transform(dataset, n_features=500)
    # 在最优参数下进行多次聚类，当轮廓系数小于0.617时表示符合要求，并取该次结果为最终结果
    for i in range(0, 1000):
        score = train(X, vectorizer, true_k=47, showLable=True) / len(dataset)
        print(score)
        if score < 0.617:
            break


# test()
out()
# os.system("pause")

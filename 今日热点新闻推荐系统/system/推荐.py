# encoding:utf-8
# ! python3
# -*- coding: utf-8 -*-

import os
import math
import linecache
import re
import codecs
import time
import jieba
from jieba import analyse
from collections import Counter

import matplotlib.pyplot as plt
from wordcloud import WordCloud


def fenci(txtPath):
    with codecs.open(txtPath, 'r', 'utf8') as f:
        txt = f.read()
    seg_list = jieba.cut(txt)
    # 创建停用词list
    stopwords = [line.strip() for line in open('./stop.txt', 'r', encoding='utf-8').readlines()]
    clean_list = []
    for word in seg_list:
        if word not in stopwords:
            if ord(word[0]) > 127:
                if word != '\t':
                    clean_list.append(word)
    return clean_list


def tf(seg_list):
    dic_value = {}
    for word in seg_list:
        if len(word) > 1 and word != '\r\n':
            if not dic_value.get(word):
                dic_value[word] = [1, 0]
            else:
                dic_value[word][0] += 1
    return dic_value


def idf(filePath, dic_value):
    N = 0  # 文章篇数
    idf = 0
    files = os.listdir(filePath)
    for file in files:
        N += 1
    for word in dic_value:
        df = 0
        for file in files:
            # 读入每个txt文件
            txtPath = filePath + '/' + file
            with codecs.open(txtPath, 'r', 'utf8') as f:
                txt = f.read()
            # 判断该词是否在txt中出现
            if re.findall(word, txt, flags=0):
                df += 1
        if df:
            idf = N / df
        dic_value[word][1] = idf
    return dic_value


def weight(dic_value):
    w_value = {}
    weight = 0
    for key in dic_value:
        weight = dic_value[key][0] * dic_value[key][1]
        w_value[key] = weight
    return w_value


def cos(w1_value, w2_value):
    w_mul = 0
    w1_exp = 0
    w2_exp = 0
    cos = 0
    fenzi = 0
    for word in w1_value:
        if word in w2_value:
            w_mul += float(w2_value[word])
            w1_exp += math.pow(1, 2)
            w2_exp += math.pow(w2_value[word], 2)
    fenzi = (math.sqrt(w1_exp) * math.sqrt(w2_exp))
    if fenzi:
        cos = w_mul / (math.sqrt(w1_exp) * math.sqrt(w2_exp))
    return cos


def similarity(filePath, standard):
    files = os.listdir(filePath)
    stan_list = jieba.cut(standard)
    w1_value = tf(stan_list)
    sim = {}
    for file in files:
        txtPath = filePath + '/' + file
        seg_list = fenci(txtPath)
        tf_value = tf(seg_list)
        dic_value = idf(filePath, tf_value)
        w2_value = weight(dic_value)
        cos_value = cos(w1_value, w2_value)
        sim[file] = cos_value
    sim_sort = sorted(sim.items(), key=lambda item: item[1], reverse=True)
    i = 0
    for ns_name in sim_sort:
        if i < 3:
            real_name = re.sub(".txt", "", ns_name[0])
            real_name = "    " + real_name
            print(real_name)
        else:
            break
        i += 1


def hot_news(filePath):
    # 对类中的每篇新闻操作
    files = os.listdir(filePath)  # 得到文件夹下的所有文件名称
    Atime = [0] * 50  # 记录每小时内的新闻数
    i = -1
    a = 0.8
    for file in files:  # 遍历文件夹
        i = (i + 1) % 12 + 12
        if not os.path.isdir(file):  # 判断是否为文件夹，不是文件夹就打开
            # txt_judge = linecache.getline(filePath + "\\" + file, 2).strip()
            # if re.match('发布时间', txt_judge):
            news = linecache.getline(filePath + "\\" + file, 3).strip()
            if re.findall(r'[0-9]+-[0-9]+-[0-9]+', news, flags=0):
                date_string = re.findall(r'[0-9]+-[0-9]+-[0-9]+', news, flags=0)
                # print(date_string)
                time_string = re.findall(r'[0-9]+:[0-9]+:[0-9]+', news, flags=0)
                # print(time_string)
                news_time_string = date_string[0] + " " + time_string[0]
                # print(news_time_string)
                news_time = int(time.mktime(time.strptime(news_time_string, "%Y-%m-%d %H:%M:%S")))
                now_data = '2020-03-25 00:00:00'
                now = int(time.mktime(time.strptime(now_data, "%Y-%m-%d %H:%M:%S")))
                delta = now - news_time
                m, s = divmod(delta, 60)
                h, m = divmod(m, 60)
                Atime[h] = int(Atime[h]) + 1
            else:
                Atime[i] = int(Atime[i]) + 1
        else:
            continue
    # 指数衰减公式
    i = 0
    weight = 0
    while i < 50:
        weight = weight + a * math.pow((1 - a), i) * Atime[i]
        i += 1
    return weight


def keyword(filePath):
    # 提取关键字
    files = os.listdir(filePath)  # 得到文件夹下的所有文件名
    s = []
    context = " "
    for file in files:  # 遍历文件夹
        if not os.path.isdir(file):  # 判断是否为文件夹，不是文件夹就打开
            f = open(filePath + "/" + file, 'r', encoding='utf-8')  # 打开文件
            iter_f = iter(f)  # 创建迭代器
            for line in iter_f:  # 遍历文件，以行遍历，读取文本
                context = context + line
            s.append(context)  # 每个文件文本保存到context中
        else:
            context = "null"

    jieba.analyse.set_stop_words('./stop.txt')
    textrank = analyse.textrank
    keywords = textrank(context)
    return keywords


def hotnews(rootDir):
    news_weight = {}
    count = 0
    dirs1 = os.listdir(rootDir)
    for dir1 in dirs1:  # 得到该类的关键词后为文件重命名
        news_keywords = keyword(rootDir + "/" + dir1)
        news_keyword = news_keywords[0] + news_keywords[1]
        os.rename(rootDir + "/" + dir1, rootDir + "/" + news_keyword)
    dirs2 = os.listdir(rootDir)
    for dir2 in dirs2:
        key = dir2
        value = hot_news(rootDir + "/" + dir2)
        if key not in news_weight.keys():
            news_weight[key] = value
    news_sort = sorted(news_weight.items(), key=lambda item: item[1], reverse=True)
    i = 0
    for news_name in news_sort:
        if i < 15:
            print(news_name[0])
            similarity(rootDir + '/' + news_name[0], news_name[0])
        else:
            break
        i += 1


def time_judge(txtPath):
    news = linecache.getline(txtPath, 3).strip()
    if re.findall(r'[0-9]+-[0-9]+-[0-9]+', news, flags=0):
        date_string = re.findall(r'[0-9]+-[0-9]+-[0-9]+', news, flags=0)
        time_string = re.findall(r'[0-9]+:[0-9]+:[0-9]+', news, flags=0)
        news_time_string = date_string[0] + " " + time_string[0]
        news_time = int(time.mktime(time.strptime(news_time_string, "%Y-%m-%d %H:%M:%S")))
        now_data = '2020-03-25 00:00:00'
        now = int(time.mktime(time.strptime(now_data, "%Y-%m-%d %H:%M:%S")))
        # now_data = time.time()
        delta = news_time - now
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        if h <= 24 & h > 12:
            return 3
        else:
            return 2
    else:
        return 3


def hotwords(filePath):
    value = Counter()
    tf_value = {}
    for root, dirs, files in os.walk(filePath):  # dirs 不能去掉
        for file in files:
            txtPath = os.path.join(root, file)
            seg_list = fenci(txtPath)
            judge = time_judge(txtPath)
            if judge == 2:
                for new in seg_list:
                    if len(new) > 1 and new != '\r\n':
                        if not tf_value.get(new):
                            tf_value[new] = [0, 1]
                        else:
                            tf_value[new][1] += 1
                        # print("这是新词")
                        # print(tf_value[new])
            else:
                for old in seg_list:
                    if len(old) > 1 and old != '\r\n':
                        if not tf_value.get(old):
                            tf_value[old] = [1, 0]
                        else:
                            tf_value[old][0] += 1
                        # print("这是旧词")
                        # print(tf_value[old])

    for key in tf_value:
        if tf_value[key][0] == 0:
            continue
        result = tf_value[key][1] / (tf_value[key][1] + tf_value[key][0])
        value[key] = result
    text1 = ""
    for (k, v) in value.most_common(12):
        text1 = text1 + " " + k

    wc = WordCloud(
        background_color="white",  # 设置背景为白色，默认为黑色
        collocations=False, width=1400, height=1400, margin=2
    ).generate(text1.lower())
    # 为云图去掉坐标轴
    plt.axis("off")
    # 画云图，显示
    # plt.show(wc)
    # 保存云图
    wc.to_file("./wordcloud.png")


def interet(filePath):
    print("请输入你感兴趣的新闻话题：")
    words = input()

    w1_value = {}
    w1_value[words] = 1

    files = os.listdir(filePath)
    sim = {}
    news_name = []
    for root, dirs, files in os.walk(filePath):  # dirs 不能去掉
        for file in files:
            txtPath = os.path.join(root, file)
            seg_list = fenci(txtPath)
            tf_value = tf(seg_list)
            dic_value = idf(root, tf_value)
            w2_value = weight(dic_value)
            cos_value = cos(w1_value, w2_value)
            sim[file] = cos_value
    sim_sort = sorted(sim.items(), key=lambda item: item[1], reverse=True)
    i = 0
    for ns_name in sim_sort:
        if i < 3:
            real_name = re.sub(".txt", "", ns_name[0])
            news_name.append(real_name)
            print(i + 1, '、', news_name[i])
        else:
            break
        i += 1


if __name__ == "__main__":
    start = time.time()
    filePath = 'F:\今日新闻\分类'

    # 热点新闻呈现
    hotnews(filePath)
    # 热词呈现
    hotwords(filePath)
    # 兴趣新闻
    interet(filePath)

    end = time.time()
    delta = end - start
    m, s = divmod(delta, 60)
    h, m = divmod(m, 60)
    print("\nTime cost: %02F:%02F:%02d" % (h, m, s))

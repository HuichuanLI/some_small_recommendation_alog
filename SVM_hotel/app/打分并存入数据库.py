import sys
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.decomposition import PCA
# from sklearn import svm
# from sklearn import metrics
from sklearn.externals import joblib
# import joblib
import collections
import mysql.connector

clf = joblib.load("my_model_1.m")


def countgrades(filename):
    df = pd.read_csv(filename)
    x = df.iloc[:, 2:]
    predict = clf.predict(x)
    pred_probas = clf.predict_proba(x)
    x = collections.Counter(predict)
    x0 = x[0]
    x1 = x[1]
    grades = 100 * x1 / (x1 + x0)
    return grades


if __name__ == "__main__":
    conn = mysql.connector.connect(user='root', password='12345678', database='grades', use_unicode=True,
                                   auth_plugin='mysql_native_password')
    cursor = conn.cursor()
    filename1 = "./comment_data.csv"
    grades1 = countgrades(filename1)
    cursor.execute('insert into grades (hotel,grades) values(%s,%s)', ('南京全季酒店', int(grades1)))
    print('南京全季酒店的分数是: %.2f' % grades1)
    filename2 = "comment_bupt_data.csv"
    grades2 = countgrades(filename2)
    cursor.execute('insert into grades (hotel,grades) values(%s,%s)', ('北邮科技酒店', int(grades2)))
    print('北邮科技酒店的分数是: %.2f' % grades2)
    filename3 = "comment_pku_data.csv"
    grades3 = countgrades(filename3)
    cursor.execute('insert into grades (hotel,grades) values(%s,%s)', ('北大博雅酒店', int(grades3)))
    print('北大博雅酒店的分数是: %.2f' % grades3)
    filename4 = "comment_beiwai_data.csv"
    grades4 = countgrades(filename4)
    cursor.execute('insert into grades (hotel,grades) values(%s,%s)', ('鹤佳酒店', int(grades4)))
    print('鹤佳酒店的分数是: %.2f' % grades4)
    filename5 = "comment_beijiao_data.csv"
    grades5 = countgrades(filename5)
    cursor.execute('insert into grades (hotel,grades) values(%s,%s)', ('乐家服务酒店', int(grades5)))
    print('乐家服务酒店的分数是: %.2f' % grades5)
    conn.commit()
    cursor.close()

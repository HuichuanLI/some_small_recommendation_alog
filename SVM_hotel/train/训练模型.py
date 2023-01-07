#!/usr/bin/env python
# -*- coding: utf-8  -*-
# PCA  SVM
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn import svm
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

# 获取数据 [1995 rows x 256 columns]
fdir = ''
df = pd.read_csv(fdir + '2000_data.csv')
y = df.iloc[:, 1].values
x = df.iloc[:, 2:].values
(x_train, x_test, y_train, y_test) = train_test_split(x, y, test_size=0.2, random_state=1)
clf = svm.SVC(C=10, kernel='rbf', gamma=0.38, probability=True)  ##训练
clf.fit(x_train, y_train)
# clf.fit(x,y)
print('train Accuracy: %.2f' % clf.score(x_train, y_train))
print('Test Accuracy: %.2f' % clf.score(x_test, y_test))
# print 'Test Accuracy: %.2f'% clf.score(x,y)
pred_probas = clf.predict_proba(x)[:, 1]  # score
fpr, tpr, _ = metrics.roc_curve(y, pred_probas)
roc_auc = metrics.auc(fpr, tpr)
plt.plot(fpr, tpr, label='area = %.2f' % roc_auc)
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.legend(loc='lower right')
plt.show()
joblib.dump(clf, "my_model_1.m")

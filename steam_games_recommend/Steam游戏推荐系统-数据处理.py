#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import random
from collections import Counter
from sklearn.metrics import roc_curve, auc, average_precision_score
import joblib

# 导入数据集并列表显示
path = './steam-video-games/steam-200k.csv'
df = pd.read_csv(path, header = None, names = ['UserID', 'Game', 'Action', 'Hours', 'Not Needed'])
df.head()
# 从购买记录和游玩记录中筛选出游戏时长
df['Hours_Played'] = df['Hours'].astype('float32')
df.loc[(df['Action'] == 'purchase') & (df['Hours'] == 1.0), 'Hours_Played'] = 0

# 排序
df.UserID = df.UserID.astype('int')
df = df.sort_values(['UserID', 'Game', 'Hours_Played'])

# 整理为新的表格clean_df
clean_df = df.drop_duplicates(['UserID', 'Game'], keep = 'last').drop(['Action', 'Hours', 'Not Needed'], axis = 1)
clean_df.head()
n_users = len(clean_df.UserID.unique())
n_games = len(clean_df.Game.unique())
print('用户-游戏数据集中一共有{0}个用户，{1}个游戏'.format(n_users, n_games))
# 计算矩阵的稀疏程度
sparsity = clean_df.shape[0] / float(n_users * n_games)
print('用户-游戏矩阵中有效数据占比为：{:.2%}'.format(sparsity))
# 建立序列化的id方便使用

# 用户id到用户序列化id的字典
user2idx = {user: i for i, user in enumerate(clean_df.UserID.unique())}
# 用户序列化id到用户id的字典
idx2user = {i: user for user, i in user2idx.items()}

# 游戏名到游戏序列化id的字典
game2idx = {game: i for i, game in enumerate(clean_df.Game.unique())}
# 游戏序列化id到游戏名的字典
idx2game = {i: game for game, i in game2idx.items()}

# 将字典保存，用于PyQt5中
joblib.dump(idx2game, './Save_data/idx2game.pkl')
joblib.dump(game2idx, './Save_data/game2idx.pkl')
# 用户序列化id-游戏序列化id-游戏时长
user_idx = clean_df['UserID'].apply(lambda x: user2idx[x]).values
game_idx = clean_df['gamesIdx'] = clean_df['Game'].apply(lambda x:game2idx[x]).values
hours = clean_df['Hours_Played'].values
# 保存游戏时长矩阵
hours_save = np.zeros(shape = (n_users, n_games))
for i in range(len(user_idx)):
    hours_save[user_idx[i], game_idx[i]] = hours[i]
joblib.dump(hours_save, './Save_data/hours.pkl')
# 建立稀疏矩阵存储大数据集
# 
# 购买矩阵:
# 未购买标识为0
# 购买标识为1
# 
# 置信度矩阵：
# 根据游戏时长提高置信度，最低为1

zero_matrix = np.zeros(shape = (n_users, n_games))
# 购买矩阵
user_game_pref = zero_matrix.copy()
user_game_pref[user_idx, game_idx] = 1
# 保存购买矩阵
joblib.dump(user_game_pref, './Save_data/buy.pkl')
# 置信度矩阵
user_game_interactions = zero_matrix.copy()
user_game_interactions[user_idx, game_idx] = hours + 1
k = 5

# 对于每个用户计算他们购买的游戏数量
purchase_counts = np.apply_along_axis(np.bincount, 1, user_game_pref.astype(int))
buyers_idx = np.where(purchase_counts[:, 1] >= 2 * k)[0] #购买超过2*k个游戏的买家集合
print('{0}名玩家购买了至少{1}款游戏'.format(len(buyers_idx), 2 * k))
# 保存有效购买用户名单
joblib.dump(buyers_idx, './Save_data/buyers.pkl')
test_frac = 0.2 # 10%数据用来验证，10%数据用来测试
test_users_idx = np.random.choice(buyers_idx, 
                                  size = int(np.ceil(len(buyers_idx) * test_frac)), 
                                  replace = False)
val_users_idx = test_users_idx[:int(len(test_users_idx) / 2)]
test_users_idx = test_users_idx[int(len(test_users_idx) / 2):]
# 在训练集中掩盖k个游戏
def data_process(dat, train, test, user_idx, k):
    for user in user_idx:
        purchases = np.where(dat[user, :] == 1)[0]
        mask = np.random.choice(purchases, size = k, replace = False)
        train[user, mask] = 0
        test[user, mask] = dat[user, mask]
    return train, test
train_matrix = user_game_pref.copy()
test_matrix = zero_matrix.copy()
val_matrix = zero_matrix.copy()

train_matrix, val_matrix = data_process(user_game_pref, train_matrix, val_matrix, val_users_idx, k)
train_matrix, test_matrix = data_process(user_game_pref, train_matrix, test_matrix, test_users_idx, k)


tf.reset_default_graph()

# 偏好矩阵
pref = tf.placeholder(tf.float32, (n_users, n_games))
# 游戏时间矩阵
interactions = tf.placeholder(tf.float32, (n_users, n_games))
user_idx = tf.placeholder(tf.int32, (None))
n_features = 30 # 隐藏特征个数设置为30

# X矩阵（用户-隐藏特征）表示用户潜在偏好
X = tf.Variable(tf.truncated_normal([n_users, n_features], mean = 0, stddev = 0.05), dtype = tf.float32, name = 'X')
# Y矩阵（游戏-隐藏特征）表示游戏潜在特征
Y = tf.Variable(tf.truncated_normal([n_games, n_features], mean = 0, stddev = 0.05), dtype = tf.float32, name = 'Y')

# 置信度参数初始化
conf_alpha = tf.Variable(tf.random_uniform([1], 0,1))
# 初始化用户偏差
user_bias = tf.Variable(tf.truncated_normal([n_users, 1], stddev = 0.2))

# 将向量连接到用户矩阵
X_plus_bias = tf.concat([X,
                        user_bias,
                        tf.ones((n_users, 1), dtype = tf.float32)], 
                        axis = 1)
# 初始化游戏偏差
item_bias = tf.Variable(tf.truncated_normal([n_games, 1], stddev = 0.2))

# 将向量连接到游戏矩阵
Y_plus_bias = tf.concat([Y,
                        tf.ones((n_games, 1), dtype = tf.float32),
                        item_bias],
                        axis = 1)
# 通过矩阵乘积确定结果评分矩阵
pred_pref = tf.matmul(X_plus_bias, Y_plus_bias, transpose_b = True)

# 使用游戏时长与alpha参数构造置信度矩阵
conf = 1 + conf_alpha * interactions
#损失函数
cost = tf.reduce_sum(tf.multiply(conf, tf.square(tf.subtract(pref, pred_pref))))
l2_sqr = tf.nn.l2_loss(X) + tf.nn.l2_loss(Y) + tf.nn.l2_loss(user_bias) + tf.nn.l2_loss(item_bias)
lambda_c = 0.01
loss = cost + lambda_c * l2_sqr
#梯度下降算法优化器
lr = 0.05
optimize = tf.train.AdagradOptimizer(learning_rate = lr).minimize(loss)

# 精确度计算优化，将游戏本体和DLC合并为同一种游戏
def precision_dlc(recommandations, labels):
    # 推荐的游戏按单词划分
    recommandations_split = []
    # 实际购买的游戏按单词划分
    labels_split = []
    for label in labels:
        labels_split.append(idx2game[label].split())
    for game in recommandations:
        recommandations_split.append(idx2game[game].split())
        
    count = 0
    for game in recommandations_split:
        for label in labels_split:
            # 当推荐的游戏与实际购买的游戏单词重合度高于阈值判定为同一款游戏
            if (len(set(game) & set(label)) / min(len(game),len(label))) > 0.2:
                count += 1
                break
    
    return float(count / len(recommandations))

# 从预测的列表中挑选最高的k个
def top_k_precision(pred, mat, k, user_idx):
    precisions = []
    for user in user_idx:
        rec = np.argsort(-pred[user, :])
        # 选取推荐评分最高的k个
        top_k = rec[:k]
        labels = mat[user, :].nonzero()[0]
        # 计算推荐与实际的准确率并返回
        precision = precision_dlc(top_k, labels)
        precisions.append(precision)
    return np.mean(precisions)

iterations = 500
# 绘图用数据：误差、训练集准确率
fig_loss = np.zeros([iterations])
fig_train_precision = np.zeros([iterations])

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    for i in range(iterations):
        sess.run(optimize, feed_dict = {pref: train_matrix, 
                                       interactions: user_game_interactions})
        if i % 10 == 0:
            mod_loss = sess.run(loss, feed_dict = {pref: train_matrix,
                                                   interactions: user_game_interactions})
            mod_pred = pred_pref.eval()
            train_precision = top_k_precision(mod_pred, train_matrix, k, val_users_idx)
            val_precision = top_k_precision(mod_pred, val_matrix, k, val_users_idx)
            print('当前进度：{}...'.format(i),
                  '误差为：{:.2f}...'.format(mod_loss),
                  '训练集上的正确率：{:.3f}...'.format(train_precision),
                  '验证集上的正确率：{:.3f}'.format(val_precision))
        fig_loss[i] = sess.run(loss, feed_dict = {pref: train_matrix,
                                                  interactions: user_game_interactions})
        fig_train_precision[i] = top_k_precision(mod_pred, train_matrix, k, val_users_idx)
    rec = pred_pref.eval()
    test_precision = top_k_precision(rec, test_matrix, k, test_users_idx)
    print('\n')
    print('模型完成，正确率为：{:.3f}'.format(test_precision))

#验证测试
n_examples = 5
users = np.random.choice(test_users_idx, size = n_examples, replace = False)
rec_games = np.argsort(-rec)

for user in users:
    purchase_history = np.where(train_matrix[user, : ] != 0)[0]
    recommandations = rec_games[user, : ]
    new_recommandations = recommandations[~np.in1d(recommandations, purchase_history)][:k]
    
    print('给id为{0}的玩家推荐的游戏如下：'.format(idx2user[user]))
    print('，'.join([idx2game[game] for game in new_recommandations]))
    print('玩家实际购买游戏如下：')
    print('，'.join([idx2game[game] for game in np.where(test_matrix[user, : ] != 0)[0]]))
    print('准确率：{:.2f}%'.format( 100 * precision_dlc(new_recommandations, np.where(test_matrix[user, : ] != 0)[0])))
    print('\n')

# 将训练得到的评分矩阵保存
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    joblib.dump(pred_pref.eval(), './Save_data/rec.pkl')

#绘制训练图
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['KaiTi']

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
lns1 = ax1.plot(np.arange(iterations), fig_loss, label = 'Loss')
lns2 = ax2.plot(np.arange(iterations), fig_train_precision, 'r', label = 'Train Accuracy')
ax1.set_xlabel('训练轮次')
ax1.set_ylabel('训练损失值')
ax2.set_ylabel('训练准确率')
# 合并图例
lns = lns1 + lns2
labels = ['损失', '准确率']
plt.legend(lns, labels, loc=7)
plt.show()
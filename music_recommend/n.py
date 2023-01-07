import numpy as np
import pandas
import math

# 基于流行度的推荐模型
class popularity_recommender_py():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.popularity_recommendations = None

    # 创建基于流行度的推荐模型
    def create(self, train_data, user_id, item_id):
        self.train_data = train_data
        self.user_id = user_id
        self.item_id = item_id
    # 获取每个item的播放量，作为推荐指标
        train_data_grouped = train_data.groupby([self.item_id]).agg({self.user_id: 'count'}).reset_index()
    #为了直观展示，用得分表示结果
        train_data_grouped.rename(columns={user_id: 'score'}, inplace=True)
    #根据得分给歌曲排序
        train_data_sort = train_data_grouped.sort_values(['score', self.item_id], ascending=[0, 1])
    #加入一项排行等级，表示其推荐的优先级
        train_data_sort['Rank'] = train_data_sort['score'].rank(ascending=0, method='first')
    # 得到top10列表
        self.popularity_recommendations = train_data_sort.head(10)
    #使用基于流行度的算法进行推荐
    def recommend(self, user_id):
        user_recommendations = self.popularity_recommendations
    #根据用户id为指定用户生成推荐列表
        user_recommendations['user_id'] = user_id
        cols = user_recommendations.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        user_recommendations = user_recommendations[cols]
        return user_recommendations

#基于项目的协同过滤推荐
class item_similarity_recommender_py():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.cooccurence_matrix = None
        self.songs_dict = None
        self.rev_songs_dict = None
        self.item_similarity_recommendations = None
    #给定用户，找出用户听过的所有歌曲
    def get_user_items(self, user):
        user_data = self.train_data[self.train_data[self.user_id] == user]
        user_items = list(user_data[self.item_id].unique())
        return user_items
    #给定歌曲，找出听过这首歌的所有用户
    def get_item_users(self, item):
        item_data = self.train_data[self.train_data[self.item_id] == item]
        item_users = set(item_data[self.user_id].unique())
        return item_users
    #对数据集中的歌曲去重
    def get_all_items_train_data(self):
        all_items = list(self.train_data[self.item_id].unique())
        return all_items

    #Jaccard系数构建相似度矩阵
    def construct_cooccurence_matrix(self, user_songs, all_songs):
        user_songs_users = []
        for i in range(0, len(user_songs)):
            user_songs_users.append(self.get_item_users(user_songs[i]))
        #设置矩阵大小为某一指定用户听过的所有歌曲×数据集中歌曲总数
        cooccurence_matrix = np.matrix(np.zeros(shape=(len(user_songs), len(all_songs))), float)

        for i in range(0, len(all_songs)):
            #找出用户听过的第i首歌被哪些人听过
            songs_i_data = self.train_data[self.train_data[self.item_id] == all_songs[i]]
            users_i = set(songs_i_data[self.user_id].unique())
            #找出歌曲集中第j首歌被哪些人听过
            for j in range(0, len(user_songs)):
                users_j = user_songs_users[j]

                # 计算听过i歌曲人数和j歌曲人数的交集
                users_intersection = users_i.intersection(users_j)

                if len(users_intersection) != 0:
                    # 计算听过i歌曲人数和j歌曲人数的并集
                    users_union = users_i.union(users_j)
                    #使用Jaccard系数计算i,j之间的相似度
                    cooccurence_matrix[j,i] = float(len(users_intersection)) / float(len(users_union))
                else:
                    cooccurence_matrix[j,i] = 0
        return cooccurence_matrix

    # 使用相似度矩阵进行topN推荐
    def generate_top_recommendations(self, user, cooccurence_matrix, all_songs, user_songs):
        print("Non zero values in cooccurence_matrix :%d" % np.count_nonzero(cooccurence_matrix))
        # 对每一首待推荐歌曲，计算其与用户听过的所有歌曲相似度的平均值
        user_sim_scores = cooccurence_matrix.sum(axis=0) / float(cooccurence_matrix.shape[0])
        user_sim_scores = np.array(user_sim_scores)[0].tolist()
        sort_index = sorted(((e, i) for i, e in enumerate(list(user_sim_scores))), reverse=True)
        columns = ['user_id', 'song', 'score', 'rank']
        df = pandas.DataFrame(columns=columns)

        # 推荐相似度最高的5首歌
        rank = 1
        for i in range(0, len(sort_index)):
            if ~np.isnan(sort_index[i][0]) and all_songs[sort_index[i][1]] not in user_songs and rank <= 5:
                df.loc[len(df)] = [user, all_songs[sort_index[i][1]], sort_index[i][0], rank]
                rank = rank + 1
        if df.shape[0] == 0:
            print("The current user has no songs for training the item similarity based recommendation model.")
            return -1
        else:
            return df

    # 创建基于项目的协同过滤推荐模型
    def create(self, train_data, user_id, item_id):
        self.train_data = train_data
        self.user_id = user_id
        self.item_id = item_id
    #进行推荐
    def recommend(self, user):
        user_songs = self.get_user_items(user)
        print("No. of unique songs for the user: %d" % len(user_songs))
        all_songs = self.get_all_items_train_data()
        print("no. of unique songs in the training set: %d" % len(all_songs))
        cooccurence_matrix = self.construct_cooccurence_matrix(user_songs, all_songs)
        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, user_songs)
        return df_recommendations
"""
 #构建相似度矩阵,考虑用户活跃度影响，进行矩阵归一化
    def construct_cooccurence_matrix(self, user_songs, all_songs):
        # 每首歌都找出听过的人
        user_songs_users = []
        for i in range(0, len(user_songs)):
            user_songs_users.append(self.get_item_users(user_songs[i]))
        # 矩阵大小： 用户听过的歌曲数×歌曲总数
        cooccurence_matrix = np.matrix(np.zeros(shape=(len(user_songs), len(all_songs))), float)
        # 计算用户歌曲和其他所有歌曲的相似度
        for i in range(0, len(all_songs)):
            #从所有歌中确定了某首歌
            songs_i_data = self.train_data[self.train_data[self.item_id] == all_songs[i]]    
            #找出了听过歌的用户
            users_i = set(songs_i_data[self.user_id].unique())                         
            for j in range(0, len(user_songs)):

               #听过j的人
                users_j = user_songs_users[j]   
               #听过i和j的人的交集
                users_intersection = users_i.intersection(users_j)
                if len(users_intersection) != 0:
                    for k in users_intersection:
                        user_k = self.get_user_items(k)
                        cooccurence_matrix[j, i] += 1/math.log(1 + len(user_k)*1.0)
                    cooccurence_matrix[j, i] = float(cooccurence_matrix[j, i]/math.sqrt(len(users_i)*len(users_j)))
                else:
                    cooccurence_matrix[j, i] = 0
        coo_max = cooccurence_matrix.max(axis=1)
        cooccurence_matrix = cooccurence_matrix/coo_max
        #print(cooccurence_matrix)

        return cooccurence_matrix
"""
#!/usr/bin/python
# -*- coding: utf-8 -*-

import joblib
import numpy as np
import pandas as pd
import math
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#读取数据
game2idx = joblib.load('./Save_data/game2idx.pkl')
idx2game = joblib.load('./Save_data/idx2game.pkl')
rec = joblib.load('./Save_data/rec.pkl')
hours = joblib.load('./Save_data/hours.pkl')
buy = joblib.load('./Save_data/buy.pkl')
users = joblib.load('./Save_data/buyers.pkl')
#游戏名称列表
gamelist = list(game2idx)
#游戏数
n_game = len(gamelist)
#传入字典
gamedict = {1:"NULL",2:"NULL",3:"NULL",4:"NULL",5:"NULL"}
timedict = {1:"NULL",2:"NULL",3:"NULL",4:"NULL",5:"NULL"}
idxdict = {1:"NULL",2:"NULL",3:"NULL",4:"NULL",5:"NULL"}
#下面两个是要传递的
usertime=[]
useridx=[]
#下面的是返回的推荐游戏
recgame=[]
#相似度推荐
def UserSimilarity(games, game_hours):
    similarity = np.zeros(len(users)) # 用户相似度矩阵
    for i in range(len(users)):
        # 计算用户输入的游戏与数据集中每个用户购买游戏的重合度
        coincidence = 0 # 重合度
        positions = [] # 重合游戏在games中的位置
        for ii in range(len(games)):
            if games[ii] in np.where(buy[users[i], :] == 1)[0]:
                coincidence += 1
                positions.append(ii)
        if coincidence == 0:
            continue
        simi = []
        for position in positions:
            game = games[position]
            hour = abs(game_hours[position] - hours[users[i], game])
            simi.append(math.exp(-hour))
        similarity[i] = sum(simi) / coincidence
    # 相似度与玩家-游戏矩阵每一行相乘
    for i in range(len(users)):
        user = users[i]
        rec[user] = rec[user] * similarity[i]
        
    new_rec = np.zeros(len(rec[0])) # 1*n_games矩阵
    for i in range(len(new_rec)):
        for user in users:
            new_rec[i] += rec[user][int(i)]
    return new_rec
class Recommandation(QWidget):
    #初始化
    def __init__(self):
        super().__init__()
        self.initUI()
    #初始化布局
    def initUI(self):
        #设置界面的初始位置和界面的初始大小
        self.setGeometry(600,200,450,550)
        #窗口名
        self.setWindowTitle('steam游戏推荐')
        
        #设置组件，以下为标签
        self.lb1 = QLabel('请输入游戏名：',self)
        #这是所在位置
        self.lb1.move(20,20)
        self.lb2 = QLabel('请输入游戏名：',self)
        self.lb2.move(20,80)
        self.lb3 = QLabel('请输入游戏名：',self)
        self.lb3.move(20,140)
        self.lb4 = QLabel('请输入游戏名：',self)
        self.lb4.move(20,200)
        self.lb5 = QLabel('请输入游戏名：',self)
        self.lb5.move(20,260)
        
        #以下为下拉输入框的创建
        self.combobox1 = QComboBox(self, minimumWidth=200)
        self.combobox1.move(100,20)
        self.combobox1.setEditable(True)
        
        self.combobox2 = QComboBox(self, minimumWidth=200)
        self.combobox2.move(100,80)
        self.combobox2.setEditable(True)
        
        self.combobox3 = QComboBox(self, minimumWidth=200)
        self.combobox3.move(100,140)
        self.combobox3.setEditable(True)
        
        self.combobox4 = QComboBox(self, minimumWidth=200)
        self.combobox4.move(100,200)
        self.combobox4.setEditable(True)
        
        self.combobox5 = QComboBox(self, minimumWidth=200)
        self.combobox5.move(100,260)
        self.combobox5.setEditable(True)
        
        #以下为输入的按键设置
        self.bt1 = QPushButton('请输入游戏时间',self)
        self.bt1.move(330,20)
        self.bt2 = QPushButton('请输入游戏时间',self)
        self.bt2.move(330,80)
        self.bt3 = QPushButton('请输入游戏时间',self)
        self.bt3.move(330,140)
        self.bt4 = QPushButton('请输入游戏时间',self)
        self.bt4.move(330,200)
        self.bt5 = QPushButton('请输入游戏时间',self)
        self.bt5.move(330,260)
        
        
        #推荐按钮
        self.bt=QPushButton('推荐开始',self)
        self.bt.move(20,400)
        
        #初始化下拉输入框
        self.init_combobox()
        
        #连接按键与槽
        self.bt1.clicked.connect(self.timeDialog)
        self.bt2.clicked.connect(self.timeDialog)
        self.bt3.clicked.connect(self.timeDialog)
        self.bt4.clicked.connect(self.timeDialog)
        self.bt5.clicked.connect(self.timeDialog)
        #连接推荐
        self.bt.clicked.connect(self.recommand)
        
        
     #初始化下拉输入框   
    def init_combobox(self):
        # 增加选项元素
        for i in range(len(gamelist)):
            self.combobox1.addItem(gamelist[i])
            self.combobox2.addItem(gamelist[i])
            self.combobox3.addItem(gamelist[i])
            self.combobox4.addItem(gamelist[i])
            self.combobox5.addItem(gamelist[i])
        self.combobox1.setCurrentIndex(-1)
        self.combobox2.setCurrentIndex(-1)
        self.combobox3.setCurrentIndex(-1)
        self.combobox4.setCurrentIndex(-1)
        self.combobox5.setCurrentIndex(-1)
        # 增加自动补全
        self.completer = QCompleter(gamelist)
        #补全方式
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.combobox1.setCompleter(self.completer)
        self.combobox2.setCompleter(self.completer)
        self.combobox3.setCompleter(self.completer)
        self.combobox4.setCompleter(self.completer)
        self.combobox5.setCompleter(self.completer)
        
        
    def timeDialog(self):
        #获取信号
        sender = self.sender()
        if sender == self.bt1:
                #获取下拉输入框1输入的游戏名
                gamename = self.combobox1.currentText()
                #通过字典game2idx来查询刚刚获得的游戏名所对应的序列号
                gameid = game2idx.get(gamename)
                #没有序列号的情况，可以理解为没有输入正确的游戏名，或者输入为空，
                if gameid == None:
                    #这种情况下生成一个MessageBox来报错
                    reply = QMessageBox.information(self,'Error','请输入正确的游戏名!', QMessageBox.Close)
                else:
                    #输入正确的情况，将游戏名字，游戏id，分别记录到一个字典里，方便保存与更改
                    gamedict[1] = gamename
                    idxdict[1] = gameid
                    #弹出一个文本输入框，要求输入对应游戏的游戏时长
                    text, ok = QInputDialog.getDouble(self, '游戏时间', '请输入游戏时间：', min = 0.1)
                    #如果输入正确，就将时长记录到一个字典中，方便保存与更改。
                    if ok:
                        timedict[1] = text
        elif sender == self.bt2:
                gamename = self.combobox2.currentText()
                gameid = game2idx.get(gamename)
                if gameid == None:
                    reply = QMessageBox.information(self,'Error','请输入正确的游戏名!', QMessageBox.Close)
                else:
                    gamedict[2] = gamename
                    idxdict[2] = gameid
                    text, ok = QInputDialog.getDouble(self, '游戏时间', '请输入游戏时间：', min = 0.1)
                    if ok:
                        timedict[2] = text
        elif sender == self.bt3:
                gamename = self.combobox3.currentText()
                gameid = game2idx.get(gamename)
                if gameid == None:
                    reply = QMessageBox.information(self,'Error','请输入正确的游戏名!', QMessageBox.Close)
                else:
                    gamedict[3] = gamename
                    idxdict[3] = gameid
                    text, ok = QInputDialog.getDouble(self, '游戏时间', '请输入游戏时间：', min = 0.1)
                    if ok:
                        timedict[3] = text
        elif sender == self.bt4:
                gamename = self.combobox4.currentText()
                gameid = game2idx.get(gamename)
                if gameid == None:
                    reply = QMessageBox.information(self,'Error','请输入正确的游戏名!', QMessageBox.Close)
                else:
                    gamedict[4] = gamename
                    idxdict[4] = gameid
                    text, ok = QInputDialog.getDouble(self, '游戏时间', '请输入游戏时间：', min = 0.1)
                    if ok:
                        timedict[4] = text
        elif sender == self.bt5:
                gamename = self.combobox5.currentText()
                gameid = game2idx.get(gamename)
                if gameid == None:
                    reply = QMessageBox.information(self,'Error','请输入正确的游戏名!', QMessageBox.Close)
                else:
                    gamedict[5] = gamename
                    idxdict[5] = gameid
                    text, ok = QInputDialog.getDouble(self, '游戏时间', '请输入游戏时间：', min = 0.1)
                    if ok:
                        timedict[5] = text
                        
    def recommand(self):
        #验证是否存在没有写入的数据
        c = 0
        for i in range(1,6):
            if gamedict[i] == "NULL":
                c+=1
            if idxdict[i] == "NULL":
                c+=1
            if timedict[i] == "NULL":
                c+=1
        #全部写完的情况
        if c == 0:
            #将字典转化为列表
            usertime = list(timedict.values())
            useridx = list(idxdict.values())
            #调用模型
            allrecidx = UserSimilarity(useridx,usertime)
            #降序排列数据
            rr = np.argsort(-allrecidx)
            #获取排行前五的游戏id
            top_k = rr[:5]
            #将id对应的游戏名字输入数组
            for i in top_k:
                recgame.append(idx2game[i])
            #将数组转化为字符串并输出
            reclist = ','.join(recgame)
            reply = QMessageBox.information(self,'推荐的游戏','给您推荐的游戏是'+reclist, QMessageBox.Close)
        #存在没有写完的数据，要求重新写入。
        else:
            reply = QMessageBox.information(self,'Error','请输入全部数据!', QMessageBox.Close)

#主函数
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Recommandation()
    w.show()
    sys.exit(app.exec_())
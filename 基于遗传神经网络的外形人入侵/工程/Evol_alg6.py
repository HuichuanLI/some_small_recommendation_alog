# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 16:21:44 2020

@author: 23826
"""

from __future__ import division, print_function
from collections import defaultdict

import numpy as np
import operator

from math import floor
from random import randint
from random import random
from random import sample
from random import uniform

class Plane():
    def __init__(self,settings,plane_image,wih=None, who=None):
        #游戏初始设定
        self.plane_image=plane_image
        self.rect=self.plane_image.get_rect() #四个返回值，x,y,width,height
        self.width=self.rect[2]
        self.height=self.rect[3]
        self.x=settings['Screen_Size'][0]/2-self.width/2
        self.y=settings['Screen_Size'][1]-self.height
        self.move_x=0
        self.speed=2
        self.alive=True
        #神经网络初始设置
        self.wih=wih
        self.who=who
        self.livetime=0
    def update(self):
        self.x+=self.move_x*self.speed
    #指定位置绘制飞船
    def draw(self,screen):
        screen.blit(self.plane_image,(self.x,self.y,self.width,self.height))
    #判定死亡
    def is_dead(self,enemys,settings):
        if(self.x<-self.width)or(self.x > settings['Screen_Size'][0]):
            return True
        for enemy in enemys:
            if self.collision(enemy):
                return True
        return False
    #判定撞击
    def collision(self,enemy):
        if not ((self.x>enemy.x+enemy.width)or(self.x+self.width<enemy.x)or(self.y>enemy.y+enemy.height)):
            return True
        else:
            return False
    #获取输入值
    def get_inputs_values(self,enemys,settings):
       inputs=[]
       for i in range(0,settings['inodes']):
           inputs.append(0.0)
       inputs[0]=self.x/settings['Screen_Size'][0]
       #inputs[1]=self.move_x
       index=1
       for enemy in enemys:
           inputs[index]=enemy.x/settings['Screen_Size'][0]
           index+=1
           inputs[index]=enemy.y/settings['Screen_Size'][1]
           index+=1
       if len(enemys)>0 and self.x<enemys[0].x:
           inputs[index]=-1.0
       else:
           inputs[index]=1.0
       self.inputs=inputs
       return inputs
            
    #神经网络正向运算
    def think(self):
        af = lambda x: np.tanh(x)               # 激活函数
        h1 = af(np.dot(self.wih, self.inputs))  # 隐藏层
        out = af(np.dot(self.who, h1))          # 输出层

        #返回输出
        self.nn_out = float(out)
        
       
def evolve(settings, planes_old,plane_image):

    elitism_num = int(floor(settings['elitism'] * settings['pop']))
    random_num=int(floor(settings['random_rate']*settings['pop']))
    new_pls = settings['pop'] - elitism_num-random_num
    

    #从父代中获取一些统计数据
    '''
    stats = defaultdict(int)
    for plane in planes_old:
        if plane.livetime > stats['BEST'] or stats['BEST'] == 0:
            stats['BEST'] = plane.livetime

        if plane.livetime < stats['WORST'] or stats['WORST'] == 0:
            stats['WORST'] = plane.livetime

        stats['SUM'] += plane.livetime
        stats['COUNT'] += 1

    stats['AVG'] = stats['SUM'] / stats['COUNT']
    '''

    #父代选择
    planes_sorted = sorted(planes_old, key=operator.attrgetter('livetime'), reverse=True)
    planes_new = []
    for i in range(0, elitism_num):
        planes_new.append(Plane(settings,plane_image=plane_image,wih=planes_sorted[i].wih, who=planes_sorted[i].who))

    
    #生成子代
    for w in range(0, new_pls):

        # 从父代候选人中随机选择两个
        canidates = range(0, elitism_num)
        random_index = sample(canidates, 2)
        pl_1 = planes_sorted[random_index[0]]
        pl_2 = planes_sorted[random_index[1]]

        #交叉
        crossover_weight = random()
        wih_new = (crossover_weight * pl_1.wih) + ((1 - crossover_weight) * pl_2.wih)
        who_new = (crossover_weight * pl_1.who) + ((1 - crossover_weight) * pl_2.who)
        #print(np.shape(who_new))

        # 变异
        mutate = random()
        #是否突变
        if mutate <= settings['mutate']:

            # 选择突变wih或who
            mat_pick = randint(0,1)

            # WIH突变
            if mat_pick == 0:
                index_row = randint(0,settings['hnodes']-1)
                index_col = randint(0,settings['inodes']-1)
                wih_new[index_row][index_col] = wih_new[index_row][index_col] * uniform(0.9, 1.1)
                #if wih_new[index_row][index_col] >  1: wih_new[index_row][index_col] = 1
                #if wih_new[index_row][index_col] < -1: wih_new[index_row][index_col] = -1

            # MUTATE: WHO WEIGHTS
            if mat_pick == 1:
                #index_row = randint(0,settings['onodes']-1)
                index_col = randint(0,settings['hnodes']-1)
                who_new[0][index_col] = who_new[0][index_col] * uniform(0.9, 1.1)
                #if who_new[0][index_col] >  1: who_new[0][index_col] = 1
                #if who_new[0][index_col] < -1: who_new[0][index_col] = -1

        planes_new.append(Plane(settings, plane_image=plane_image,wih=wih_new, who=who_new))
    #随机引入：
    for i in range(0,random_num):
        wih_init = np.random.uniform(-1, 1, (settings['hnodes'], settings['inodes']))     # mlp weights (input -> hidden)
        who_init = np.random.uniform(-1, 1, (settings['onodes'], settings['hnodes']))
        plane=Plane(settings,plane_image,wih_init,who_init)
        planes_new.append(plane)
    return planes_new
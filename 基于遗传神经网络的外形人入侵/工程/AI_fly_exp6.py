# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 16:21:08 2020

@author: 23826
"""
#生物环境遗传算法每代引入随机，每次重新开始时外星人下落位置固定，对照组为contrast
import pygame
import sys
from pygame.locals import *
import random
import numpy as np
from Evol_alg6 import evolve,Plane

#所有设置
settings={}
#游戏方面
settings['BackGround']=(230,230,230)
settings['Screen_Size']=(500,324)
settings['plane_image']='./images/plane.bmp'
settings['enemy_image']='./images/enemy.bmp'
settings['exit_image']='./images/返回按钮.png'
settings['max_enemys']=1
settings['FPS']=100
#遗传算法方面
settings['pop']=50
#神经网络方面
settings['inodes'] = 1+3*settings['max_enemys']#输入层神经元个数,一个敌人时为4
settings['hnodes'] = 4*settings['inodes']#隐藏层神经元个数
settings['onodes'] = 1#输出层神经元个数
settings['mutate'] = 0.5       # 突变率
settings['elitism']=0.2        # 选择占比  
settings['random_rate']=0.1     #随机引入占比     
class Enemy():
    def __init__(self,settings,enemy_image):
        self.enemy_image=enemy_image
        self.rect=self.enemy_image.get_rect()
        self.width=self.rect[2]
        self.height=self.rect[3]
        self.x=random.choice(range(0,int(settings['Screen_Size'][0]-self.width/2),71))
        #print(self.x)
        self.y=0
    def update(self):
        self.y+=6
    def draw(self,screen):
        screen.blit(self.enemy_image,(self.x,self.y,self.width,self.height))
    def is_out(self):
        return True if self.y>=settings['Screen_Size'][1] else False


class ExitEvent():
    def __init__(self,icon,position):
        self.image = pygame.image.load(icon).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topright = position

    def draw(self,screen):
        screen.blit(self.image,self.rect)
        


class Game():
    def __init__(self,settings):
        pygame.init()
        self.screen=pygame.display.set_mode(settings['Screen_Size'])
        self.clock=pygame.time.Clock()
        pygame.display.set_caption('实验组')
        #self.ai...
        self.generation=0
        self.exit_signal = False
        self.state = 1  #当前活跃状态，1为活跃，0为不活跃
        self.max_enemys=settings['max_enemys']
        self.plane_image=pygame.image.load(settings['plane_image']).convert_alpha()
        self.enemy_image=pygame.image.load(settings['enemy_image']).convert_alpha()
        self.exit_image = pygame.image.load(settings['exit_image']).convert_alpha()
        self.exit_width = self.exit_image.get_width()
        self.exit_height = self.exit_image.get_height()
        #self.plane_image=pygame.image.load(settings['plane_image']).convert()
        #self.enemy_image=pygame.image.load(settings['enemy_image']).convert()
    #产生第一代飞机
    def start(self,settings,new_planes=[]):
        self.score=0
        self.planes=new_planes
        self.enemys=[]
        #self.generate...
        for i in range(0,settings['pop']):
            #用随机数初始化神经网络权重
            if(self.generation==0):
                wih_init = np.random.uniform(-1, 1, (settings['hnodes'], settings['inodes']))     # mlp weights (input -> hidden)
                who_init = np.random.uniform(-1, 1, (settings['onodes'], settings['hnodes']))
                plane=Plane(settings,self.plane_image,wih_init,who_init)
                self.planes.append(plane)
        self.generation+=1
        #存活数
        self.alives=len(self.planes)
    #每一代飞机依靠其神经网络预测进行躲避
    def update(self,settings):
        ExitEvent(settings['exit_image'],(500,0)).draw(self.screen)
        #依据神经网络输出判断左移或右移
        for i in range(len(self.planes)):
            #只重新绘制存活的
            if self.planes[i].alive:
                self.planes[i].get_inputs_values(self.enemys,settings)
                self.planes[i].think()
                if self.planes[i].nn_out<=0:
                    self.planes[i].move_x = -1
                elif self.planes[i].nn_out>0:
                    self.planes[i].move_x = 1
                #更新飞机位置
                self.planes[i].update()
                self.planes[i].draw(self.screen)
                #更新存活情况
                if self.planes[i].is_dead(self.enemys,settings)==True:
                    self.planes[i].alive=False
                    #记录每条飞船存活时间
                    self.planes[i].livetime=self.score
                    self.alives-=1
                    if self.is_all_dead():
                        #使用遗传算法生成新一代飞机对象
                        next_planes=evolve(settings,self.planes,self.plane_image)
                        self.start(settings,next_planes)
        self.generate_enemys()
        for i in range(len(self.enemys)):
            self.enemys[i].update()
            self.enemys[i].draw(self.screen)
            if self.enemys[i].is_out():
                del self.enemys[i]
                break
        self.score+=1
        print('[INFO]:\nAlive:%s, Generation:%s, Score:%s' % (self.alives, self.generation, self.score))
        
    def run(self,settings,level):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.mouse_select(event,level)
            if self.state == 1:
                self.screen.fill(settings['BackGround'])
                self.update(settings)
                pygame.display.update()
                self.clock.tick(settings['FPS'])
    def generate_enemys(self):
        if len(self.enemys)<self.max_enemys:
            enemy=Enemy(settings,self.enemy_image)
            self.enemys.append(enemy)
    def is_all_dead(self):
        for plane in self.planes:
            if plane.alive:
                return False
        return True
    def mouse_select(self,button,level):
        #global self.exit_signal
        if button.type == MOUSEBUTTONDOWN:
            mouse_down_x, mouse_down_y = button.pos
            if settings['Screen_Size'][0] - self.exit_width < mouse_down_x < settings['Screen_Size'][0] \
               and 0 < mouse_down_y < self.exit_height:
                level = 0
                self.state = 0
                pygame.quit()
                sys.exit()
            else:
                level = 1
                self.state = 1
        if button.type == MOUSEBUTTONUP:
            pass
        return level
'''
game=Game(settings)
game.start(settings)
game.run(settings)
'''

import pygame
import random
from pygame.locals import *

import AI_fly_exp6
from AI_fly_exp6 import settings
game1 = AI_fly_exp6.Game(settings)


class MainWindow(pygame.sprite.Sprite):
    #开始选择页面
    mainpic = './images/背景2.png'
    syzpic = './images/实验组.png'
    position = ([180,140])

    def __init__(self,icon,position):
        super().__init__()
        self.image = pygame.image.load(icon).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = position

    def draw(self,screen):
        screen.blit(self.image,self.rect)
        
class ManageWindow:
    __screen_size = (500,324)
    screen = pygame.display.set_mode(__screen_size, DOUBLEBUF, 32)
    syz_image = pygame.image.load(MainWindow.syzpic).convert_alpha()
    syzpic_width = syz_image.get_width()
    syzpic_height = syz_image.get_height()

    def drawWindow(self):
        MainWindow(MainWindow.mainpic,(0,324)).draw(self.screen)
        MainWindow(MainWindow.syzpic,MainWindow.position).draw(self.screen)
        #MainWindow(MainWindow.dzzpic,MainWindow.position[1]).draw(self.screen)
        #MainWindow(MainWindow.resultpic,MainWindow.position[2]).draw(self.screen)

    def mouse_select(self,button,level):
        if button.type == MOUSEBUTTONDOWN:
            mouse_down_x, mouse_down_y = button.pos
            print(button.pos)
            if level == 0:
                if MainWindow.position[0] < mouse_down_x < MainWindow.position[0] + self.syzpic_width \
                                and MainWindow.position[1] - self.syzpic_height< mouse_down_y < MainWindow.position[1]:
                                    level = 1
        if button.type == MOUSEBUTTONUP:
            pass
        return level
'''
class Manager:
    level = 0
    def change(self,button):
        if game1.mouse_select(button):
            pygame.quit()
            self.level = 0
        
 '''       
        
        
        
        
        
'''        
self.exit_width = self.exit_image.get_width()
        self.exit_height = self.exit_image.get_height()        
if self.mouse_select(event):
                    main.level = 0
if settings['Screen_Size'][0] - self.exit_width < mouse_down_x < settings['Screen_Size'][0] \
               and 0 < mouse_down_y < self.exit_height:
                self.exit_signal = True
            else:
                self.exit_signal = False
        if button.type == MOUSEBUTTONUP:
            pass
'''














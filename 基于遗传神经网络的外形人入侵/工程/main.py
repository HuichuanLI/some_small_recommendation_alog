import pygame
from pygame.locals import *
import sys
import mainwindow
from AI_fly_exp6 import settings,Game



syz = Game(settings)
pygame.init()
mwindow = mainwindow.ManageWindow()
global level
level = 0
while True:
    if level == 0:
        mwindow.drawWindow()
    elif level == 1:
        syz.start(settings)
        syz.run(settings,level)
    
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            pygame.quit()
            sys.exit()
        level = mwindow.mouse_select(event,level)
        level = syz.mouse_select(event,level)
        #m.change(event)
        
    pygame.display.flip()
    
    
if __name__ == "main":
    main()

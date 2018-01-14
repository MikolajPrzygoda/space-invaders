#!/usr/bin/env python3
import os
import sys
import pygame

#add game dir to the path for later importing 
sys.path.append(os.path.dirname(__file__))
from scripts.Game import Game

pygame.init()

game = Game()
game.loadScene("menu")
while game.isRunning:
    game.run()

pygame.quit()

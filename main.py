#!/usr/bin/env python3
import pygame
from scripts.Game import Game

pygame.init()

game = Game()
game.loadScene("menu")
while game.isRunning:
    game.run()

pygame.quit()

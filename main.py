#!/usr/bin/env python3
import pygame
from scripts.Game import Game

pygame.init()

game = Game()
game.load_scene("menu")
while game.is_running:
    game.run()

pygame.quit()

import pygame
from main import game


class Scene:
    def __init__(self):
        self.gameInstance = game

    def load(self):
        raise NotImplementedError()


class MainMenuScene(Scene):
    def __init__(self):
        super().__init__()

    def load(self):
        pass


class Level1Scene(Scene):
    def __init__(self):
        super().__init__()
        self.playerSprites = None
        self.gameObjects = None

    def load(self):
        self.playerSprites = pygame.image.load('assets/playerShips.png')
        self.gameObjects = {
            "player": [],
            "enemies": [],
            "projectiles": [],
            "powerups": []
        }


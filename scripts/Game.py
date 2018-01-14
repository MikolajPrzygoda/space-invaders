import pygame
from scripts.Scene import MainMenuScene, HelpScreenScene, GameplayScene, EndScreenScene, WinScreenScene, loadAsset


class Game:
    def __init__(self):
        pygame.display.set_caption("Space Invaders")
        self.backgroundColor = (0, 0, 0)
        self.width = 800
        self.height = 640
        self.fps = 60
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_icon(loadAsset("assets/icon.jpg"))
        self.clock = pygame.time.Clock()
        self.currentScene = None
        self.isRunning = True
        self.endScore = 0
        self.scenes = dict(
            menu=MainMenuScene(self),
            help=HelpScreenScene(self),
            gameplay=GameplayScene(self),
            endscreen=EndScreenScene(self),
            winscreen=WinScreenScene(self),
        )

    def run(self):
        self.screen.fill(self.backgroundColor)
        self.handleEvents()

        self.currentScene.tick()

        self.clock.tick(self.fps)
        pygame.display.flip()

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isRunning = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isRunning = False
                    break

            self.currentScene.handleEvent(event)

    def loadScene(self, sceneName: str):
        if self.currentScene:
            self.currentScene.unload()
        self.currentScene = self.scenes[sceneName]
        self.currentScene.load()

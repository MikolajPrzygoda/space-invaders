import pygame
from scripts.Scene import MainMenuScene, Level1Scene


class Game:
    def __init__(self):
        self.backgroundColor = (0, 0, 0)
        self.width = 800
        self.height = 640
        self.fps = 60
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.currentScene = None
        self.isRunning = True
        self.scenes = dict(
            mainMenu=MainMenuScene(self),
            # pauseMenu=PauseMenuScene(self),
            level1=Level1Scene(self)
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
            # ------------KeyDownEvents--------------
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isRunning = False
                    break
            # ---------------------------------------

            # -------------KeyUpEvents---------------
            elif event.type == pygame.KEYUP:
                pass
            # ---------------------------------------

            game.currentScene.handleEvent(event)

    def setCurrentScene(self, sceneName: str):
        if self.currentScene:
            self.currentScene.unload()
        self.currentScene = self.scenes[sceneName]
        self.currentScene.load()


pygame.init()

game = Game()
# game.setCurrentScene("level1")
game.setCurrentScene("mainMenu")
while game.isRunning:
    game.run()

pygame.quit()

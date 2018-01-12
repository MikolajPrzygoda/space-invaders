import pygame

from scripts.GameObjectClasses import Player, Enemy
from scripts.Scene import *


class Game:
    backgroundColor = (0, 0, 0)
    width = 800
    height = 640
    fps = 120
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    isRunning = True

    def run(self):
        #-------------Events--------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isRunning = False

            #------------KeyDownEvents--------------
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.gameObjects["player"][0].toggleIsShooting()
                elif event.key == pygame.K_ESCAPE:
                    self.isRunning = False
            #---------------------------------------

            #-------------KeyUpEvents---------------
            elif event.type == pygame.KEYUP:
                pass
            #---------------------------------------
        #---------------------------------
        self.clock.tick(self.fps)
        self.screen.fill(self.backgroundColor)

        # # remove offscreen projectiles
        # for i in range(len(self.gameObjects["projectiles"])):
        #     if self.gameObjects["projectiles"][i].y < -self.gameObjects["projectiles"][i].height:
        #         self.gameObjects["projectiles"].pop(i)
        #         break  #
        #
        # # call essential methods on every game object
        # for gameObject in self.gameObjects["player"] + \
        #                   self.gameObjects["enemies"] + \
        #                   self.gameObjects["projectiles"] + \
        #                   self.gameObjects["powerups"]:
        #
        #     gameObject.update()
        #     gameObject.handleInput()
        #     gameObject.draw()

        pygame.display.flip()

    # def createPlayer(self):
    #     if len(self.gameObjects["player"]) > 0:
    #         raise RuntimeError("Called createPlayer() for the second time.")
    #     self.gameObjects["player"].append(Player(self))


pygame.init()
game = Game()
scenes = dict(
    mainMenu=MainMenuScene(),
    # pauseMenu=PauseMenuScene(),
    # level1=Level1Scene()
)
# game.createPlayer()
# game.gameObjects["enemies"].append(Enemy(game, (400, 10)))
while game.isRunning:
    game.run()

pygame.quit()

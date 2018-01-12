import pygame
from scripts.GameObjectClasses import Player, Enemy


class Scene:
    def __init__(self, gameInstance):
        self.gameInstance = gameInstance

    def load(self):
        raise NotImplementedError()

    def unload(self):
        raise NotImplementedError()

    def handleEvent(self, event):
        raise NotImplementedError()

    def tick(self):
        raise NotImplementedError()


class MainMenuScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)

    def load(self):
        pass

    def unload(self):
        pass

    def handleEvent(self, event):
        pass

    def tick(self):
        pass


class Level1Scene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.playerSprites = None
        self.gameObjects = None
        self.images = None

    def load(self):
        self.gameObjects = {
            "player": None,
            "enemies": [],
            "playerProjectiles": [],
            "enemyProjectiles": [],
            "powerups": []
        }
        self.images = {
            "player": pygame.image.load("assets/playerShips.png").convert_alpha(),
            "enemy": pygame.image.load("assets/alienShip2.png").convert_alpha(),
            "projectile": pygame.image.load("assets/projectile.png").convert_alpha()
        }
        pygame.display.get_surface().blit(self.images["player"], (0, 0))
        self.gameObjects["player"] = Player(self.gameInstance, self.images["player"])
        self.gameObjects["enemies"].append(Enemy(self.gameInstance, self.images["enemy"], 300, 0))

    def unload(self):
        pass

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.gameObjects["player"].isShooting = not self.gameObjects["player"].isShooting
            elif event.key == pygame.K_ESCAPE:
                self.gameInstance.isRunning = False

        elif event.type == pygame.KEYUP:
            pass

    def tick(self):
        # remove offscreen projectiles
        print(len(self.gameObjects["playerProjectiles"]))
        for i in range(len(self.gameObjects["playerProjectiles"])):
            if self.gameObjects["playerProjectiles"][i].rect.y < -self.gameObjects["playerProjectiles"][i].height:
                del self.gameObjects["playerProjectiles"][i]
                break

        # call essential methods on every game object
        for gameObject in [self.gameObjects["player"]] + \
                self.gameObjects["enemies"] + \
                self.gameObjects["playerProjectiles"] + \
                self.gameObjects["powerups"]:
            gameObject.update()
            gameObject.handleInput()
            gameObject.draw()

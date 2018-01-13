import gc
import pygame

from scripts.GameplayObjectClasses import Player, Enemy, Powerup
from scripts.Menu import Menu


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
        self.menu = None

    def load(self):
        self.menu = Menu(self.gameInstance, "Space Invaders")
        self.menu.addItem("Play", "gameplay")
        self.menu.addItem("Help", "help")
        self.menu.addItem("Quit", "quit")

    def unload(self):
        self.menu = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.menu.setNextAsActive()
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                self.menu.setPreviousAsActive()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.menu.activate()

    def tick(self):
        self.menu.draw()


class HelpScreenScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.labels = None
        self.font = None
        self.textColor = None
        self.bgrColor = None

    def load(self):
        self.labels = list()
        self.font = pygame.font.SysFont("monospace", 20)
        self.textColor = (255, 255, 255)
        self.bgrColor = (0, 0, 0)
        self.labels.append(Menu.Item("Sterowanie statkiem: w/s/a/d", "", self.font))
        self.labels.append(Menu.Item("Przelaczanie strzelania: spacja", "", self.font))
        self.labels.append(Menu.Item("Wybor opcji menu: spacja / enter", "", self.font))
        self.labels.append(Menu.Item("Nacisnij 'q' aby powrocic do menu glownego", "", self.font))

    def unload(self):
        self.labels = None
        self.font = None
        self.textColor = None
        self.bgrColor = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.gameInstance.loadScene("menu")

    def tick(self):
        screenPadding = 40
        itemBottomPadding = 20
        x, y = screenPadding, screenPadding
        for label in self.labels:
            surf = label.getSurface()
            self.gameInstance.screen.blit(surf, (x, y))
            y += surf.get_rect().height + itemBottomPadding


class GameplayScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.playerSprites = None
        self.gameObjects = None
        self.powerups = None
        self.images = None
        self.font = None
        self.scoreLabel = None
        self.score = 0

        self.isActive = None

    def load(self):
        self.isActive = True
        self.gameObjects = {
            "player": None,
            "enemies": [],
            "playerProjectiles": [],
            "enemyProjectiles": [],
            "powerups": [],
            "blocks": []
        }
        self.images = {
            "player":       pygame.image.load("assets/playerShips.png").convert_alpha(),
            "enemy":        pygame.image.load("assets/alienShip2.png").convert_alpha(),
            "enemySpecial": pygame.image.load("assets/alienShip3.png").convert_alpha(),
            "projectile":   pygame.image.load("assets/projectile.png").convert_alpha(),
            "powerup":      pygame.image.load("assets/powerup.png").convert_alpha(),
            "block":        pygame.Surface((100, 30)).fill((255, 255, 255))
        }
        self.powerups = [
            Powerup(self.gameInstance, self.images["powerup"])
        ]
        # test enemy objects
        self.gameObjects["enemies"].append(Enemy(self.gameInstance, self.images["enemy"], (300, 0), 2))
        self.gameObjects["enemies"].append(Enemy(self.gameInstance, self.images["enemySpecial"], (200, 0), 4, self.powerups[0]))

        self.gameObjects["player"] = Player(self.gameInstance, self.images["player"])
        self.font = pygame.font.SysFont("monospace", 20)
        self.scoreLabel = self.font.render("Score: ", 1, (255, 255, 255))

    def unload(self):
        self.isActive = False
        self.playerSprites = None
        self.gameObjects = None
        self.images = None
        self.font = None
        self.scoreLabel = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.gameObjects["player"].isShooting = not self.gameObjects["player"].isShooting
            elif event.key == pygame.K_ESCAPE:
                self.gameInstance.isRunning = False

        elif event.type == pygame.KEYUP:
            pass

    def tick(self):
        # call essential methods on every game object
        for gameObject in [self.gameObjects["player"]] + \
                self.gameObjects["enemies"] + \
                self.gameObjects["playerProjectiles"] + \
                self.gameObjects["powerups"]:
            gameObject.draw()
            gameObject.update()
            gameObject.handleInput()

        # drawing score
        # quick solution for the following code trying to draw score after scene was unloaded
        # TODO: do something less hacky to fix this
        if not self.isActive:
            return
        self.gameInstance.screen.blit(self.scoreLabel, (30, 30))
        numberLabel = self.font.render(str(self.score), 1, (255, 255, 255))
        self.gameInstance.screen.blit(numberLabel, (30 + self.scoreLabel.get_rect().width, 30))


class EndScreenScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.label = None
        self.font = None

    def load(self):
        self.font = pygame.font.SysFont("monospace", 34)
        self.label = self.font.render("Koniec gry, Twoj wynik to: ", 1, (255, 255, 255))

    def unload(self):
        self.font = None
        self.label = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            self.gameInstance.loadScene("menu")

    def tick(self):
        numberLabel = self.font.render(str(self.gameInstance.endScore), 1, (255, 255, 255))

        x = (self.gameInstance.width - self.label.get_rect().width) / 2
        y = (self.gameInstance.height - self.label.get_rect().height) / 2

        self.gameInstance.screen.blit(self.label, (x, y))
        self.gameInstance.screen.blit(numberLabel, (x + self.label.get_rect().width, y))

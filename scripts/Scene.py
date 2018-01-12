import pygame
from scripts.GameObjectClasses import Player, Enemy
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
        self.menu.addItem("Play", "level1")
        self.menu.addItem("Help", "help")
        self.menu.addItem("Quit", "quit")

    def unload(self):
        self.menu = None

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
        self.labels.append(Menu.Item("Nacisnij 'q' aby wrocic z tego ekranu", "", self.font))

    def unload(self):
        self.labels = None
        self.font = None
        self.textColor = None
        self.bgrColor = None

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.gameInstance.setCurrentScene("menu")

    def tick(self):
        screenPadding = 40
        itemBottomPadding = 20
        x, y = screenPadding, screenPadding
        for label in self.labels:
            surf = label.getSurface()
            self.gameInstance.screen.blit(surf, (x, y))
            y += surf.get_rect().height + itemBottomPadding

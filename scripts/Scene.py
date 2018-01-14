import os
import sys
import gc
import pygame

from scripts.Menu import Menu
from scripts.Levels import *


def loadAsset(relativePath: str, noAlpha=False) -> pygame.Surface:
    """ Get an asset, works for development and for packaged one-file exutable"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    absPath = os.path.join(base_path, relativePath)
    if noAlpha:
        return pygame.image.load(absPath).convert()
    else:
        return pygame.image.load(absPath).convert_alpha()


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
        self.menu.addItem("Graj", "gameplay")
        self.menu.addItem("Pomoc", "help")
        self.menu.addItem("Wyjdź", "quit")

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
        self.font = None
        self.textColor = None
        self.tipSurfaces = None
        self.powerupSurfaces = None
        self.powerupDescrtiptionsSurfaces = None

    def load(self):
        self.font = pygame.font.SysFont("monospace", 16)
        self.textColor = (255, 255, 255)
        self.tipSurfaces = [
            self.font.render("Sterowanie statkiem: w/s/a/d", 1, self.textColor),
            self.font.render("Przełączanie strzelania: spacja", 1, self.textColor),
            self.font.render("Wybór opcji menu: spacja / enter", 1, self.textColor),
            self.font.render("W każdej chwili działania gry możesz ja zamknąć za pomocą 'escape'", 1, self.textColor),
            self.font.render("Naciśnij 'q' aby powrócić do menu głównego", 1, self.textColor),
        ]
        self.powerupDescrtiptionsSurfaces = [
            self.font.render("Speed - zwiększa prędkość maksymalną i przyśpieszenie statku", 1, self.textColor),
            self.font.render("Power - zwieksza szybkostrzelność, prędkość pocisków i ich obrażenia", 1, self.textColor),
            self.font.render("Passthrough Bullets - twoje pociski przenikają przez przeciwników", 1, self.textColor),
            self.font.render("Invincibiliy - zapewnia nietykalność na krótki czas", 1, self.textColor),
        ]
        self.powerupSurfaces = [
            loadAsset("assets/powerup_power.png"),
            loadAsset("assets/powerup_speed.png"),
            loadAsset("assets/powerup_ghostBullets.png"),
            loadAsset("assets/powerup_invincibility.png")
        ]

    def unload(self):
        self.tipSurfaces = None
        self.font = None
        self.textColor = None
        self.powerupSurfaces = None
        self.powerupDescrtiptionsSurfaces = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.gameInstance.loadScene("menu")

    def tick(self):
        screenPadding = 40
        itemBottomPadding = 20
        x, y = screenPadding, screenPadding

        # print general tips list
        for label in self.tipSurfaces:
            self.gameInstance.screen.blit(label, (x, y))
            y += label.get_rect().height + itemBottomPadding

        y += 40 # additional padding above powerups list

        # print list with icons and descriptions of ingame powerups
        for i in range(len(self.powerupSurfaces)):
            powerupSurface = self.powerupSurfaces[i]
            powerupDescriptionSurface = self.powerupDescrtiptionsSurfaces[i]

            self.gameInstance.screen.blit(powerupSurface, (x, y + 5))
            self.gameInstance.screen.blit(powerupDescriptionSurface, (x + powerupSurface.get_rect().width + 5, y))
            y += powerupDescriptionSurface.get_rect().height + itemBottomPadding


class GameplayScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.gameObjects = None
        self.images = None
        self.font = None
        self.scoreLabel = None
        self.score = None

        self.isActive = None
        self.currentLevel = None

    def load(self):
        self.isActive = True
        self.currentLevel = 1
        self.images = {
            "player":                   loadAsset("assets/playerShip.png"),
            "enemy":                    loadAsset("assets/alienShip.png"),
            "enemy2":                   loadAsset("assets/alienShip2.png"),
            "enemy3":                   loadAsset("assets/alienShip3.png"),
            "enemySpecial":             loadAsset("assets/alienShipSpecial.png"),
            "boss":                     loadAsset("assets/bossShip.png"),
            "projectile":               loadAsset("assets/projectile.png"),
            "enemyProjectile":          loadAsset("assets/enemyProjectile.png"),
            "enemyProjectile_directed": loadAsset("assets/enemyProjectile_directed.png"),
            "enemyProjectile_spread":   loadAsset("assets/enemyProjectile_spread.png"),
            "powerup_power":            loadAsset("assets/powerup_power.png"),
            "powerup_speed":            loadAsset("assets/powerup_speed.png"),
            "powerup_ghostBullets":     loadAsset("assets/powerup_ghostBullets.png"),
            "powerup_invincibility":    loadAsset("assets/powerup_invincibility.png"),
            "playerShield":             loadAsset("assets/shield.png", noAlpha=True) #no per pixel alpha in that one
        }
        self.gameObjects = Level1().load(self.gameInstance, self.images)
        self.score = 0
        self.font = pygame.font.SysFont("monospace", 20)
        self.scoreLabel = self.font.render("Score: ", 1, (255, 255, 255))

    def unload(self):
        self.isActive = False
        self.gameObjects = None
        self.images = None
        self.score = None
        self.font = None
        self.scoreLabel = None
        self.currentLevel = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.gameObjects["player"].isShooting = not self.gameObjects["player"].isShooting
            elif event.key == pygame.K_ESCAPE:
                self.gameInstance.isRunning = False

        elif event.type == pygame.KEYUP:
            pass

    # noinspection PyArgumentList
    def tick(self):
        # call essential methods on every game object
        for gameObject in [self.gameObjects["player"]] + \
                self.gameObjects["enemies"] + \
                self.gameObjects["playerProjectiles"] + \
                self.gameObjects["bossProjectiles"] + \
                self.gameObjects["powerups"]:
            gameObject.draw()
            gameObject.update()
            gameObject.handleInput()

        if not self.isActive:
            return

        # --- drawing ui ---
        x = 20
        y = 20
        itemBottomPadding = 10
        durationBarWidth = 100
        bossHpBarWidth = 300
        bossHpBarHeight = 10

        # Score label
        self.gameInstance.screen.blit(self.scoreLabel, (x, y))
        numberLabel = self.font.render(str(self.score), 1, (255, 255, 255))
        self.gameInstance.screen.blit(numberLabel, (x + self.scoreLabel.get_rect().width, y))
        y += numberLabel.get_rect().height + itemBottomPadding

        # Active powerups list
        for powerup in self.gameObjects["player"].activePowerups:
            # draw icon
            icon = self.images[powerup.type.value]
            self.gameInstance.screen.blit(icon, (x, y))
            # draw duration bar
            surface = pygame.Surface((durationBarWidth, icon.get_rect().height)).convert_alpha()
            surface.fill((255, 255, 255, 255))
            percentLeft = powerup.duration / powerup.startDuration
            surface.fill((0, 0, 0, 0), pygame.Rect(1, 1, durationBarWidth*percentLeft-2, icon.get_rect().height-2))
            self.gameInstance.screen.blit(surface, (x + icon.get_rect().width + 10, y))

            y += icon.get_rect().height + itemBottomPadding

        # Boss hp bar if on 5th level
        if self.currentLevel == 5:
            hpPrercent = self.gameObjects["boss"].healthPoints / self.gameObjects["boss"].maxHp

            # no idea why, sometimes hue was value not in [0, 360]
            hue = 120 * hpPrercent
            hue = min(max(0, hue), 120)

            bossHpBarColor = pygame.Color("black")
            bossHpBarColor.hsla = (hue, 100, 50, 100)
            surface = pygame.Surface((bossHpBarWidth, bossHpBarHeight)).convert_alpha()
            surface.fill(bossHpBarColor)
            surface.fill(pygame.Color("black"), pygame.Rect(1, 1, bossHpBarWidth - 2, bossHpBarHeight - 2))
            x = (self.gameInstance.width - surface.get_rect().width) / 2
            surface.fill(bossHpBarColor, pygame.Rect(1, 1, bossHpBarWidth*hpPrercent - 2, bossHpBarHeight - 2))
            self.gameInstance.screen.blit(surface, (x, 10))

    def nextLevel(self):
        if self.currentLevel == 1:
            self.score += 10000
            self.gameObjects = Level2().load(self.gameInstance, self.images)
        elif self.currentLevel == 2:
            self.score += 20000
            self.gameObjects = Level3().load(self.gameInstance, self.images)
        elif self.currentLevel == 3:
            self.score += 30000
            self.gameObjects = Level4().load(self.gameInstance, self.images)
        elif self.currentLevel == 4:
            self.score += 40000
            self.gameObjects = Level5().load(self.gameInstance, self.images)
        elif self.currentLevel == 5:
            self.score += 100000
            self.gameInstance.endScore = self.score
            self.gameInstance.loadScene("winscreen")
            return

        self.currentLevel += 1

    def checkForEnd(self):
        if len(self.gameObjects["enemies"]) == 0:
            self.nextLevel()


class EndScreenScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.label = None
        self.labelTip1 = None
        self.labelTip2 = None
        self.font = None

    def load(self):
        self.font = pygame.font.SysFont("monospace", 16)
        self.labelTip1 = self.font.render("Nacisnij 'q' aby powrocic do menu glownego", 1, (255, 255, 255))
        self.labelTip2 = self.font.render("Nacisnij 'r' aby zagrac ponownie", 1, (255, 255, 255))
        self.font = pygame.font.SysFont("monospace", 34)
        self.label = self.font.render("Koniec gry, Twoj wynik to: ", 1, (255, 255, 255))

    def unload(self):
        self.font = None
        self.label = None
        self.labelTip1 = None
        self.labelTip2 = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.gameInstance.loadScene("menu")
            if event.key == pygame.K_r:
                self.gameInstance.loadScene("gameplay")

    def tick(self):
        numberLabel = self.font.render(str(self.gameInstance.endScore), 1, (255, 255, 255))

        x = (self.gameInstance.width - (self.label.get_rect().width + numberLabel.get_rect().width)) / 2
        y = (self.gameInstance.height - self.label.get_rect().height) / 2

        self.gameInstance.screen.blit(self.label, (x, y))
        self.gameInstance.screen.blit(numberLabel, (x + self.label.get_rect().width, y))

        x = (self.gameInstance.width - self.labelTip1.get_rect().width) / 2
        y += self.label.get_rect().height + 20
        self.gameInstance.screen.blit(self.labelTip1, (x, y))

        x = (self.gameInstance.width - self.labelTip2.get_rect().width) / 2
        y += self.labelTip1.get_rect().height + 20
        self.gameInstance.screen.blit(self.labelTip2, (x, y))


class WinScreenScene(Scene):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.label = None
        self.labelTip1 = None
        self.labelTip2 = None
        self.font = None

    def load(self):
        self.font = pygame.font.SysFont("monospace", 16)
        self.labelTip1 = self.font.render("Nacisnij 'q' aby powrocic do menu glownego", 1, (255, 255, 255))
        self.labelTip2 = self.font.render("Nacisnij 'r' aby zagrac ponownie", 1, (255, 255, 255))
        self.font = pygame.font.SysFont("monospace", 34)
        self.label = self.font.render("Wygrales, twoj wynik to: ", 1, (255, 255, 255))

    def unload(self):
        self.font = None
        self.label = None
        self.labelTip1 = None
        self.labelTip2 = None
        gc.collect()

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.gameInstance.loadScene("menu")
            if event.key == pygame.K_r:
                self.gameInstance.loadScene("gameplay")

    def tick(self):
        numberLabel = self.font.render(str(self.gameInstance.endScore), 1, (255, 255, 255))

        x = (self.gameInstance.width - (self.label.get_rect().width + numberLabel.get_rect().width)) / 2
        y = (self.gameInstance.height - self.label.get_rect().height) / 2

        self.gameInstance.screen.blit(self.label, (x, y))
        self.gameInstance.screen.blit(numberLabel, (x + self.label.get_rect().width, y))

        x = (self.gameInstance.width - self.labelTip1.get_rect().width) / 2
        y += self.label.get_rect().height + 20
        self.gameInstance.screen.blit(self.labelTip1, (x, y))

        x = (self.gameInstance.width - self.labelTip2.get_rect().width) / 2
        y += self.labelTip1.get_rect().height + 20
        self.gameInstance.screen.blit(self.labelTip2, (x, y))

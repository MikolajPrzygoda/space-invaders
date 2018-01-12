import pygame
from pygame import Surface


class GameObject:
    def __init__(self, gameInstance):
        self.gameInstance = gameInstance
        self.image = None
        self.rect = None

        #for smooth movement - used in moveFloat method
        self.dx = 0
        self.dy = 0

    def update(self):
        raise NotImplementedError

    def handleInput(self):
        raise NotImplementedError

    def draw(self):
        self.gameInstance.screen.blit(self.image, self.rect)

    def moveFloat(self, x: float, y: float):
        self.dx += x
        self.dy += y
        if abs(self.dx) > 1:
            self.rect.move_ip(int(self.dx), 0)
            self.dx -= int(self.dx)
        if abs(self.dy) > 1:
            self.rect.move_ip(0, int(self.dy))
            self.dy -= int(self.dy)


class Projectile(GameObject):

    def __init__(self, gameInstance, image: Surface, x: int, y: int, travelSpeed: int, damage: int):
        super().__init__(gameInstance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.size[0]
        self.height = self.rect.size[1]
        self.rect.move_ip(x - self.width/2, y)
        self.travelSpeed = travelSpeed
        self.damage = damage
        self.gameInstance.currentScene.gameObjects["playerProjectiles"].append(self)

    def update(self):
        self.moveFloat(0, -self.travelSpeed)

    def handleInput(self):
        pass


class Player(GameObject):
    def __init__(self, gameInstance, image: Surface):
        super().__init__(gameInstance)
        self.width = 60
        self.height = 65
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.image.blit(image, (0, 0), (145, 25, self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.move_ip((self.gameInstance.width - self.width)/2, self.gameInstance.height - self.height)

        self.maxSpeed = 8
        self.speedDumpingFactor = 0.92
        self.acceleration = 0.6
        self.currentSpeed = {
            "x": 0,
            "y": 0
        }
        self.minHeight = self.gameInstance.height - 300

        self.isShooting = False
        self.shootingSpeed = 20
        self.shootingCooldown = 0
        self.projectileSpeed = 12
        self.projectileDamage = 1

    def updateSpeed(self):
        self.currentSpeed["x"] *= self.speedDumpingFactor
        self.currentSpeed["y"] *= self.speedDumpingFactor

        if pygame.key.get_pressed()[pygame.K_a]:
            self.currentSpeed["x"] -= self.acceleration
        if pygame.key.get_pressed()[pygame.K_d]:
            self.currentSpeed["x"] += self.acceleration
        if pygame.key.get_pressed()[pygame.K_s]:
            self.currentSpeed["y"] += self.acceleration
        if pygame.key.get_pressed()[pygame.K_w]:
            self.currentSpeed["y"] -= self.acceleration

        if self.currentSpeed["x"] > self.maxSpeed:
            self.currentSpeed["x"] = self.maxSpeed
        elif self.currentSpeed["x"] < -self.maxSpeed:
            self.currentSpeed["x"] = -self.maxSpeed
        if self.currentSpeed["y"] > self.maxSpeed:
            self.currentSpeed["y"] = self.maxSpeed
        elif self.currentSpeed["y"] < -self.maxSpeed:
            self.currentSpeed["y"] = -self.maxSpeed

    def updatePosition(self):
        self.move(self.currentSpeed["x"], self.currentSpeed["y"])

    def move(self, x, y):
        self.moveFloat(x, y)

        if self.rect.x < 0:
            self.rect.x = 0
            self.currentSpeed["x"] = 0
        elif self.rect.x + self.width > self.gameInstance.width:
            self.rect.x = self.gameInstance.width - self.width
            self.currentSpeed["x"] = 0

        if self.rect.y + self.height < self.minHeight:
            self.rect.y = self.minHeight - self.height
            self.currentSpeed["y"] = 0

        elif self.rect.y + self.height > self.gameInstance.height:
            self.rect.y = self.gameInstance.height - self.height
            self.currentSpeed["y"] = 0

    def shoot(self):
        Projectile(self.gameInstance,
                   self.gameInstance.currentScene.images["projectile"],
                   self.rect.x + self.width/2, self.rect.y,
                   self.projectileSpeed,
                   self.projectileDamage
        )

    def handleInput(self):
        pass

    def update(self):
        self.updateSpeed()
        self.updatePosition()

        if self.shootingCooldown == 0:
            if self.isShooting:
                self.shoot()
                self.shootingCooldown = self.shootingSpeed
        else:
            if self.shootingCooldown > 0:
                self.shootingCooldown -= 1


class Enemy(GameObject):
    def __init__(self, gameInstance, image: Surface, x: int, y: int):
        super().__init__(gameInstance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(x, y)
        self.speed = {
            "x": 3,
            "y": 0
        }
        self.width = self.rect.width
        self.height = self.rect.width

    def update(self):
        self.rect.x += self.speed["x"]
        self.rect.y += self.speed["y"]

        if self.rect.x < 0 or self.rect.x + self.width > self.gameInstance.width:
            self.speed["x"] = -self.speed["x"]
            self.rect.y += self.height

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.width > self.gameInstance.width:
            self.rect.x = self.gameInstance.width - self.width

    def handleInput(self):
        pass

    # def damage(self):

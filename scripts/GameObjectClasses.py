import pygame


class GameObject:
    def __init__(self, gameInstance):
        self.gameInstance = gameInstance

    def update(self):
        raise NotImplementedError

    def handleInput(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError


class Projectile(GameObject):

    def __init__(self, gameInstance, x, y, travelSpeed, damage):
        super().__init__(gameInstance)
        self.image = pygame.image.load("assets/projectile.png").convert_alpha()
        self.width = self.image.get_rect().size[0]
        self.height = self.image.get_rect().size[1]
        self.x = x - self.width/2
        self.y = y # no "- self.height/2" to spawn projectile hidden behind the player image
        self.travelSpeed = travelSpeed
        self.damage = damage
        self.gameInstance.gameObjects["projectiles"].append(self)

    def update(self):
        self.y -= self.travelSpeed

    def draw(self):
        self.gameInstance.screen.blit(self.image, (self.x, self.y))

    def handleInput(self):
        pass

    # def __del__(self, gameInstance):
    #     gameInstance.gameObjects.remove(self)
    #     print("deleting projectile: ", self.projID)


class Player(GameObject):
    def __init__(self, gameInstance):
        super().__init__(gameInstance)
        self.width = 60
        self.height = 65
        self.playerSprites = self.gameInstance.playerSprites
        self.image = pygame.Surface((self.width, self.height))
        self.image.blit(self.playerSprites, (0, 0), (145, 25, self.width, self.height))

        self.maxSpeed = 6
        self.speedDumpingFactor = 0.92
        self.acceleration = 0.3
        self.currentSpeed = {
            "x": 0,
            "y": 0
        }
        self.position = {
            "x": (self.gameInstance.width - self.width)/2,
            "y": self.gameInstance.height - self.height
        }
        self.minHeight = self.gameInstance.height - 300

        self.isShooting = False
        self.shootingSpeed = 20
        self.shootingCooldown = 0
        self.projectileSpeed = 13
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
        self.position["x"] += x
        if self.position["x"] < 0:
            self.position["x"] = 0
            self.currentSpeed["x"] = 0
        elif self.position["x"] + self.width > self.gameInstance.width:
            self.position["x"] = self.gameInstance.width - self.width
            self.currentSpeed["x"] = 0

        self.position["y"] += y
        if self.position["y"] + self.height < self.minHeight:
            self.position["y"] = self.minHeight - self.height
            self.currentSpeed["y"] = 0

        elif self.position["y"] + self.height > self.gameInstance.height:
            self.position["y"] = self.gameInstance.height - self.height
            self.currentSpeed["y"] = 0

    def toggleIsShooting(self):
        self.isShooting = not self.isShooting

    def shoot(self):
        Projectile(self.gameInstance, self.position["x"]+self.width/2, self.position["y"],
                   self.projectileSpeed, self.projectileDamage)

    def handleInput(self):
        pass

    def update(self):
        self.updateSpeed()
        self.updatePosition()

        if self.isShooting and self.shootingCooldown == 0:
            self.shoot()
            self.shootingCooldown = self.shootingSpeed
        else:
            if self.shootingCooldown > 0:
                self.shootingCooldown -= 1

    def draw(self):
        self.gameInstance.screen.blit(self.image, (self.position["x"], self.position["y"]))


class Enemy(GameObject):
    def __init__(self, gameInstance, spawnCoords: (int, int)):
        super().__init__(gameInstance)
        self.image = pygame.image.load("assets/alienShip2.png").convert_alpha()
        self.position = {
            "x": spawnCoords[0],
            "y": spawnCoords[1]
        }
        self.speed = {
            "x": 3,
            "y": 0
        }
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.position["x"] += self.speed["x"]
        self.position["y"] += self.speed["y"]

        if self.position["x"] < 0 or self.position["x"] + self.width > self.gameInstance.width:
            self.speed["x"] = -self.speed["x"]
            self.position["y"] += self.height

        if self.position["x"] < 0:
            self.position["x"] = 0
        elif self.position["x"] + self.width > self.gameInstance.width:
            self.position["x"] = self.gameInstance.width - self.width

    def handleInput(self):
        pass

    def draw(self):
        self.gameInstance.screen.blit(self.image, (self.position["x"], self.position["y"]))

    # def damage(self):


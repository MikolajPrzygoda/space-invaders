import pygame

from enum import Enum
from math import sin, cos, sqrt, pi
from random import randint


class GameplayObject:
    def __init__(self, gameInstance):
        self.gameInstance = gameInstance
        self.sceneInstance = gameInstance.currentScene
        self.image = None
        self.rect = None

        # used in moveFloat method
        self.dx = 0
        self.dy = 0

    def update(self):
        raise NotImplementedError

    def handleInput(self):
        pass

    def draw(self):
        self.gameInstance.screen.blit(self.image, self.rect)

    # since rect stores (x,y) values as ints this helper function allows for gameObjects to be moved by
    # finer values storing exact change in position and moving object only by the intiger part
    def moveFloat(self, x: float, y: float):
        self.dx += x
        self.dy += y
        if abs(self.dx) > 1:
            self.rect.move_ip(int(self.dx), 0)
            self.dx -= int(self.dx)
        if abs(self.dy) > 1:
            self.rect.move_ip(0, int(self.dy))
            self.dy -= int(self.dy)

    def die(self):
        raise NotImplementedError


class PowerupType(Enum):
    POWER = "powerup_power"
    SPEED = "powerup_speed"
    GHOST_BULLETS = "powerup_ghostBullets"
    INVINCIBILITY = "powerup_invincibility"


class Powerup(GameplayObject):
    def __init__(self, gameInstance, image: pygame.Surface, powerupType: PowerupType):
        super().__init__(gameInstance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.player = None
        self.type = powerupType
        self.isPickedup = False

        if powerupType == PowerupType.POWER:
            self.startDuration = 300
        elif powerupType == PowerupType.SPEED:
            self.startDuration = 1000
        elif powerupType == PowerupType.GHOST_BULLETS:
            self.startDuration = 500
        elif powerupType == PowerupType.INVINCIBILITY:
            self.startDuration = 500
        self.duration = self.startDuration

    def update(self):
        if not self.sceneInstance.isActive:
            return

        if self.isPickedup:
            self.duration -= 1
            if self.duration == 0:
                self.onDurrEnd()
        else:
            self.rect.move_ip(0, 3)
            if self.rect.y > self.gameInstance.height:
                self.die()

    def onPickup(self):
        self.isPickedup = True
        self.player = self.sceneInstance.gameObjects["player"]
        self.player.activePowerups.append(self)
        if self.type == PowerupType.POWER:
            self.player.projectileDamage = 4
            self.player.projectileSpeed = 24
            self.player.shootingSpeed = 14

        elif self.type == PowerupType.SPEED:
            self.player.maxSpeed = 11
            self.player.speedDumpingFactor = 0.9
            self.player.acceleration = 1.5

        elif self.type == PowerupType.INVINCIBILITY:
            self.player.invincibility = True
            # ghost bullets handled in Projectile.update()

    def onDurrEnd(self):
        if self.type == PowerupType.POWER:
            self.player.projectileDamage = 1
            self.player.projectileSpeed = 12
            self.player.shootingSpeed = 20

        elif self.type == PowerupType.SPEED:
            self.player.maxSpeed = 8
            self.player.speedDumpingFactor = 0.92
            self.player.acceleration = 0.6

        elif self.type == PowerupType.INVINCIBILITY:
            self.player.invincibility = False
        # ghost bullets handled in Projectile.update()

        self.die(True)

    def die(self, lookInPlayer: bool = False):
        if lookInPlayer:
            powerups = self.player.activePowerups
        else:
            powerups = self.sceneInstance.gameObjects["powerups"]
        for i in range(len(powerups)):
            if self == powerups[i]:
                del powerups[i]
                break


class Projectile(GameplayObject):
    def __init__(self,
                 gameInstance,
                 image: pygame.Surface,
                 pos: (int, int),
                 travelSpeed: int,
                 damage: int):

        super().__init__(gameInstance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos[0] - self.rect.width / 2, pos[1])
        self.playerInstance = self.sceneInstance.gameObjects["player"]
        self.travelSpeed = travelSpeed
        self.damage = damage
        self.sceneInstance.gameObjects["playerProjectiles"].append(self)

        # needed when player gets 'ghostBullets' powerup
        self.enemiesAreadyHit = list()

    def update(self):
        if not self.sceneInstance.isActive:
            return

        self.moveFloat(0, -self.travelSpeed)

        # remove offscreen projectiles
        if self.rect.y < -self.rect.height:
            self.die()
            return

        # check for collision with enemy ships
        for enemy in self.sceneInstance.gameObjects["enemies"]:
            if self.rect.colliderect(enemy.rect) and enemy not in self.enemiesAreadyHit:
                enemy.damage(self.damage)
                self.enemiesAreadyHit.append(enemy)
                for powerup in self.playerInstance.activePowerups:
                    if powerup.type == PowerupType.GHOST_BULLETS:
                        # important: make sure that this collision detection code is the last piece
                        #            in the update funcion so the return below wont break anything.
                        return
                self.die()

    def die(self):
        if not self.sceneInstance.isActive:
            return
        playerProjectiles = self.sceneInstance.gameObjects["playerProjectiles"]
        for i in range(len(playerProjectiles)):
            if self == playerProjectiles[i]:
                del playerProjectiles[i]
                break


class BossProjectile(GameplayObject):
    def __init__(self,
                 gameInstance,
                 image: pygame.Surface,
                 pos: (int, int),
                 travelVector: (float, float),
                 travelSpeed: int):

        super().__init__(gameInstance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos[0] - self.rect.width / 2, pos[1])
        self.travelVector = travelVector
        self.travelSpeed = travelSpeed
        self.sceneInstance.gameObjects["bossProjectiles"].append(self)
        self.player = self.sceneInstance.gameObjects["player"]

    def update(self):
        if not self.sceneInstance.isActive:
            return

        self.moveFloat(
            self.travelVector[0] * self.travelSpeed,
            self.travelVector[1] * self.travelSpeed
        )

        # remove offscreen projectiles
        if self.rect.y > self.gameInstance.height:
            self.die()
            return

    def die(self):
        bossProjectiles = self.sceneInstance.gameObjects["bossProjectiles"]
        for i in range(len(bossProjectiles)):
            if self == bossProjectiles[i]:
                del bossProjectiles[i]
                break


class Player(GameplayObject):
    # noinspection PyArgumentList
    def __init__(self, gameInstance, image: pygame.Surface):
        super().__init__(gameInstance)
        self.width = 60
        self.height = 65
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.move_ip((self.gameInstance.width - self.width) / 2, self.gameInstance.height - self.height - 10)

        self.maxSpeed = 8
        self.speedDumpingFactor = 0.92
        self.acceleration = 0.6
        self.currentSpeed = {
            "x": 0,
            "y": 0
        }
        # self.minHeight = self.gameInstance.height - 300
        self.minHeight = 0

        self.isShooting = False
        self.shootingSpeed = 20
        self.shootingCooldown = 0
        self.projectileSpeed = 12
        self.projectileDamage = 1
        self.activePowerups = list()
        self.invincibility = False
        self.shieldSurface = self.sceneInstance.images["playerShield"]
        self.shieldSurface.set_alpha(100)

    def draw(self):
        self.gameInstance.screen.blit(self.image, self.rect)
        if self.invincibility:
            self.gameInstance.screen.blit(self.shieldSurface, (self.rect.x - 3, self.rect.y + 2))

    def updateSpeed(self):
        self.currentSpeed["x"] *= self.speedDumpingFactor
        self.currentSpeed["y"] *= self.speedDumpingFactor

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
                   self.sceneInstance.images["projectile"],
                   (self.rect.x + self.width / 2, self.rect.y),
                   self.projectileSpeed,
                   self.projectileDamage
                   )

    def handleInput(self):
        # ifs instead of elifs to allow for change in speed in more than one direction
        if pygame.key.get_pressed()[pygame.K_a]:
            self.currentSpeed["x"] -= self.acceleration
        if pygame.key.get_pressed()[pygame.K_d]:
            self.currentSpeed["x"] += self.acceleration
        if pygame.key.get_pressed()[pygame.K_s]:
            self.currentSpeed["y"] += self.acceleration
        if pygame.key.get_pressed()[pygame.K_w]:
            self.currentSpeed["y"] -= self.acceleration

    def update(self):
        if not self.sceneInstance.isActive:
            return

        if not self.invincibility:
            # check for collision with enemy ships
            for enemy in self.sceneInstance.gameObjects["enemies"]:
                if self.rect.colliderect(enemy.rect):
                    self.die()
                    return

            # check for collision with enemy projectiles
            for bossProjectiles in self.sceneInstance.gameObjects["bossProjectiles"]:
                if self.rect.colliderect(bossProjectiles.rect):
                    self.die()
                    return

        # check for collision with powerups
        for powerup in self.sceneInstance.gameObjects["powerups"]:
            if self.rect.colliderect(powerup.rect):
                found = False
                for activePowerup in self.activePowerups:
                    if powerup.type.value == activePowerup.type.value:
                        activePowerup.duration = activePowerup.startDuration
                        found = True
                if not found:
                    powerup.onPickup()
                powerup.die()

        # movement
        self.updateSpeed()
        self.updatePosition()

        # shooting
        if self.shootingCooldown == 0:
            if self.isShooting:
                self.shoot()
                self.shootingCooldown = self.shootingSpeed
        else:
            if self.shootingCooldown > 0:
                self.shootingCooldown -= 1

        # update active powerups (since the update method is no longer called from the Scene.tick() )
        for powerup in self.activePowerups:
            powerup.update()

    def die(self):
        self.gameInstance.endScore = self.sceneInstance.score
        self.gameInstance.loadScene("endscreen")


class Enemy(GameplayObject):
    def __init__(self,
                 gameInstance,
                 image: pygame.Surface,
                 pos: (int, int),
                 healthPoints: int = 1,
                 powerup: Powerup = None,
                 scoreValue: int = 100):

        super().__init__(gameInstance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos[0], pos[1])
        self.speed = (2, 0)
        self.width = self.rect.width
        self.height = self.rect.width
        self.yJump = 50
        self.healthPoints = healthPoints
        self.powerup = powerup
        self.scoreValue = scoreValue

    def update(self):
        if not self.sceneInstance.isActive:
            return

        self.moveFloat(self.speed[0], self.speed[1])

        # change direction
        if self.rect.x < 0 or self.rect.x + self.width > self.gameInstance.width:
            self.speed = (-self.speed[0], self.speed[1])
            self.rect.y += self.yJump

        # make sure enemy is right at the edge of screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.width > self.gameInstance.width:
            self.rect.x = self.gameInstance.width - self.width

    def die(self):
        self.sceneInstance.score += self.scoreValue

        # spawn powerup on death
        if self.powerup:
            # move powerup on top of the crime scene
            x, y = self.rect.center
            x -= self.powerup.rect.width / 2
            y -= self.powerup.rect.height / 2
            self.powerup.moveFloat(x, y)
            self.sceneInstance.gameObjects["powerups"].append(self.powerup)

        enemies = self.sceneInstance.gameObjects["enemies"]
        for i in range(len(enemies)):
            if self == enemies[i]:
                del enemies[i]
                break

        self.sceneInstance.checkForEnd()

    def damage(self, value: int):
        self.healthPoints -= value
        if self.healthPoints <= 0:
            self.die()

    def setSpeed(self, newSpeed: (float, float)):
        self.speed = newSpeed
        return self


class Boss(Enemy):
    def __init__(self, gameInstance, images: dict):
        x = (gameInstance.width - images["boss"].get_rect().width) / 2
        self.maxHp = 120

        super().__init__(gameInstance, images["boss"], (x, 30), self.maxHp, scoreValue=100000)

        self.speed = 1.5
        self.projectile = images["enemyProjectile"]
        self.projectile_directed = images["enemyProjectile_directed"]
        self.projectile_spread = images["enemyProjectile_spread"]
        self.projectileSpeed = 2
        self.shootingSpeed = 60
        self.shootingCooldown = 0

        self.currentPhase = 0
        self.startingPhaseDuration = 300
        self.phaseDuration = self.startingPhaseDuration

        self.spawnSpeed = 300
        self.spawnCooldown = 150

    def update(self):
        # --- movement ---
        self.moveFloat(self.speed, 0)
        # change direction
        if self.rect.x <= 100 or self.rect.x + self.rect.width >= self.gameInstance.width - 100:
            self.speed = -self.speed
        # make sure enemy is right at the edge of screen
        if self.rect.x < 100:
            self.rect.x = 100
        elif self.rect.x + self.width > self.gameInstance.width - 100:
            self.rect.x = self.gameInstance.width - self.width - 100

        # shooting
        if self.shootingCooldown == 0:
            self.shoot()
            self.shootingCooldown = self.shootingSpeed
        else:
            if self.shootingCooldown > 0:
                self.shootingCooldown -= 1

        # spawning enemy ships
        if self.spawnCooldown == 0:
            self.spawnShip()
            print("spawn")
            self.spawnCooldown = self.spawnSpeed
        else:
            if self.spawnCooldown > 0:
                self.spawnCooldown -= 1

        # changing phases
        self.phaseDuration -= 1
        if self.phaseDuration == 0:
            self.nextPhase()

    def shoot(self):
        if self.currentPhase == 0:
            BossProjectile(self.gameInstance,
                           self.projectile,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           # self.getVectorTo(self.sceneInstance.gameObjects["player"]),
                           (0, 1),
                           self.projectileSpeed)

        elif self.currentPhase == 1:
            BossProjectile(self.gameInstance,
                           self.projectile_directed,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           self.getVectorTo(self.sceneInstance.gameObjects["player"]),
                           self.projectileSpeed)

        elif self.currentPhase == 2:
            BossProjectile(self.gameInstance,
                           self.projectile_spread,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           (0, 1),
                           self.projectileSpeed)
            BossProjectile(self.gameInstance,
                           self.projectile_spread,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           self.rotateVector((0, 1), pi/6),
                           self.projectileSpeed)
            BossProjectile(self.gameInstance,
                           self.projectile_spread,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           self.rotateVector((0, 1), -pi/6),
                           self.projectileSpeed)

    def nextPhase(self):
        self.currentPhase += 1
        if self.healthPoints > self.maxHp / 2:
            self.currentPhase %= 2
        else:
            # 3rd phase reachable only on less than half boss hp left
            self.currentPhase %= 3

        # reset phase duration left
        self.phaseDuration = self.startingPhaseDuration

        # fine tune boss shooting stats to accomodate for diffrent modes of firing
        if self.currentPhase == 0:
            self.projectileSpeed = 2
            self.shootingSpeed = 70
        elif self.currentPhase == 1:
            self.projectileSpeed = 3
            self.shootingSpeed = 60
        elif self.currentPhase == 2:
            self.projectileSpeed = 3
            self.shootingSpeed = 50

        # spawn enemies with powerups on phase change
        if self.currentPhase == 0:
            powerup = Powerup(
                self.gameInstance,
                self.sceneInstance.images["powerup_speed"],
                PowerupType.SPEED)
            self.sceneInstance.gameObjects["enemies"].append(
                Enemy(
                    self.gameInstance,
                    self.sceneInstance.images["enemySpecial"],
                    (self.rect.x + 50, self.rect.y + 100),
                    powerup=powerup,
                    scoreValue=5000,
                    healthPoints=3
                )
            )
        elif self.currentPhase == 1:
            powerup = Powerup(
                self.gameInstance,
                self.sceneInstance.images["powerup_invincibility"],
                PowerupType.INVINCIBILITY
            )
            enemy = Enemy(
                    self.gameInstance,
                    self.sceneInstance.images["enemySpecial"],
                    (self.rect.x - 50, self.rect.y + 100),
                    powerup=powerup,
                    scoreValue=5000,
                    healthPoints=3
                )
            enemy.setSpeed((-2, 0))
            self.sceneInstance.gameObjects["enemies"].append(enemy)

        else:
            powerup1 = Powerup(
                self.gameInstance,
                self.sceneInstance.images["powerup_power"],
                PowerupType.POWER
            )
            powerup2 = Powerup(
                self.gameInstance,
                self.sceneInstance.images["powerup_invincibility"],
                PowerupType.INVINCIBILITY
            )
            self.sceneInstance.gameObjects["enemies"].append(
                Enemy(
                    self.gameInstance,
                    self.sceneInstance.images["enemySpecial"],
                    (self.rect.x - 50, self.rect.y + 100),
                    powerup=powerup1,
                    scoreValue=5000,
                    healthPoints=3
                )
            )
            self.sceneInstance.gameObjects["enemies"].append(
                Enemy(
                    self.gameInstance,
                    self.sceneInstance.images["enemySpecial"],
                    (self.rect.x + 50, self.rect.y + 100),
                    powerup=powerup2,
                    scoreValue=5000,
                    healthPoints=3
                )
            )

    def spawnShip(self):
        for i in range(randint(1, 3)):
            self.sceneInstance.gameObjects["enemies"].append(
                Enemy(
                    self.gameInstance,
                    self.sceneInstance.images["enemy"],
                    (self.rect.x - 50 * (i+1), self.rect.y + 100),
                    scoreValue=1000
                ).setSpeed((-2, 0))
            )
            self.sceneInstance.gameObjects["enemies"].append(
                Enemy(
                    self.gameInstance,
                    self.sceneInstance.images["enemy"],
                    (self.rect.x + 50 * (i + 1), self.rect.y + 100),
                    scoreValue=1000
                )
            )

    def getVectorTo(self, player) -> (float, float):
        bossX = self.rect.x + self.width / 2
        bossY = self.rect.y + self.rect.height - 10
        playerX, playerY = player.rect.center

        dx, dy = playerX - bossX, playerY - bossY
        mag = sqrt(dx*dx + dy*dy)
        dx /= mag
        dy /= mag
        return dx, dy

    @staticmethod
    def rotateVector(vector: (float, float), alpha: float) -> (float, float):
        x = cos(alpha)*vector[0] - sin(alpha)*vector[1]
        y = sin(alpha)*vector[0] + cos(alpha)*vector[1]
        return x, y

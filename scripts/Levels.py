from scripts.GameplayObjects import Player, Enemy, Powerup, PowerupType, Boss


class Level:
    def __init__(self):
        self.gameObjects = {
            "player": None,
            "enemies": [],
            "playerProjectiles": [],
            "bossProjectiles": [],
            "powerups": []
            # "blocks": [],
        }
        self.killScore = 100
        self.specialKillScore = 500
        self.rowHeight = 100

    def load(self, gameInstance, images: dict):
        self.gameObjects["player"] = Player(gameInstance, images["player"])


class Level1(Level):
    def __init__(self):
        super().__init__()

    def load(self, gameInstance, images: dict) -> dict:
        super().load(gameInstance, images)

        for r in range(2):
            for i in range(100, 701, 60):
                enemy = Enemy(gameInstance, images["enemy"], (i, r * self.rowHeight), scoreValue=int(self.killScore))
                if r == 1:
                    enemy.setSpeed((-2, 0))
                self.gameObjects["enemies"].append(enemy)

        return self.gameObjects


class Level2(Level):
    def __init__(self):
        super().__init__()
        self.killScore *= 1.5
        self.specialKillScore *= 1.5

    def load(self, gameInstance, images: dict) -> dict:
        super().load(gameInstance, images)

        for i in range(100, 701, 60):
            self.gameObjects["enemies"].append(
                Enemy(gameInstance, images["enemy2"], (i, 0), healthPoints=3, scoreValue=int(self.killScore) * 3)
            )
        for r in range(1, 4):
            for i in range(100, 701, 60):
                enemy = Enemy(gameInstance, images["enemy"], (i, r * self.rowHeight), scoreValue=int(self.killScore))
                if r in [1, 3]:
                    enemy.setSpeed((-2, 0))
                self.gameObjects["enemies"].append(enemy)
        self.gameObjects["enemies"].append(
            Enemy(gameInstance,
                  images["enemySpecial"],
                  (370, 400),
                  healthPoints=3,
                  powerup=Powerup(gameInstance, images["powerup_power"], PowerupType.POWER),
                  scoreValue=int(self.specialKillScore))
        )

        return self.gameObjects


class Level3(Level):
    def __init__(self):
        super().__init__()
        self.killScore *= 4.5
        self.specialKillScore *= 4.5

    def load(self, gameInstance, images: dict) -> dict:
        super().load(gameInstance, images)

        for i in range(100, 701, 60):
            self.gameObjects["enemies"].append(
                Enemy(gameInstance, images["enemy3"], (i, 0), healthPoints=5, scoreValue=int(self.killScore) * 5)
            )
        for i in range(100, 701, 60):
            self.gameObjects["enemies"].append(
                Enemy(gameInstance, images["enemy2"], (i, 100), healthPoints=3, scoreValue=int(self.killScore) * 3)
                .setSpeed((-2, 0))
            )
        for r in range(2, 4):
            for i in range(100, 701, 60):
                enemy = Enemy(gameInstance, images["enemy"], (i, r * self.rowHeight), scoreValue=int(self.killScore))
                if r == 3:
                    enemy.setSpeed((-2, 0))
                self.gameObjects["enemies"].append(enemy)
        self.gameObjects["enemies"].append(
            Enemy(gameInstance,
                  images["enemySpecial"],
                  (470, 400),
                  healthPoints=3,
                  powerup=Powerup(gameInstance, images["powerup_power"], PowerupType.POWER),
                  scoreValue=int(self.specialKillScore))
        )
        self.gameObjects["enemies"].append(
            Enemy(gameInstance,
                  images["enemySpecial"],
                  (270, 400),
                  healthPoints=3,
                  powerup=Powerup(gameInstance, images["powerup_speed"], PowerupType.SPEED),
                  scoreValue=int(self.specialKillScore))
        )

        return self.gameObjects


class Level4(Level):
    def __init__(self):
        super().__init__()
        self.killScore *= 6
        self.specialKillScore *= 6

    def load(self, gameInstance, images: dict) -> dict:
        super().load(gameInstance, images)

        for r in range(0, 4):
            for i in range(100, 701, 60):
                if r < 2:
                    enemy = Enemy(gameInstance,
                                  images["enemy3"],
                                  (i, r * self.rowHeight),
                                  healthPoints=5,
                                  scoreValue=int(self.killScore) * 5
                                  )
                    if r == 0:
                        enemy.setSpeed((-2, 0))
                    self.gameObjects["enemies"].append(enemy)
                else:
                    if r == 3 and i in [160, 340, 400, 640]:
                        powerup = None
                        if i in [160, 640]:
                            powerup = Powerup(gameInstance, images["powerup_speed"], PowerupType.SPEED)
                        elif i == 340:
                            powerup = Powerup(gameInstance, images["powerup_power"], PowerupType.POWER)
                        elif i == 400:
                            powerup = Powerup(gameInstance, images["powerup_ghostBullets"], PowerupType.GHOST_BULLETS)
                        self.gameObjects["enemies"].append(
                            Enemy(gameInstance,
                                  images["enemySpecial"],
                                  (i, r * self.rowHeight),
                                  healthPoints=3,
                                  powerup=powerup,
                                  scoreValue=int(self.specialKillScore)
                                  )
                        )
                    else:
                        enemy = Enemy(gameInstance, images["enemy"], (i, r * self.rowHeight),
                                      scoreValue=int(self.killScore))
                        if r == 2:
                            enemy.setSpeed((-2, 0))
                        self.gameObjects["enemies"].append(enemy)

        return self.gameObjects


class Level5(Level):
    def __init__(self):
        super().__init__()
        self.killScore *= 10
        self.specialKillScore *= 10

    def load(self, gameInstance, images: dict) -> dict:
        super().load(gameInstance, images)

        boss = Boss(gameInstance, images)
        self.gameObjects["enemies"].append(boss)
        self.gameObjects["boss"] = boss

        return self.gameObjects

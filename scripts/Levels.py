from scripts.GameplayObjects import Player, Enemy, Powerup, PowerupType, Boss


class Level:
    def __init__(self):
        self.game_objects = {
            "player": None,
            "enemies": [],
            "player_projectiles": [],
            "boss_projectiles": [],
            "powerups": []
            # "blocks": [],
        }
        self.kill_score = 100
        self.special_kill_score = 500
        self.row_height = 100

    def load(self, game_instance, images: dict):
        self.game_objects["player"] = Player(game_instance, images["player"])


class Level1(Level):
    def __init__(self):
        super().__init__()

    def load(self, game_instance, images: dict) -> dict:
        super().load(game_instance, images)

        for r in range(2):
            for i in range(100, 701, 60):
                enemy = Enemy(game_instance, images["enemy"], (i, r * self.row_height), score_value=int(self.kill_score))
                if r == 1:
                    enemy.set_speed((-2, 0))
                self.game_objects["enemies"].append(enemy)

        return self.game_objects


class Level2(Level):
    def __init__(self):
        super().__init__()
        self.kill_score *= 1.5
        self.special_kill_score *= 1.5

    def load(self, game_instance, images: dict) -> dict:
        super().load(game_instance, images)

        for i in range(100, 701, 60):
            self.game_objects["enemies"].append(
                Enemy(game_instance, images["enemy2"], (i, 0), health_points=3, score_value=int(self.kill_score) * 3)
            )
        for r in range(1, 4):
            for i in range(100, 701, 60):
                enemy = Enemy(game_instance, images["enemy"], (i, r * self.row_height), score_value=int(self.kill_score))
                if r in [1, 3]:
                    enemy.set_speed((-2, 0))
                self.game_objects["enemies"].append(enemy)
        self.game_objects["enemies"].append(
            Enemy(game_instance,
                  images["enemy_special"],
                  (370, 400),
                  health_points=3,
                  powerup=Powerup(game_instance, images["powerup_power"], PowerupType.POWER),
                  score_value=int(self.special_kill_score))
        )

        return self.game_objects


class Level3(Level):
    def __init__(self):
        super().__init__()
        self.kill_score *= 4.5
        self.special_kill_score *= 4.5

    def load(self, game_instance, images: dict) -> dict:
        super().load(game_instance, images)

        for i in range(100, 701, 60):
            self.game_objects["enemies"].append(
                Enemy(game_instance, images["enemy3"], (i, 0), health_points=5, score_value=int(self.kill_score) * 5)
            )
        for i in range(100, 701, 60):
            self.game_objects["enemies"].append(
                Enemy(game_instance, images["enemy2"], (i, 100), health_points=3, score_value=int(self.kill_score) * 3)
                .set_speed((-2, 0))
            )
        for r in range(2, 4):
            for i in range(100, 701, 60):
                enemy = Enemy(game_instance, images["enemy"], (i, r * self.row_height), score_value=int(self.kill_score))
                if r == 3:
                    enemy.set_speed((-2, 0))
                self.game_objects["enemies"].append(enemy)
        self.game_objects["enemies"].append(
            Enemy(game_instance,
                  images["enemy_special"],
                  (470, 400),
                  health_points=3,
                  powerup=Powerup(game_instance, images["powerup_power"], PowerupType.POWER),
                  score_value=int(self.special_kill_score))
        )
        self.game_objects["enemies"].append(
            Enemy(game_instance,
                  images["enemy_special"],
                  (270, 400),
                  health_points=3,
                  powerup=Powerup(game_instance, images["powerup_speed"], PowerupType.SPEED),
                  score_value=int(self.special_kill_score))
        )

        return self.game_objects


class Level4(Level):
    def __init__(self):
        super().__init__()
        self.kill_score *= 6
        self.special_kill_score *= 6

    def load(self, game_instance, images: dict) -> dict:
        super().load(game_instance, images)

        for r in range(0, 4):
            for i in range(100, 701, 60):
                if r < 2:
                    enemy = Enemy(game_instance,
                                  images["enemy3"],
                                  (i, r * self.row_height),
                                  health_points=5,
                                  score_value=int(self.kill_score) * 5
                                  )
                    if r == 0:
                        enemy.set_speed((-2, 0))
                    self.game_objects["enemies"].append(enemy)
                else:
                    if r == 3 and i in [160, 340, 400, 640]:
                        powerup = None
                        if i in [160, 640]:
                            powerup = Powerup(game_instance, images["powerup_speed"], PowerupType.SPEED)
                        elif i == 340:
                            powerup = Powerup(game_instance, images["powerup_power"], PowerupType.POWER)
                        elif i == 400:
                            powerup = Powerup(game_instance, images["powerup_ghost_bullets"], PowerupType.GHOST_BULLETS)
                        self.game_objects["enemies"].append(
                            Enemy(game_instance,
                                  images["enemy_special"],
                                  (i, r * self.row_height),
                                  health_points=3,
                                  powerup=powerup,
                                  score_value=int(self.special_kill_score)
                                  )
                        )
                    else:
                        enemy = Enemy(game_instance, images["enemy"], (i, r * self.row_height),
                                      score_value=int(self.kill_score))
                        if r == 2:
                            enemy.set_speed((-2, 0))
                        self.game_objects["enemies"].append(enemy)

        return self.game_objects


class Level5(Level):
    def __init__(self):
        super().__init__()
        self.kill_score *= 10
        self.special_kill_score *= 10

    def load(self, game_instance, images: dict) -> dict:
        super().load(game_instance, images)

        boss = Boss(game_instance, images)
        self.game_objects["enemies"].append(boss)
        self.game_objects["boss"] = boss

        return self.game_objects

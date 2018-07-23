import pygame

from enum import Enum
from math import sin, cos, sqrt, pi
from random import randint


class GameplayObject:
    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.scene_instance = game_instance.current_scene
        self.image = None
        self.rect = None

        # used in move_float method
        self.dx = 0
        self.dy = 0

    def update(self):
        raise NotImplementedError

    def handle_input(self):
        pass

    def draw(self):
        self.game_instance.screen.blit(self.image, self.rect)

    # since rect stores (x,y) values as ints this helper function allows for game_objects to be moved by
    # finer values storing exact change in position and moving object only by the integer part
    def move_float(self, x: float, y: float):
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
    GHOST_BULLETS = "powerup_ghost_bullets"
    INVINCIBILITY = "powerup_invincibility"


class Powerup(GameplayObject):
    def __init__(self, game_instance, image: pygame.Surface, powerup_type: PowerupType):
        super().__init__(game_instance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.player = None
        self.type = powerup_type
        self.is_picked_up = False

        if powerup_type == PowerupType.POWER:
            self.start_duration = 300
        elif powerup_type == PowerupType.SPEED:
            self.start_duration = 1000
        elif powerup_type == PowerupType.GHOST_BULLETS:
            self.start_duration = 500
        elif powerup_type == PowerupType.INVINCIBILITY:
            self.start_duration = 500
        self.duration = self.start_duration

    def update(self):
        if not self.scene_instance.is_active:
            return

        if self.is_picked_up:
            self.duration -= 1
            if self.duration == 0:
                self.on_duration_end()
        else:
            self.rect.move_ip(0, 3)
            if self.rect.y > self.game_instance.height:
                self.die()

    def on_pickup(self):
        self.is_picked_up = True
        self.player = self.scene_instance.game_objects["player"]
        self.player.active_powerups.append(self)
        if self.type == PowerupType.POWER:
            self.player.projectile_damage = 4
            self.player.projectile_speed = 24
            self.player.shooting_speed = 14

        elif self.type == PowerupType.SPEED:
            self.player.max_speed = 11
            self.player.speed_dumping_factor = 0.9
            self.player.acceleration = 1.5

        elif self.type == PowerupType.INVINCIBILITY:
            self.player.invincibility = True
            # ghost bullets handled in Projectile.update()

    def on_duration_end(self):
        if self.type == PowerupType.POWER:
            self.player.projectile_damage = 1
            self.player.projectile_speed = 12
            self.player.shooting_speed = 20

        elif self.type == PowerupType.SPEED:
            self.player.max_speed = 8
            self.player.speed_dumping_factor = 0.92
            self.player.acceleration = 0.6

        elif self.type == PowerupType.INVINCIBILITY:
            self.player.invincibility = False
        # ghost bullets handled in Projectile.update()

        self.die(True)

    def die(self, look_in_player: bool = False):
        if look_in_player:
            powerups = self.player.active_powerups
        else:
            powerups = self.scene_instance.game_objects["powerups"]
        for i in range(len(powerups)):
            if self == powerups[i]:
                del powerups[i]
                break


class Projectile(GameplayObject):
    def __init__(self,
                 game_instance,
                 image: pygame.Surface,
                 pos: (int, int),
                 travel_speed: int,
                 damage: int):

        super().__init__(game_instance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos[0] - self.rect.width / 2, pos[1])
        self.player_instance = self.scene_instance.game_objects["player"]
        self.travel_speed = travel_speed
        self.damage = damage
        self.scene_instance.game_objects["player_projectiles"].append(self)

        # needed when player gets 'ghostBullets' powerup
        self.enemies_hit = list()

    def update(self):
        if not self.scene_instance.is_active:
            return

        self.move_float(0, -self.travel_speed)

        # remove off screen projectiles
        if self.rect.y < -self.rect.height:
            self.die()
            return

        # check for collision with enemy ships
        for enemy in self.scene_instance.game_objects["enemies"]:
            if self.rect.colliderect(enemy.rect) and enemy not in self.enemies_hit:
                enemy.damage(self.damage)
                self.enemies_hit.append(enemy)
                for powerup in self.player_instance.active_powerups:
                    if powerup.type == PowerupType.GHOST_BULLETS:
                        # important: make sure that this collision detection code is the last piece
                        #            in the update function so the return below wont break anything.
                        return
                self.die()

    def die(self):
        if not self.scene_instance.is_active:
            return
        player_projectiles = self.scene_instance.game_objects["player_projectiles"]
        for i in range(len(player_projectiles)):
            if self == player_projectiles[i]:
                del player_projectiles[i]
                break


class BossProjectile(GameplayObject):
    def __init__(self,
                 game_instance,
                 image: pygame.Surface,
                 pos: (int, int),
                 travel_vector: (float, float),
                 travel_speed: int):

        super().__init__(game_instance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos[0] - self.rect.width / 2, pos[1])
        self.travel_vector = travel_vector
        self.travel_speed = travel_speed
        self.scene_instance.game_objects["boss_projectiles"].append(self)
        self.player = self.scene_instance.game_objects["player"]

    def update(self):
        if not self.scene_instance.is_active:
            return

        self.move_float(
            self.travel_vector[0] * self.travel_speed,
            self.travel_vector[1] * self.travel_speed
        )

        # remove off screen projectiles
        if self.rect.y > self.game_instance.height:
            self.die()
            return

    def die(self):
        boss_projectiles = self.scene_instance.game_objects["boss_projectiles"]
        for i in range(len(boss_projectiles)):
            if self == boss_projectiles[i]:
                del boss_projectiles[i]
                break


class Player(GameplayObject):
    def __init__(self, game_instance, image: pygame.Surface):
        super().__init__(game_instance)
        self.width = 60
        self.height = 65
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.move_ip((self.game_instance.width - self.width) / 2, self.game_instance.height - self.height - 10)

        self.max_speed = 8
        self.speed_dumping_factor = 0.92
        self.acceleration = 0.6
        self.current_speed = {
            "x": 0,
            "y": 0
        }
        # self.min_height = self.game_instance.height - 300
        self.min_height = 0

        self.is_shooting = False
        self.shooting_speed = 20
        self.shooting_cooldown = 0
        self.projectile_speed = 12
        self.projectile_damage = 1
        self.active_powerups = list()
        self.invincibility = False
        self.shield_surface = self.scene_instance.images["player_shield"]
        self.shield_surface.set_alpha(100)

    def draw(self):
        self.game_instance.screen.blit(self.image, self.rect)
        if self.invincibility:
            self.game_instance.screen.blit(self.shield_surface, (self.rect.x - 3, self.rect.y + 2))

    def update_speed(self):
        self.current_speed["x"] *= self.speed_dumping_factor
        self.current_speed["y"] *= self.speed_dumping_factor

        if self.current_speed["x"] > self.max_speed:
            self.current_speed["x"] = self.max_speed
        elif self.current_speed["x"] < -self.max_speed:
            self.current_speed["x"] = -self.max_speed
        if self.current_speed["y"] > self.max_speed:
            self.current_speed["y"] = self.max_speed
        elif self.current_speed["y"] < -self.max_speed:
            self.current_speed["y"] = -self.max_speed

    def update_position(self):
        self.move(self.current_speed["x"], self.current_speed["y"])

    def move(self, x, y):
        self.move_float(x, y)

        if self.rect.x < 0:
            self.rect.x = 0
            self.current_speed["x"] = 0
        elif self.rect.x + self.width > self.game_instance.width:
            self.rect.x = self.game_instance.width - self.width
            self.current_speed["x"] = 0

        if self.rect.y < self.min_height:
            self.rect.y = self.min_height
            self.current_speed["y"] = 0

        elif self.rect.y + self.height > self.game_instance.height:
            self.rect.y = self.game_instance.height - self.height
            self.current_speed["y"] = 0

    def shoot(self):
        Projectile(self.game_instance,
                   self.scene_instance.images["projectile"],
                   (self.rect.x + self.width / 2, self.rect.y),
                   self.projectile_speed,
                   self.projectile_damage
                   )

    def handle_input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            self.current_speed["x"] -= self.acceleration
        if pressed[pygame.K_d]:
            self.current_speed["x"] += self.acceleration
        if pressed[pygame.K_s]:
            self.current_speed["y"] += self.acceleration
        if pressed[pygame.K_w]:
            self.current_speed["y"] -= self.acceleration

        # DEBUG
        if pressed[pygame.K_v]:
            self.projectile_damage += 1

    def update(self):
        if not self.scene_instance.is_active:
            return

        if not self.invincibility:
            # check for collision with enemy ships
            for enemy in self.scene_instance.game_objects["enemies"]:
                if self.rect.colliderect(enemy.rect):
                    self.die()
                    return

            # check for collision with enemy projectiles
            for boss_projectiles in self.scene_instance.game_objects["boss_projectiles"]:
                if self.rect.colliderect(boss_projectiles.rect):
                    self.die()
                    return

        # check for collision with powerups
        for powerup in self.scene_instance.game_objects["powerups"]:
            if self.rect.colliderect(powerup.rect):
                found = False
                for active_powerup in self.active_powerups:
                    if powerup.type.value == active_powerup.type.value:
                        active_powerup.duration = active_powerup.start_duration
                        found = True
                if not found:
                    powerup.on_pickup()
                powerup.die()

        # movement
        self.update_speed()
        self.update_position()

        # shooting
        if self.shooting_cooldown == 0:
            if self.is_shooting:
                self.shoot()
                self.shooting_cooldown = self.shooting_speed
        else:
            if self.shooting_cooldown > 0:
                self.shooting_cooldown -= 1

        # update active powerups (since the update method is no longer called from the Scene.tick() )
        for powerup in self.active_powerups:
            powerup.update()

    def die(self):
        self.game_instance.end_score = self.scene_instance.score
        self.game_instance.load_scene("endscreen")


class Enemy(GameplayObject):
    def __init__(self,
                 game_instance,
                 image: pygame.Surface,
                 pos: (int, int),
                 health_points: int = 1,
                 powerup: Powerup = None,
                 score_value: int = 100):

        super().__init__(game_instance)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos[0], pos[1])
        self.speed = (2, 0)
        self.width = self.rect.width
        self.height = self.rect.width
        self.y_jump = 50
        self.health_points = health_points
        self.powerup = powerup
        self.score_value = score_value

    def update(self):
        if not self.scene_instance.is_active:
            return

        self.move_float(self.speed[0], self.speed[1])

        # change direction
        if self.rect.x < 0 or self.rect.x + self.width > self.game_instance.width:
            self.speed = (-self.speed[0], self.speed[1])
            self.rect.y += self.y_jump

        # make sure enemy is right at the edge of screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.width > self.game_instance.width:
            self.rect.x = self.game_instance.width - self.width

        # end the game if enemy touched the bottom of screen
        if self.rect.y + self.rect.height > self.game_instance.height:
            self.scene_instance.game_objects["player"].die()

    def die(self):
        self.scene_instance.score += self.score_value

        # spawn powerup on death
        if self.powerup:
            # move powerup on top of the crime scene
            x, y = self.rect.center
            x -= self.powerup.rect.width / 2
            y -= self.powerup.rect.height / 2
            self.powerup.move_float(x, y)
            self.scene_instance.game_objects["powerups"].append(self.powerup)

        enemies = self.scene_instance.game_objects["enemies"]
        for i in range(len(enemies)):
            if self == enemies[i]:
                del enemies[i]
                break

        self.scene_instance.check_for_end()

    def damage(self, value: int):
        self.health_points -= value
        if self.health_points <= 0:
            self.die()

    def set_speed(self, new_speed: (float, float)):
        self.speed = new_speed
        return self


class Boss(Enemy):
    def __init__(self, game_instance, images: dict):
        x = (game_instance.width - images["boss"].get_rect().width) / 2
        self.max_hp = 120

        super().__init__(game_instance, images["boss"], (x, 30), self.max_hp, score_value=100000)

        self.speed = 1.5
        self.projectile = images["enemy_projectile"]
        self.projectile_directed = images["enemy_projectile_directed"]
        self.projectile_spread = images["enemy_projectile_spread"]
        self.projectile_speed = 2
        self.shooting_speed = 60
        self.shooting_cooldown = 0

        self.current_phase = 0
        self.starting_phase_duration = 300
        self.phase_duration = self.starting_phase_duration

        self.spawn_speed = 300
        self.spawn_cooldown = 150

    def update(self):
        # --- movement ---
        self.move_float(self.speed, 0)
        # change direction
        if self.rect.x <= 100 or self.rect.x + self.rect.width >= self.game_instance.width - 100:
            self.speed = -self.speed
        # make sure enemy is right at the edge of screen
        if self.rect.x < 100:
            self.rect.x = 100
        elif self.rect.x + self.width > self.game_instance.width - 100:
            self.rect.x = self.game_instance.width - self.width - 100

        # shooting
        if self.shooting_cooldown == 0:
            self.shoot()
            self.shooting_cooldown = self.shooting_speed
        else:
            if self.shooting_cooldown > 0:
                self.shooting_cooldown -= 1

        # spawning enemy ships
        if self.spawn_cooldown == 0:
            self.spawn_ship()
            self.spawn_cooldown = self.spawn_speed
        else:
            if self.spawn_cooldown > 0:
                self.spawn_cooldown -= 1

        # changing phases
        self.phase_duration -= 1
        if self.phase_duration == 0:
            self.next_phase()

    def shoot(self):
        if self.current_phase == 0:
            BossProjectile(self.game_instance,
                           self.projectile,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           # self.get_vector_to(self.scene_instance.game_objects["player"]),
                           (0, 1),
                           self.projectile_speed)

        elif self.current_phase == 1:
            BossProjectile(self.game_instance,
                           self.projectile_directed,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           self.get_vector_to(self.scene_instance.game_objects["player"]),
                           self.projectile_speed)

        elif self.current_phase == 2:
            BossProjectile(self.game_instance,
                           self.projectile_spread,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           (0, 1),
                           self.projectile_speed)
            BossProjectile(self.game_instance,
                           self.projectile_spread,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           self.rotate_vector((0, 1), pi / 6),
                           self.projectile_speed)
            BossProjectile(self.game_instance,
                           self.projectile_spread,
                           (self.rect.x + self.width / 2, self.rect.y + self.rect.height - 10),
                           self.rotate_vector((0, 1), -pi / 6),
                           self.projectile_speed)

    def next_phase(self):
        self.current_phase += 1
        if self.health_points > self.max_hp / 2:
            self.current_phase %= 2
        else:
            # 3rd phase reachable only on less than half boss hp left
            self.current_phase %= 3

        # reset phase duration left
        self.phase_duration = self.starting_phase_duration

        # tune boss shooting stats to accommodate for different modes of firing
        if self.current_phase == 0:
            self.projectile_speed = 2
            self.shooting_speed = 70
        elif self.current_phase == 1:
            self.projectile_speed = 3
            self.shooting_speed = 60
        elif self.current_phase == 2:
            self.projectile_speed = 3
            self.shooting_speed = 50

        # spawn enemies with powerups on phase change
        if self.current_phase == 0:
            powerup = Powerup(
                self.game_instance,
                self.scene_instance.images["powerup_speed"],
                PowerupType.SPEED)
            self.scene_instance.game_objects["enemies"].append(
                Enemy(
                    self.game_instance,
                    self.scene_instance.images["enemy_special"],
                    (self.rect.x + 50, self.rect.y + 100),
                    powerup=powerup,
                    score_value=5000,
                    health_points=3
                )
            )
        elif self.current_phase == 1:
            powerup = Powerup(
                self.game_instance,
                self.scene_instance.images["powerup_invincibility"],
                PowerupType.INVINCIBILITY
            )
            enemy = Enemy(
                self.game_instance,
                self.scene_instance.images["enemy_special"],
                (self.rect.x - 50, self.rect.y + 100),
                powerup=powerup,
                score_value=5000,
                health_points=3
            )
            enemy.set_speed((-2, 0))
            self.scene_instance.game_objects["enemies"].append(enemy)

        else:
            powerup1 = Powerup(
                self.game_instance,
                self.scene_instance.images["powerup_power"],
                PowerupType.POWER
            )
            powerup2 = Powerup(
                self.game_instance,
                self.scene_instance.images["powerup_invincibility"],
                PowerupType.INVINCIBILITY
            )
            self.scene_instance.game_objects["enemies"].append(
                Enemy(
                    self.game_instance,
                    self.scene_instance.images["enemy_special"],
                    (self.rect.x - 50, self.rect.y + 100),
                    powerup=powerup1,
                    score_value=5000,
                    health_points=3
                )
            )
            self.scene_instance.game_objects["enemies"].append(
                Enemy(
                    self.game_instance,
                    self.scene_instance.images["enemy_special"],
                    (self.rect.x + 50, self.rect.y + 100),
                    powerup=powerup2,
                    score_value=5000,
                    health_points=3
                )
            )

    def spawn_ship(self):
        for i in range(randint(1, 3)):
            self.scene_instance.game_objects["enemies"].append(
                Enemy(
                    self.game_instance,
                    self.scene_instance.images["enemy"],
                    (self.rect.x - 50 * (i + 1), self.rect.y + 100),
                    score_value=1000
                ).set_speed((-2, 0))
            )
            self.scene_instance.game_objects["enemies"].append(
                Enemy(
                    self.game_instance,
                    self.scene_instance.images["enemy"],
                    (self.rect.x + 50 * (i + 1), self.rect.y + 100),
                    score_value=1000
                )
            )

    def get_vector_to(self, player) -> (float, float):
        boss_x = self.rect.x + self.width / 2
        boss_y = self.rect.y + self.rect.height - 10
        player_x, player_y = player.rect.center

        dx, dy = player_x - boss_x, player_y - boss_y
        mag = sqrt(dx * dx + dy * dy)
        dx /= mag
        dy /= mag
        return dx, dy

    @staticmethod
    def rotate_vector(vector: (float, float), alpha: float) -> (float, float):
        x = cos(alpha) * vector[0] - sin(alpha) * vector[1]
        y = sin(alpha) * vector[0] + cos(alpha) * vector[1]
        return x, y


class Particle(GameplayObject):
    def __init__(self, game_instance, particles: list, pos: (int, int) = (None, None), speed: float = 1) -> None:
        super().__init__(game_instance)
        self.particles = particles
        self.speed = speed

        if pos[0] is not None:
            self.position = pos
        else:
            self.position = (randint(0, game_instance.width), 0)

        self.particles.append(self)

    def update(self):
        self.position = (self.position[0], self.position[1] + self.speed)
        if self.position[1] > self.game_instance.height:
            self.die()

    def draw(self):
        self.game_instance.screen.fill((255, 255, 255), pygame.Rect(self.position[0], self.position[1], 1, 1))

    def die(self):
        for i in range(len(self.particles)):
            if self == self.particles[i]:
                del self.particles[i]
                break

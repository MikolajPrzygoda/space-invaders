import os
import sys
import gc
import pygame

from random import randint, random

from scripts.Menu import Menu
from scripts.Levels import *
from scripts.GameplayObjects import Particle


def load_asset(relative_path: str, no_alpha: bool = False) -> pygame.Surface:
    """ Get an asset, works for development and for packaged one-file executable"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    abs_path = os.path.join(base_path, relative_path)

    if no_alpha:
        return pygame.image.load(abs_path).convert()
    else:
        return pygame.image.load(abs_path).convert_alpha()


class Scene:
    def __init__(self, game_instance):
        self.game_instance = game_instance

    def load(self):
        raise NotImplementedError()

    def unload(self):
        raise NotImplementedError()

    def handle_event(self, event):
        raise NotImplementedError()

    def tick(self):
        raise NotImplementedError()


class MainMenuScene(Scene):
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.menu = None
        self.particles = None
        self.spawn_speed = 4
        self.spawn_cooldown = 0

    def load(self):
        self.menu = Menu(self.game_instance, "Space Invaders")
        self.menu.add_item("Graj", "gameplay")
        self.menu.add_item("Pomoc", "help")
        self.menu.add_item("Wyjdź", "quit")
        self.particles = list()

        # 75 is the average count of particles on screen when spawned once every 5 frames, as they are now
        for i in range(75):
            Particle(
                self.game_instance,
                self.particles,
                pos=(randint(0, self.game_instance.width), randint(0, self.game_instance.height)),
                speed=random()*2+1
            )

    def unload(self):
        self.menu = None
        self.particles = None
        gc.collect()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.menu.set_next_as_active()
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                self.menu.set_previous_as_active()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.menu.activate()

    def tick(self):
        if self.spawn_cooldown == 0:
            Particle(self.game_instance, self.particles, speed=random() * 2 + 1)
            self.spawn_cooldown = self.spawn_speed
        else:
            self.spawn_cooldown -= 1

        self.menu.draw()
        for particle in self.particles:
            particle.draw()
            particle.update()


class HelpScreenScene(Scene):
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.font = None
        self.text_color = None
        self.tip_surfaces = None
        self.powerup_surfaces = None
        self.powerup_descrtiptions_surfaces = None
        self.screen_padding = 40
        self.item_bottom_padding = 20

    def load(self):
        self.font = pygame.font.SysFont("monospace", 16)
        self.text_color = (255, 255, 255)
        self.tip_surfaces = [
            self.font.render("Sterowanie statkiem: w/s/a/d", 1, self.text_color),
            self.font.render("Przełączanie strzelania: spacja", 1, self.text_color),
            self.font.render("Wybór opcji menu: spacja / enter", 1, self.text_color),
            self.font.render("W każdej chwili działania gry możesz ja zamknąć za pomocą 'escape'", 1, self.text_color),
            self.font.render("Naciśnij 'q' aby powrócić do menu głównego", 1, self.text_color),
        ]
        self.powerup_descrtiptions_surfaces = [
            self.font.render("Speed - zwiększa prędkość maksymalną i przyśpieszenie statku", 1, self.text_color),
            self.font.render("Power - zwieksza szybkostrzelność, prędkość oraz obrażenia pocisków", 1, self.text_color),
            self.font.render("Passthrough Bullets - twoje pociski przenikają przez przeciwników", 1, self.text_color),
            self.font.render("Invincibiliy - zapewnia nietykalność na krótki czas", 1, self.text_color),
        ]
        self.powerup_surfaces = [
            load_asset("assets/powerup_power.png"),
            load_asset("assets/powerup_speed.png"),
            load_asset("assets/powerup_ghost_bullets.png"),
            load_asset("assets/powerup_invincibility.png")
        ]

    def unload(self):
        self.tip_surfaces = None
        self.font = None
        self.text_color = None
        self.powerup_surfaces = None
        self.powerup_descrtiptions_surfaces = None
        gc.collect()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.game_instance.load_scene("menu")

    def tick(self):
        x, y = self.screen_padding, self.screen_padding

        # print general tips list
        for label in self.tip_surfaces:
            self.game_instance.screen.blit(label, (x, y))
            y += label.get_rect().height + self.item_bottom_padding

        y += 40  # additional padding above power-ups list

        # print list with icons and descriptions of in-game power-ups
        for i in range(len(self.powerup_surfaces)):
            powerup_surface = self.powerup_surfaces[i]
            powerup_description_surface = self.powerup_descrtiptions_surfaces[i]

            self.game_instance.screen.blit(powerup_surface, (x, y + 5))
            self.game_instance.screen.blit(powerup_description_surface, (x + powerup_surface.get_rect().width + 5, y))
            y += powerup_description_surface.get_rect().height + self.item_bottom_padding


class GameplayScene(Scene):
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.game_objects = None
        self.images = None
        self.font = None
        self.score_label = None
        self.score = None

        self.is_active = None
        self.current_level = None

    def load(self):
        self.is_active = True
        self.current_level = 1
        self.images = {
            "player":                    load_asset("assets/player_ship.png"),
            "enemy":                     load_asset("assets/alien_ship.png"),
            "enemy2":                    load_asset("assets/alien_ship2.png"),
            "enemy3":                    load_asset("assets/alien_ship3.png"),
            "enemy_special":             load_asset("assets/alien_ship_special.png"),
            "boss":                      load_asset("assets/boss_ship.png"),
            "projectile":                load_asset("assets/projectile.png"),
            "enemy_projectile":          load_asset("assets/enemy_projectile.png"),
            "enemy_projectile_directed": load_asset("assets/enemy_projectile_directed.png"),
            "enemy_projectile_spread":   load_asset("assets/enemy_projectile_spread.png"),
            "powerup_power":             load_asset("assets/powerup_power.png"),
            "powerup_speed":             load_asset("assets/powerup_speed.png"),
            "powerup_ghost_bullets":     load_asset("assets/powerup_ghost_bullets.png"),
            "powerup_invincibility":     load_asset("assets/powerup_invincibility.png"),
            "player_shield":             load_asset("assets/shield.png", no_alpha=True)  # no per pixel alpha
        }
        self.game_objects = Level1().load(self.game_instance, self.images)
        self.score = 0
        self.font = pygame.font.SysFont("monospace", 20)
        self.score_label = self.font.render("Score: ", 1, (255, 255, 255))

    def unload(self):
        self.is_active = False
        self.game_objects = None
        self.images = None
        self.score = None
        self.font = None
        self.score_label = None
        self.current_level = None
        gc.collect()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game_objects["player"].is_shooting = not self.game_objects["player"].is_shooting
            elif event.key == pygame.K_ESCAPE:
                self.game_instance.is_running = False

            # DEBUG
            elif event.key == pygame.K_n:
                self.next_level()

        elif event.type == pygame.KEYUP:
            pass

    # noinspection PyArgumentList
    def tick(self):
        # call essential methods on every game object
        for game_object in [self.game_objects["player"]] + \
                            self.game_objects["enemies"] + \
                            self.game_objects["player_projectiles"] + \
                            self.game_objects["boss_projectiles"] + \
                            self.game_objects["powerups"]:
            game_object.draw()
            game_object.update()
            game_object.handle_input()

        if not self.is_active:
            return

        # --- drawing ui ---
        x = 20
        y = 20
        item_bottom_padding = 10
        duration_bar_width = 100
        boss_hp_bar_width = 300
        boss_hp_bar_height = 10

        # Score label
        self.game_instance.screen.blit(self.score_label, (x, y))
        number_label = self.font.render(str(self.score), 1, (255, 255, 255))
        self.game_instance.screen.blit(number_label, (x + self.score_label.get_rect().width, y))
        y += number_label.get_rect().height + item_bottom_padding

        # Active powerups list
        for powerup in self.game_objects["player"].active_powerups:
            # draw icon
            icon = self.images[powerup.type.value]
            self.game_instance.screen.blit(icon, (x, y))
            # draw duration bar
            surface = pygame.Surface((duration_bar_width, icon.get_rect().height)).convert_alpha()
            surface.fill((255, 255, 255, 255))
            percent_left = powerup.duration / powerup.start_duration
            surface.fill((0, 0, 0, 0), pygame.Rect(1, 1, duration_bar_width*percent_left-2, icon.get_rect().height-2))
            self.game_instance.screen.blit(surface, (x + icon.get_rect().width + 10, y))

            y += icon.get_rect().height + item_bottom_padding

        # Boss hp bar if on 5th level
        if self.current_level == 5:
            hp_percent = self.game_objects["boss"].health_points / self.game_objects["boss"].max_hp

            # no idea why, sometimes hue was value not in [0, 120]
            hue = 120 * hp_percent
            hue = min(max(0, hue), 120)

            boss_hp_bar_color = pygame.Color("black")
            boss_hp_bar_color.hsla = (hue, 100, 50, 100)
            surface = pygame.Surface((boss_hp_bar_width, boss_hp_bar_height)).convert_alpha()
            surface.fill(boss_hp_bar_color)
            surface.fill(pygame.Color("black"), pygame.Rect(1, 1, boss_hp_bar_width - 2, boss_hp_bar_height - 2))
            x = (self.game_instance.width - surface.get_rect().width) / 2
            surface.fill(boss_hp_bar_color, pygame.Rect(1, 1, boss_hp_bar_width * hp_percent - 2, boss_hp_bar_height-2))
            self.game_instance.screen.blit(surface, (x, 10))

    def next_level(self):
        if self.current_level == 1:
            self.score += 10000
            self.game_objects = Level2().load(self.game_instance, self.images)
        elif self.current_level == 2:
            self.score += 20000
            self.game_objects = Level3().load(self.game_instance, self.images)
        elif self.current_level == 3:
            self.score += 30000
            self.game_objects = Level4().load(self.game_instance, self.images)
        elif self.current_level == 4:
            self.score += 40000
            self.game_objects = Level5().load(self.game_instance, self.images)
        elif self.current_level == 5:
            self.score += 100000
            self.game_instance.endScore = self.score
            self.game_instance.load_scene("winscreen")
            return

        self.current_level += 1

    def check_for_end(self):
        if len(self.game_objects["enemies"]) == 0:
            self.next_level()


class EndScreenScene(Scene):
    def __init__(self, game_instance):
        super().__init__(game_instance)
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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.game_instance.load_scene("menu")
            if event.key == pygame.K_r:
                self.game_instance.load_scene("gameplay")

    def tick(self):
        number_label = self.font.render(str(self.game_instance.end_score), 1, (255, 255, 255))

        x = (self.game_instance.width - (self.label.get_rect().width + number_label.get_rect().width)) / 2
        y = (self.game_instance.height - self.label.get_rect().height) / 2

        self.game_instance.screen.blit(self.label, (x, y))
        self.game_instance.screen.blit(number_label, (x + self.label.get_rect().width, y))

        x = (self.game_instance.width - self.labelTip1.get_rect().width) / 2
        y += self.label.get_rect().height + 20
        self.game_instance.screen.blit(self.labelTip1, (x, y))

        x = (self.game_instance.width - self.labelTip2.get_rect().width) / 2
        y += self.labelTip1.get_rect().height + 20
        self.game_instance.screen.blit(self.labelTip2, (x, y))


class WinScreenScene(Scene):
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.label = None
        self.label_tip1 = None
        self.label_tip2 = None
        self.font = None

    def load(self):
        self.font = pygame.font.SysFont("monospace", 16)
        self.label_tip1 = self.font.render("Nacisnij 'q' aby powrocic do menu glownego", 1, (255, 255, 255))
        self.label_tip2 = self.font.render("Nacisnij 'r' aby zagrac ponownie", 1, (255, 255, 255))
        self.font = pygame.font.SysFont("monospace", 34)
        self.label = self.font.render("Wygrales, twoj wynik to: ", 1, (255, 255, 255))

    def unload(self):
        self.font = None
        self.label = None
        self.label_tip1 = None
        self.label_tip2 = None
        gc.collect()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.game_instance.load_scene("menu")
            if event.key == pygame.K_r:
                self.game_instance.load_scene("gameplay")

    def tick(self):
        number_label = self.font.render(str(self.game_instance.end_score), 1, (255, 255, 255))

        x = (self.game_instance.width - (self.label.get_rect().width + number_label.get_rect().width)) / 2
        y = (self.game_instance.height - self.label.get_rect().height) / 2

        self.game_instance.screen.blit(self.label, (x, y))
        self.game_instance.screen.blit(number_label, (x + self.label.get_rect().width, y))

        x = (self.game_instance.width - self.label_tip1.get_rect().width) / 2
        y += self.label.get_rect().height + 20
        self.game_instance.screen.blit(self.label_tip1, (x, y))

        x = (self.game_instance.width - self.label_tip2.get_rect().width) / 2
        y += self.label_tip1.get_rect().height + 20
        self.game_instance.screen.blit(self.label_tip2, (x, y))

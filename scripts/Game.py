import pygame
from scripts.Scene import MainMenuScene, HelpScreenScene, GameplayScene, EndScreenScene, WinScreenScene, load_asset


class Game:
    def __init__(self):
        self.width = 800
        self.height = 640
        self.fps = 60
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Space Invaders")
        pygame.display.set_icon(load_asset("assets/icon.jpg"))
        self.clock = pygame.time.Clock()
        self.current_scene = None
        self.is_running = True
        self.end_score = 0
        self.scenes = dict(
            menu=MainMenuScene(self),
            help=HelpScreenScene(self),
            gameplay=GameplayScene(self),
            endscreen=EndScreenScene(self),
            winscreen=WinScreenScene(self),
        )

    def run(self):
        self.screen.fill((0, 0, 0))
        self.handle_events()

        self.current_scene.tick()

        self.clock.tick(self.fps)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                    break

            self.current_scene.handle_event(event)

    def load_scene(self, scene_name: str):
        if self.current_scene:
            self.current_scene.unload()
        self.current_scene = self.scenes[scene_name]
        self.current_scene.load()
        return self

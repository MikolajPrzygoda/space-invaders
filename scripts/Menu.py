import pygame


class Menu:
    class Item:
        def __init__(self, item_string: str, scene_name: str, font: pygame.font,
                     text_color=(255, 255, 255), background_color=(0, 0, 0)):
            self.text = item_string
            self.scene_name = scene_name
            self.font = font
            self.text_color = text_color
            self.background_color = background_color

        def get_surface(self):
            surface = self.font.render(self.text, 1, self.text_color, self.background_color)
            surface.set_colorkey(self.background_color)
            return surface

    def __init__(self, game_instance, title: str):
        self.game_instance = game_instance
        self.title = title
        self.items = []
        self.active_item = None

        self.top_padding = 100
        self.title_bottom_padding = 200
        self.item_bottom_padding = 20
        self.item_font_size = 34

        self.title_font = pygame.font.SysFont("monospace", 64)
        self.item_font = pygame.font.SysFont("monospace", self.item_font_size)

    def add_item(self, item_string: str, scene_name: str, text_color=(255, 255, 255), background_color=(0, 0, 0)):
        new_item = self.Item(item_string, scene_name, self.item_font, text_color, background_color)
        self.items.append(new_item)
        if not self.active_item:
            self.set_active_item(new_item)

    def set_active_item(self, item: Item):
        if self.active_item == item:
            return
        elif item in self.items:
            if self.active_item:
                self.active_item.text_color = (255, 255, 255)
            self.active_item = item
            self.active_item.text_color = (255, 140, 140)
        else:
            raise Exception("Set as active item that's not in this menu")

    def set_next_as_active(self):
        current_active_index = self.items.index(self.active_item)
        if current_active_index == len(self.items) - 1:
            return
        else:
            self.set_active_item(self.items[current_active_index + 1])

    def set_previous_as_active(self):
        current_active_index = self.items.index(self.active_item)
        if current_active_index == 0:
            return
        else:
            self.set_active_item(self.items[current_active_index - 1])

    def draw(self):
        title_surface = self.title_font.render(self.title, 1, (255, 255, 255), (0, 0, 0))
        y = self.top_padding
        x = (self.game_instance.width - title_surface.get_rect().width) / 2
        self.game_instance.screen.blit(title_surface, (x, y))
        y += self.title_bottom_padding + title_surface.get_rect().height

        for item in self.items:
            item_surface = item.get_surface()

            item_width, item_height = item_surface.get_rect().size
            x = (self.game_instance.width - item_width) / 2

            self.game_instance.screen.blit(item_surface, (x, y))
            y += self.item_bottom_padding + item_height

    def activate(self):
        scene = self.active_item.scene_name
        valid_scenes = ["help", "gameplay"]
        if scene == "quit":
            self.game_instance.is_running = False
            return
        if scene in valid_scenes:
            self.game_instance.load_scene(scene)
        else:
            print("No action assigned to menu item 'scene_name' field")
            print("Valid strings: ", valid_scenes)

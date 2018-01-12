import pygame


class Menu:
    class Item:
        def __init__(self, itemString: str, sceneName: str, font: pygame.font,
                     textColor=(255, 255, 255), backgroundColor=(0, 0, 0)):
            self.text = itemString
            self.sceneName = sceneName
            self.font = font
            self.textColor = textColor
            self.backgroundColor = backgroundColor

        def getSurface(self):
            return self.font.render(self.text, 1, self.textColor, self.backgroundColor)

    def __init__(self, gameInstance, title: str):
        self.gameInstance = gameInstance
        self.title = title
        self.items = []
        self.activeItem = None

        self.topPadding = 50
        self.titleBottomPadding = 200
        self.itemBottomPadding = 20
        self.itemFontSize = 34

        self.titleFont = pygame.font.SysFont("monospace", 64)
        self.itemFont = pygame.font.SysFont("monospace", self.itemFontSize)

    def addItem(self, itemString: str, sceneName: str, textColor=(255, 255, 255), backgroundColor=(0, 0, 0)):
        newItem = self.Item(itemString, sceneName, self.itemFont, textColor, backgroundColor)
        self.items.append(newItem)
        if not self.activeItem:
            self.setActiveItem(newItem)

    def setActiveItem(self, item: Item):
        if self.activeItem == item:
            return
        elif item in self.items:
            if self.activeItem:
                self.activeItem.textColor = (255, 255, 255)
            self.activeItem = item
            self.activeItem.textColor = (255, 140, 140)
        else:
            raise Exception("Set as active item thats not in this menu")

    def setNextAsActive(self):
        currentActiveIndex = self.items.index(self.activeItem)
        if currentActiveIndex == len(self.items) - 1:
            #last item is already active
            return
        else:
            self.setActiveItem(self.items[currentActiveIndex+1])

    def setPreviousAsActive(self):
        currentActiveIndex = self.items.index(self.activeItem)
        if currentActiveIndex == 0:
            #first item is already active
            return
        else:
            self.setActiveItem(self.items[currentActiveIndex-1])

    def draw(self):
        titleSurface = self.titleFont.render(self.title, 1, (255, 255, 255), (0, 0, 0))
        y = self.topPadding
        x = (self.gameInstance.width - titleSurface.get_rect().width) / 2
        self.gameInstance.screen.blit(titleSurface, (x, y))
        y += self.titleBottomPadding + titleSurface.get_rect().height

        for item in self.items:
            itemSurface = item.getSurface()

            itemW, itemH = itemSurface.get_rect().size
            x = (self.gameInstance.width - itemW)/2

            self.gameInstance.screen.blit(itemSurface, (x, y))
            y += self.itemBottomPadding + itemH

    def activate(self):
        scene = self.activeItem.sceneName
        validScenes = ["help", "level1"]
        if scene == "quit":
            self.gameInstance.isRunning = False
        if scene in validScenes:
            self.gameInstance.setCurrentScene(scene)
        else:
            print("No action assined to menu item 'sceneName' string")
            print("Valid strings: ", validScenes)

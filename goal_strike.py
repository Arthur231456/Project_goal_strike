import pygame
import pytmx
import sys


FPS = 40  # частота обновления экрана

EAST = 0    # направления игрока
NORTH = 1
WEST = 2
SOUTH = 3

TILE_SIZE = 30
W = 1600
H = 900

DATA_DIR = "source"
battle_maps = {"VS_mode": "map/map.tmx", "Cooperative_mode": "map/map2.tmx"}

block1 = pygame.image.load(f"{DATA_DIR}/block1.jpg")
heard_f = pygame.image.load(f"{DATA_DIR}/life1.jpg")
heard_s = pygame.image.load(f"{DATA_DIR}/life2.jpg")
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
map_objects = pygame.sprite.Group()


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    image = image.convert()
    if colorkey == -1:
        image.set_colorkey(image.get_at((0, 0)))
    return image


class Player(pygame.sprite.Sprite):
    red0 = load_image("image02.jpg")
    red1 = load_image("image12.jpg")
    red2 = load_image("image22.jpg")
    red3 = load_image("image32.jpg")
    blue0 = load_image("image01.jpg")
    blue1 = load_image("image11.jpg")
    blue2 = load_image("image21.jpg")
    blue3 = load_image("image31.jpg")

    def __init__(self, color):
        super().__init__(all_sprites, players)
        self.orient = 0
        eval(f"self.image = {color}{self.orient}")
        self.rect = self.image.get_rect().move(TILE_SIZE * 5,
                                               TILE_SIZE * 10)

    def move(self, x, y, orient):
        if self.orient == orient:
            self.rect.x += 10 * x
            self.rect.y += 10 * y
            if not pygame.sprite.spritecollideany(self, map_objects):
                self.rect.x -= 10 * x
                self.rect.y -= 10 * y
        else:
            self.orient = orient

    def shot(self):
        pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pass


class Field(pygame.sprite.Sprite):
    def __init__(self):
        pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    pygame.mixer.init()
    music = pygame.mixer.music
    music.load("source/music.mp3")
    music.play() 
    pygame.init()
    while True:
        pass
    sys.excepthook = except_hook

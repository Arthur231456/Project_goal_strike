import pygame
import pytmx
import sys
import pygame_gui
from random import choice as c

FPS = 40  # частота обновления экрана

EAST = 0  # направления игрока
NORTH = 1
WEST = 2
SOUTH = 3

TILE_SIZE = 30
W = 1600
H = 900

MAPS_DIR = "MAPS"
DATA_DIR = "source"

music_channel = 0
bshot_channel = 1
rshot_channel = 2
MUSIC_VOLUME = 1.0
SHOT_VOLUME = 0.7

SETHEALTHEVENT = pygame.USEREVENT + 1
block1 = pygame.image.load(f"{DATA_DIR}/block1.jpg")
heard_f = pygame.image.load(f"{DATA_DIR}/life1.jpg")
heard_s = pygame.image.load(f"{DATA_DIR}/life2.jpg")
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
map_objects = pygame.sprite.Group()
health_box = pygame.sprite.Group()


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    # image = image.convert()
    if colorkey == -1:
        image.set_colorkey(image.get_at((0, 0)))
    return image


# класс игрока
class Player(pygame.sprite.Sprite):
    red0 = load_image(f"{DATA_DIR}/image02.jpg")
    red1 = load_image(f"{DATA_DIR}/image12.jpg")
    red2 = load_image(f"{DATA_DIR}/image22.jpg")
    red3 = load_image(f"{DATA_DIR}/image32.jpg")
    blue0 = load_image(f"{DATA_DIR}/image01.jpg")
    blue1 = load_image(f"{DATA_DIR}/image11.jpg")
    blue2 = load_image(f"{DATA_DIR}/image21.jpg")
    blue3 = load_image(f"{DATA_DIR}/image31.jpg")

    def __init__(self, color):
        super().__init__(all_sprites, players)
        self.orient = 0
        self.health = 5
        self.color = color
        self.image = eval(f"self.{color}{self.orient}")
        if color == "blue":
            self.orient = 2
            self.image = eval(f"self.{color}{self.orient}")
            self.rect = self.image.get_rect().move(TILE_SIZE,
                                                   TILE_SIZE * 15)

        else:
            self.rect = self.image.get_rect().move(TILE_SIZE * 52,
                                                   TILE_SIZE * 15)

    def move(self, x, y, orient):
        if self.orient == orient:
            self.rect.x += 5 * x
            self.rect.y += 5 * y
            if pygame.sprite.spritecollideany(self, map_objects):
                self.rect.x -= 5 * x
                self.rect.y -= 5 * y
        else:
            self.orient = orient
            self.image = eval(f"self.{self.color}{self.orient}")
        a = pygame.sprite.spritecollideany(self, health_box)
        if a:
            health_box.remove(a)
            all_sprites.remove(a)
            self.health += 1

    def shot(self, mixer):
        snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/shot.wav")
        snd.set_volume(SHOT_VOLUME)
        if self.color == "blue":
            mixer.Channel(bshot_channel).play(snd)
        else:
            mixer.Channel(rshot_channel).play(snd)


# класс пуль
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pass


# класс поля битвы
class Field:
    def __init__(self, map_name):
        super().__init__()
        self.map = pytmx.load_pygame(f"{DATA_DIR}/{MAPS_DIR}/{map_name}.tmx")
        with open(f"{DATA_DIR}/{MAPS_DIR}/{map_name}_floor.txt") as t:
            self.floor = int(t.read())
        self.height = self.map.height
        self.width = self.map.width
        self.set_health((26, 13))
        self.set_health((32, 13))
        self.set_health((32, 17))
        self.set_health((26, 17))
        for x in range(self.width):
            for y in range(1, self.height):
                if self.map.get_tile_gid(x, y, 0) != self.floor:
                    sprite = pygame.sprite.Sprite(map_objects)
                    sprite.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    sprite.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def render(self, display):
        for x in range(self.width):
            for y in range(1, self.height):
                image = self.map.get_tile_image(x, y, 0)
                display.blit(image, (x * TILE_SIZE, y * TILE_SIZE))

    def set_health(self, cords=None):
        health = pygame.sprite.Sprite(health_box, all_sprites)
        health.image = load_image(f"{DATA_DIR}/health1.jpg")
        if cords is not None:
            health.rect = health.image.get_rect().move(cords[0] * TILE_SIZE, cords[1] * TILE_SIZE)
        else:
            health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE,
                                                       c(range(self.height)) * TILE_SIZE)
            while pygame.sprite.spritecollideany(health, map_objects):
                health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE,
                                                           c(range(self.height)) * TILE_SIZE)


def terminate():
    pygame.quit()
    sys.exit()


# запуск игрового процесса
def main():
    pygame.init()
    pygame.time.set_timer(SETHEALTHEVENT, 20000)
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    b = Player("blue")
    r = Player("red")
    field = Field("map")
    mixer = pygame.mixer
    snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/music.wav")
    snd.set_volume(MUSIC_VOLUME)
    mixer.Channel(music_channel).play(snd)
    move_list = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused()
                elif event.key == pygame.K_g:
                    b.shot(mixer)
                elif event.key == pygame.K_p:
                    r.shot(mixer)
                elif event.key == pygame.K_w:
                    move_list.append((0, -1, NORTH, event.key))
                elif event.key == pygame.K_s:
                    move_list.append((0, 1, SOUTH, event.key))
                elif event.key == pygame.K_a:
                    move_list.append((-1, 0, WEST, event.key))
                elif event.key == pygame.K_d:
                    move_list.append((1, 0, EAST, event.key))
                elif event.key == pygame.K_UP:
                    move_list.append((0, -1, NORTH, event.key))
                elif event.key == pygame.K_DOWN:
                    move_list.append((0, 1, SOUTH, event.key))
                elif event.key == pygame.K_LEFT:
                    move_list.append((-1, 0, WEST, event.key))
                elif event.key == pygame.K_RIGHT:
                    move_list.append((1, 0, EAST, event.key))
            elif event.type == SETHEALTHEVENT:
                field.set_health()
            elif event.type == pygame.KEYUP:
                move_list = list(filter(lambda x: x[-1] != event.key, move_list))
        for i in move_list:
            if i[3] in [pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s]:
                b.move(*i[:-1])
            elif i[3] in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                r.move(*i[:-1])
        display.fill((0, 0, 0))
        map_objects.draw(display)
        field.render(display)
        all_sprites.update()
        all_sprites.draw(display)
        pygame.display.update()
        clock.tick(FPS)


# начальный экран
def start_menu():
    pass
    # menu = Menu()


# пауза
def paused():
    pass


if __name__ == "__main__":
    pygame.mixer.init()
    main()

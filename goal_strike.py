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

BAR_HEIGHT = 30
TILE_SIZE = 30
W = 1600
H = 900

MAPS_DIR = "MAPS"
DATA_DIR = "source"
PATTERNS_DIR = "patterns"

music_channel = 0
bshot_channel = 1
rshot_channel = 2
MUSIC_VOLUME = 1.0
SHOT_VOLUME = 0.7

SETHEALTHEVENT = pygame.USEREVENT + 1
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
    red0 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image02.jpg")
    red1 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image12.jpg")
    red2 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image22.jpg")
    red3 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image32.jpg")
    blue0 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image01.jpg")
    blue1 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image11.jpg")
    blue2 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image21.jpg")
    blue3 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image31.jpg")

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
        Bullet(self.rect.x, self.rect.y, self.orient)
        if self.color == "blue":
            mixer.Channel(bshot_channel).play(snd)
        else:
            mixer.Channel(rshot_channel).play(snd)


# класс пуль
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, orient):
        super().__init__(bullets, all_sprites)
        self.orient = orient
        dx = 0
        dy = 0
        self.vect = (0, 0)
        if orient == WEST:
            dx = -10
            dy = 15
            self.vect = (-15, 0)
            self.image = pygame.Surface((5, 2))
        elif orient == NORTH:
            dx = 15
            dy = -10
            self.vect = (0, -15)
            self.image = pygame.Surface((2, 5))
        elif orient == EAST:
            dx = 35
            dy = 15
            self.vect = (15, 0)
            self.image = pygame.Surface((5, 2))
        elif orient == SOUTH:
            dx = 15
            dy = 35
            self.vect = (0, 15)
            self.image = pygame.Surface((2, 5))
        self.image.fill((181, 166, 66))
        self.rect = self.image.get_rect().move(x + dx, y + dy)

    def update(self):
        p = pygame.sprite.spritecollideany(self, players)
        w = pygame.sprite.spritecollideany(self, map_objects)
        if w:
            bullets.remove(self)
            all_sprites.remove(self)
            del self
        elif p:
            p.health -= 1
            bullets.remove(self)
            all_sprites.remove(self)
            del self
        else:
            self.rect.x += self.vect[0]
            self.rect.y += self.vect[1]


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
        left_board = pygame.sprite.Sprite(map_objects)
        left_board.image = pygame.Surface((1, 1))
        left_board.rect = pygame.Rect(1, 1, 1, self.height * TILE_SIZE)
        right_board = pygame.sprite.Sprite(map_objects)
        right_board.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        right_board.rect = pygame.Rect(self.width * TILE_SIZE - 1, 1, 1, self.height * TILE_SIZE)
        top_board = pygame.sprite.Sprite(map_objects)
        top_board.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        top_board.rect = pygame.Rect(1, BAR_HEIGHT - 5, self.width * TILE_SIZE, 1)
        bottom_board = pygame.sprite.Sprite(map_objects)
        bottom_board.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        bottom_board.rect = pygame.Rect(1, self.height * TILE_SIZE - 1, self.width * TILE_SIZE, 1)

    def render(self, display):
        for x in range(self.width):
            for y in range(1, self.height):
                image = self.map.get_tile_image(x, y, 0)
                display.blit(image, (x * TILE_SIZE, y * TILE_SIZE))

    def set_health(self, cords=None):
        health = pygame.sprite.Sprite(health_box, all_sprites)
        health.image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/health1.jpg")
        if cords is not None:
            health.rect = health.image.get_rect().move(cords[0] * TILE_SIZE, cords[1] * TILE_SIZE)
        else:
            health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE,
                                                       c(range(2, self.height)) * TILE_SIZE)
            while pygame.sprite.spritecollideany(health, map_objects):
                health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE,
                                                           c(range(2, self.height)) * TILE_SIZE)


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
            elif event.type == pygame.KEYUP and event.key not in [pygame.K_g, pygame.K_p]:
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

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
MAPS = {1: "map2", 2: "map", 3: "map4"}

with open(f"{DATA_DIR}/{MAPS_DIR}/PLACES.txt") as t:
    PLACES = list(set(eval(f"{t.read()}")))

music_channel = 0
bshot_channel = 1
rshot_channel = 2
bullet_channel = 3
health_channel = 4
capture_channel = 5
MUSIC_VOLUME = 0
SHOT_VOLUME = 0.7
BULLET_VOLUME = 0.3
HEALTH_VOLUME = 0.6
CAPTURE_VOLUME = 0.3

SETHEALTHEVENT = pygame.USEREVENT + 1
SETBULLETEVENT = pygame.USEREVENT + 2
GAMEENDEVENT = pygame.USEREVENT + 3

all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
map_objects = pygame.sprite.Group()
health_box = pygame.sprite.Group()
capture_points = pygame.sprite.Group()
bullets_box = pygame.sprite.Group()


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    if colorkey == -1:
        image = image.convert()
        image.set_colorkey(image.get_at((0, 28)))
    return image


# класс игрока
class Player(pygame.sprite.Sprite):
    red0 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image02.png")
    red1 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image12.png")
    red2 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image22.png")
    red3 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image32.png")
    blue0 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image01.png")
    blue1 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image11.png")
    blue2 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image21.png")
    blue3 = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/image31.png")

    def __init__(self, color, mixer, cord):
        super().__init__(all_sprites, players)
        self.orient = 0
        self.health = 5
        self.bullets = 20
        self.reserve = 60
        self.score = 0
        self.delay = 0
        self.mixer = mixer
        self.color = color
        self.image = eval(f"self.{color}{self.orient}")
        if color == "blue":
            self.orient = 2
            self.image = eval(f"self.{color}{self.orient}")
            self.rect = self.image.get_rect().move(*cord)

        else:
            self.rect = self.image.get_rect().move(*cord)

    def move(self, x, y, orient):
        if self.delay > 0:
            pass
        elif self.orient == orient:
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
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/health0.wav")
            snd.set_volume(SHOT_VOLUME)
            self.mixer.Channel(health_channel).play(snd)
            health_box.remove(a)
            all_sprites.remove(a)
            if self.health < 10:
                self.health += 1
        b = pygame.sprite.spritecollideany(self, bullets_box)
        if b:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/add_bullets.wav")
            snd.set_volume(SHOT_VOLUME)
            self.mixer.Channel(capture_channel).play(snd)
            bullets_box.remove(b)
            all_sprites.remove(b)
            self.reserve += 20
        try:
            pygame.sprite.spritecollideany(self, capture_points).change_color(self)
        except:
            pass

    def shot(self):
        if self.bullets != 0:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/shot.wav")
            snd.set_volume(SHOT_VOLUME)
            Bullet(self.rect.x, self.rect.y, self.orient, self.mixer)
            if self.color == "blue":
                self.mixer.Channel(bshot_channel).play(snd)
            else:
                self.mixer.Channel(rshot_channel).play(snd)
            self.bullets -= 1
        else:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/no_bullets.wav")
            snd.set_volume(SHOT_VOLUME)
            if self.color == "blue":
                self.mixer.Channel(bshot_channel).play(snd)
            else:
                self.mixer.Channel(rshot_channel).play(snd)

    def reload_gun(self):
        if self.reserve != 0 and self.bullets != 20:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/reload.wav")
            snd.set_volume(SHOT_VOLUME)
            if self.color == "blue":
                self.mixer.Channel(bshot_channel).play(snd)
            else:
                self.mixer.Channel(rshot_channel).play(snd)
            self.reserve -= 20
            self.bullets += 20
            if self.reserve < 0:
                self.bullets += self.reserve
                self.reserve -= self.reserve
            if self.bullets > 20:
                self.reserve += self.bullets - 20
                self.bullets = 20

    def update(self):
        if self.delay > 0:
            self.delay -= 1000 // FPS
        self.score = 0
        for i in capture_points:
            if i.image == eval(f"CapturePoints.{self.color}"):
                self.score += 1


# класс пуль
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, orient, mixer):
        super().__init__(bullets, all_sprites)
        self.orient = orient
        self.mixer = mixer
        self.m = int(550 / FPS)
        dx = 0
        dy = 0
        self.vect = (0, 0)
        if orient == WEST:
            dx = -10
            dy = 15
            self.vect = (-self.m, 0)
            self.image = pygame.Surface((5, 2))
        elif orient == NORTH:
            dx = 15
            dy = -10
            self.vect = (0, -self.m)
            self.image = pygame.Surface((2, 5))
        elif orient == EAST:
            dx = 35
            dy = 15
            self.vect = (self.m, 0)
            self.image = pygame.Surface((5, 2))
        elif orient == SOUTH:
            dx = 15
            dy = 35
            self.vect = (0, self.m)
            self.image = pygame.Surface((2, 5))
        self.image.fill((181, 166, 66))
        self.rect = self.image.get_rect().move(x + dx, y + dy)

    def update(self):
        p = pygame.sprite.spritecollideany(self, players)
        w = pygame.sprite.spritecollideany(self, map_objects)
        if w:
            n = c([0, 1, 3])
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/bullet{n}.wav")
            snd.set_volume(BULLET_VOLUME)
            self.mixer.Channel(bullet_channel).play(snd)
            bullets.remove(self)
            all_sprites.remove(self)
            del self
        elif p:
            n = c([0, 1])
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/player_s_shot{n}.wav")
            snd.set_volume(BULLET_VOLUME)
            snd.fadeout(10)
            self.mixer.Channel(bullet_channel).play(snd)
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
        self.name = map_name
        self.map = pytmx.load_pygame(f"{DATA_DIR}/{MAPS_DIR}/{map_name}.tmx")
        with open(f"{DATA_DIR}/{MAPS_DIR}/{map_name}_floor.txt") as t:
            self.floor = eval(t.read())
        self.height = self.map.height
        self.width = self.map.width
        for x in range(self.width):
            for y in range(1, self.height):
                if self.map.get_tile_gid(x, y, 0) not in self.floor:
                    sprite = pygame.sprite.Sprite(map_objects)
                    sprite.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    sprite.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        left_board = pygame.sprite.Sprite(map_objects)
        left_board.image = pygame.Surface((1, 1))
        left_board.rect = pygame.Rect(-TILE_SIZE - 5, 1, TILE_SIZE, self.height * TILE_SIZE)
        right_board = pygame.sprite.Sprite(map_objects)
        right_board.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        right_board.rect = pygame.Rect(W, 1, TILE_SIZE, self.height * TILE_SIZE)
        top_board = pygame.sprite.Sprite(map_objects)
        map_objects.add(top_board)
        top_board.image = pygame.Surface((self.width * TILE_SIZE, 4))
        top_board.image.fill((255, 0, 0))
        top_board.rect = pygame.Rect(0, BAR_HEIGHT - 10, self.width * TILE_SIZE, 10)
        bottom_board = pygame.sprite.Sprite(map_objects)
        bottom_board.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        bottom_board.rect = pygame.Rect(1, self.height * TILE_SIZE - 1, self.width * TILE_SIZE, TILE_SIZE)
        self.set_health((26, 13))
        self.set_health((32, 13))
        self.set_health((32, 17))
        self.set_health((26, 17))
        self.set_bullets((29, 14))
        self.set_bullets((29, 16))

    def render(self, display):
        for x in range(self.width):
            for y in range(1, self.height):
                image = self.map.get_tile_image(x, y, 0)
                display.blit(image, (x * TILE_SIZE, y * TILE_SIZE))

    def set_health(self, cords=None):
        health = pygame.sprite.Sprite(health_box, all_sprites)
        health.image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/health2.jpg")
        if cords is not None and self.name == "map":
            health.rect = health.image.get_rect().move(cords[0] * TILE_SIZE + 1, cords[1] * TILE_SIZE + 1)
        else:
            health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                       c(range(2, self.height)) * TILE_SIZE + 1)
            while pygame.sprite.spritecollideany(health, map_objects)\
                    or pygame.sprite.spritecollideany(health, capture_points):
                health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                           c(range(2, self.height)) * TILE_SIZE + 1)

    def set_bullets(self, cords=None):
        bullet = pygame.sprite.Sprite(bullets_box, all_sprites)
        bullet.image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/bullets.jpg")
        if cords is not None and self.name != "map2":
            bullet.rect = bullet.image.get_rect().move(cords[0] * TILE_SIZE + 1, cords[1] * TILE_SIZE + 1)
        else:
            bullet.rect = bullet.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                       c(range(2, self.height)) * TILE_SIZE + 1)
            while pygame.sprite.spritecollideany(bullet, map_objects)\
                    or pygame.sprite.spritecollideany(bullet, capture_points):
                bullet.rect = bullet.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                           c(range(2, self.height)) * TILE_SIZE + 1)



def terminate():
    pygame.quit()
    sys.exit()


# запуск игрового процесса
def main(map):
    pygame.init()
    pygame.time.set_timer(SETHEALTHEVENT, 20000)
    pygame.time.set_timer(SETHEALTHEVENT, 30000)
    if map == 1:
        pygame.time.set_timer(GAMEENDEVENT, 150000)
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    mixer = pygame.mixer

    field = Field(MAPS[map])
    if map == 1:
        for cord in PLACES:
            CapturePoints(cord[0], cord[1], mixer)
        b = Player("blue", mixer, (TILE_SIZE * 1, TILE_SIZE * 2))
        r = Player("red", mixer, (W - TILE_SIZE * 2, H - TILE_SIZE * 2))

    else:
        b = Player("blue", mixer, (TILE_SIZE, TILE_SIZE * 15))
        r = Player("red", mixer, (TILE_SIZE * 52, TILE_SIZE * 15))
        b.bullets = 1
        b.reserve = 0
        r.bullets = 1
        r.reserve = 0
    snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/music.wav")
    snd.set_volume(MUSIC_VOLUME)
    mixer.Channel(music_channel).play(snd)

    move_list = []
    bar = Top_bar((W, BAR_HEIGHT))
    bar.set_health(b, r)
    display.blit(bar, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused()
                elif event.key == pygame.K_g:
                    b.shot()
                elif event.key == pygame.K_p:
                    r.shot()
                elif event.key == pygame.K_r:
                    b.reload_gun()
                elif event.key == pygame.K_l:
                    r.reload_gun()
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
            elif event.type == SETBULLETEVENT:
                field.set_bullets()
            elif event.type == GAMEENDEVENT:
                end()
                terminate()
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
        if b.health == 0 and map == 1:
            players.remove(b)
            all_sprites.remove(b)
            b = Player("blue", mixer, (TILE_SIZE * 1, TILE_SIZE * 2))
            b.delay = 2000
            bar.set_health(b, r)
        elif r.health == 0 and map == 1:
            players.remove(r)
            all_sprites.remove(r)
            r = Player("red", mixer, (W - TILE_SIZE * 2, H - TILE_SIZE * 2))
            r.delay = 2000
            bar.set_health(b, r)
        all_sprites.update()
        all_sprites.draw(display)
        bar.update(pygame.time.get_ticks(), map)
        display.blit(bar, (0, 0))
        pygame.display.update()
        clock.tick(FPS)


class Top_bar(pygame.Surface):
    def __init__(self, *size):
        super().__init__(*size)
        self.fill((255, 229, 180))
        self.health = []
        self.bullets = []
        self.red = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/life1.png")
        self.blue = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/life2.png")
        self.font1 = pygame.font.Font(None, 30)
        self.font2 = pygame.font.Font(None, 15)

    def update(self, time, mode):
        self.fill((255, 229, 180))
        if mode == 1:
            time = (150000 - time) / 60000
            if time <= 0:
                time = 0
            m = self.font1.render(str(int(time)), 4, (181, 166, 66))
            a = int((time - int(time)) * 60)
            if a < 10:
                a = "0" + str(a)
            else:
                a = str(a)
            s = self.font1.render(a, 4, (181, 166, 66))
            self.blit(m, (W // 2 - 30, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
            self.blit(s, (W // 2 + 15, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
            for i in players:
                if i.color == "blue":
                    t = self.font2.render("score:", 4, (181, 166, 66))
                    s = self.font1.render(str(i.score), 4, (181, 166, 66))
                    self.blit(t, (W // 2 - 240, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
                    self.blit(s, (W // 2 - 200, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
                else:
                    t = self.font2.render("score:", 4, (181, 166, 66))
                    s = self.font1.render(str(i.score), 4, (181, 166, 66))
                    self.blit(t, (W // 2 + 160, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
                    self.blit(s, (W // 2 + 200, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
        for i in self.health:
            if i.color == "blue":
                for j in range(i.health):
                    img = self.blue
                    self.blit(img, (TILE_SIZE * j + 5 * j, BAR_HEIGHT // 2 - TILE_SIZE // 2))
                t = self.font1.render(f"{i.bullets}", 4, (181, 166, 66))
                t1 = self.font2.render(fr" \ {i.reserve}", 4, (181, 166, 66))
                self.blit(t, (400, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
                self.blit(t1, (420, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
            else:
                for j in range(i.health):
                    img = self.red
                    self.blit(img, (W - TILE_SIZE * j - 5 * j - TILE_SIZE, BAR_HEIGHT // 2 - TILE_SIZE // 2))
                t = self.font1.render(f"{i.bullets}", 4, (181, 166, 66))
                t1 = self.font2.render(fr" \ {i.reserve}", 4, (181, 166, 66))
                self.blit(t, (W - TILE_SIZE * i.health - 5 * i.health - TILE_SIZE - 70,
                              BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
                self.blit(t1, (W - TILE_SIZE * i.health - 5 * i.health - TILE_SIZE - 50,
                               BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))

    def set_health(self, *player):
        self.health = []
        for i in range(len(player)):
            self.health.append(player[i])


class CapturePoints(pygame.sprite.Sprite):
    img = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/free_place.jpg")
    red = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/place2.jpg")
    blue = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/place1.jpg")

    def __init__(self, x, y, mixer):
        super().__init__(capture_points, all_sprites)
        self.color = None
        self.image = CapturePoints.img
        self.mixer = mixer
        self.rect = self.image.get_rect().move((x * TILE_SIZE + 1, y * TILE_SIZE + 1))

    def change_color(self, player):
        if self.color != player.color:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/capture_snd.wav")
            snd.set_volume(CAPTURE_VOLUME)
            self.mixer.Channel(capture_channel).play(snd)
        self.color = player.color
        self.image = eval(f"CapturePoints.{player.color}")


# начальный экран
def start_menu():
    pass
    # menu = Menu()


# пауза
def paused():
    pass


# окончание игры, здесь окошко с конечным счетом или надписью имени победителя
# запускается при срабатывании GAMEENDEVENT в основном цикле

def end():
    pass


def welcome_screen():
    pygame.init()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/start.png")
    font = pygame.font.Font(None, 20)
    t = font.render('Press "ESC" to quit', 1, (255, 255, 255))
    t1 = font.render('Press "ENTER" to continue', 1, (255, 255, 255))
    display.blit(image, (0, 0))
    display.blit(t, (1400, 870))
    display.blit(t1, (1400, 850))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_RETURN:
                    main(1)
        pygame.display.update()


if __name__ == "__main__":
    pygame.mixer.init()
    welcome_screen()

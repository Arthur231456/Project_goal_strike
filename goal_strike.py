import pygame
import pytmx
import sys
import pygame_gui
from random import choice as c

FPS = 40  # частота обновления экрана

# направления игрока
EAST = 0
NORTH = 1
WEST = 2
SOUTH = 3

# размеры
BAR_HEIGHT = 30
TILE_SIZE = 30
W = 1600
H = 900

# имена директорий с необходимыми файлами
MAPS_DIR = "MAPS"
DATA_DIR = "source"
PATTERNS_DIR = "patterns"
SETTINGS_FILES = "settings_files"
MAPS = {1: "map2", 2: "map", 3: "map4"}

with open(f"{DATA_DIR}/{MAPS_DIR}/PLACES.txt") as t:
    PLACES = list(set(eval(f"{t.read()}")))

# каналы и громкости звуков
music_channel = 0
bshot_channel = 1
rshot_channel = 2
bullet_channel = 3
health_channel = 4
capture_channel = 5

VOLUMES = {"MUSIC_VOLUME": 0.3,
           "SHOT_VOLUME": 0.7,
           "BULLET_VOLUME": 0.3,
           "HEALTH_VOLUME": 0.6,
           "CAPTURE_VOLUME": 0.3}

with open(f"{DATA_DIR}/{SETTINGS_FILES}/volumes.info") as t:
    a = list(map(lambda x: x.rstrip("\n"), t.readlines()))
    for i in a:
        VOLUMES[i.split(" = ")[0]] = float(i.split(" = ")[1])
control = {'g': pygame.K_g,
           'p': pygame.K_p,
           'r': pygame.K_r,
           'l': pygame.K_l,
           'w': pygame.K_w,
           's': pygame.K_s,
           'a': pygame.K_a,
           'd': pygame.K_d,
           'up': pygame.K_UP,
           'down': pygame.K_DOWN,
           'left': pygame.K_LEFT,
           'right': pygame.K_RIGHT}

# события связанные с механикой игры
SETHEALTHEVENT = pygame.USEREVENT + 1
SETBULLETEVENT = pygame.USEREVENT + 2
GAMEENDEVENT = pygame.USEREVENT + 3

# группы спрайтов объектов игры
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
map_objects = pygame.sprite.Group()
health_box = pygame.sprite.Group()
capture_points = pygame.sprite.Group()
bullets_box = pygame.sprite.Group()
groups = [all_sprites, players, bullets, map_objects, health_box, capture_points, bullets_box]
pygame.init()
pygame.mouse.set_visible(False)
sprites = pygame.sprite.Group()
cursor = pygame.sprite.Sprite(sprites)
cursor.image = pygame.image.load(f"{DATA_DIR}/re/crosshair.png")
cursor.rect = cursor.image.get_rect()
sprites.add(cursor)
cursor.rect.x, cursor.rect.y = 0, 0
if pygame.mouse.get_focused():
    cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()


# функция загрузки изображения
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
            snd.set_volume(VOLUMES["SHOT_VOLUME"])
            self.mixer.Channel(health_channel).play(snd)
            health_box.remove(a)
            all_sprites.remove(a)
            if self.health < 10:
                self.health += 1
        b = pygame.sprite.spritecollideany(self, bullets_box)
        if b:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/add_bullets.wav")
            snd.set_volume(VOLUMES["SHOT_VOLUME"])
            self.mixer.Channel(capture_channel).play(snd)
            bullets_box.remove(b)
            all_sprites.remove(b)
            self.reserve += 20
        try:
            pygame.sprite.spritecollideany(self, capture_points).change_color(self)
        except:
            pass

    def shot(self):  # функция выстрела
        if self.bullets != 0:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/shot.wav")
            snd.set_volume(VOLUMES["SHOT_VOLUME"])
            Bullet(self.rect.x, self.rect.y, self.orient, self.mixer)
            if self.color == "blue":
                self.mixer.Channel(bshot_channel).play(snd)
            else:
                self.mixer.Channel(rshot_channel).play(snd)
            self.bullets -= 1
        else:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/no_bullets.wav")
            snd.set_volume(VOLUMES["SHOT_VOLUME"])
            if self.color == "blue":
                self.mixer.Channel(bshot_channel).play(snd)
            else:
                self.mixer.Channel(rshot_channel).play(snd)

    def reload_gun(self):  # функция перезарядки
        if self.reserve != 0 and self.bullets != 20:
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/reload.wav")
            snd.set_volume(VOLUMES["SHOT_VOLUME"])
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
            snd.set_volume(VOLUMES["BULLET_VOLUME"])
            self.mixer.Channel(bullet_channel).play(snd)
            bullets.remove(self)
            all_sprites.remove(self)
            del self
        elif p:
            n = c([0, 1])
            snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/player_s_shot{n}.wav")
            snd.set_volume(VOLUMES["BULLET_VOLUME"])
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

    def render(self, display):  # функция отрисовки поля
        for x in range(self.width):
            for y in range(1, self.height):
                image = self.map.get_tile_image(x, y, 0)
                display.blit(image, (x * TILE_SIZE, y * TILE_SIZE))

    def set_health(self, cords=None):  # расположение на поле аптечек
        health = pygame.sprite.Sprite(health_box, all_sprites)
        health.image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/health2.jpg")
        if cords is not None and self.name == "map":
            health.rect = health.image.get_rect().move(cords[0] * TILE_SIZE + 1, cords[1] * TILE_SIZE + 1)
        else:
            health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                       c(range(2, self.height)) * TILE_SIZE + 1)
            while pygame.sprite.spritecollideany(health, map_objects) \
                    or pygame.sprite.spritecollideany(health, capture_points):
                health.rect = health.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                           c(range(2, self.height)) * TILE_SIZE + 1)

    def set_bullets(self, cords=None):  # расположение на поле магазинов с патронами
        bullet = pygame.sprite.Sprite(bullets_box, all_sprites)
        bullet.image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/bullets.jpg")
        if cords is not None and self.name != "map2":
            bullet.rect = bullet.image.get_rect().move(cords[0] * TILE_SIZE + 1, cords[1] * TILE_SIZE + 1)
        else:
            bullet.rect = bullet.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                       c(range(2, self.height)) * TILE_SIZE + 1)
            while pygame.sprite.spritecollideany(bullet, map_objects) \
                    or pygame.sprite.spritecollideany(bullet, capture_points):
                bullet.rect = bullet.image.get_rect().move(c(range(10, self.width - 10)) * TILE_SIZE + 1,
                                                           c(range(2, self.height)) * TILE_SIZE + 1)


# функция выхода из программы
def terminate():
    pygame.quit()
    sys.exit()


# запуск игрового процесса
def main(map):
    pygame.init()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    display.blit(load_image(f"{DATA_DIR}/{PATTERNS_DIR}/mode{map}.png"), (0, 0))
    font = pygame.font.Font(None, 20)
    t = font.render('Press "ESC" to quit', 1, (255, 255, 255))
    t1 = font.render('Press "ENTER" to continue', 1, (255, 255, 255))
    display.blit(t, (1400, 870))
    display.blit(t1, (1400, 850))
    pygame.display.update()
    r = True
    while r:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.register_quit(start_menu())
                elif event.key == pygame.K_RETURN:
                    r = False
    tm = 0
    pygame.time.set_timer(SETHEALTHEVENT, 20000)
    pygame.time.set_timer(SETHEALTHEVENT, 30000)
    if map == 1:
        pygame.time.set_timer(GAMEENDEVENT, 150000)
    clock = pygame.time.Clock()

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
    snd.set_volume(VOLUMES["MUSIC_VOLUME"])
    mixer.Channel(music_channel).play(snd)

    move_list = []
    bar = Top_bar((W, BAR_HEIGHT))
    bar.set_health(b, r)
    display.blit(bar, (0, 0))
    running = True
    while running:
        cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()
        cursor.rect.x -= 11
        cursor.rect.y -= 11
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not paused(display, bar, field):
                        for i in groups:
                            i.empty()
                        pygame.mixer.quit()
                        pygame.register_quit(start_menu())
                elif event.key == control['g']:
                    b.shot()
                elif event.key == control['p']:
                    r.shot()
                elif event.key == control['r']:
                    b.reload_gun()
                elif event.key == control['l']:
                    r.reload_gun()
                elif event.key == control['w']:
                    move_list.append((0, -1, NORTH, event.key))
                elif event.key == control['s']:
                    move_list.append((0, 1, SOUTH, event.key))
                elif event.key == control['a']:
                    move_list.append((-1, 0, WEST, event.key))
                elif event.key == control['d']:
                    move_list.append((1, 0, EAST, event.key))
                elif event.key == control['up']:
                    move_list.append((0, -1, NORTH, event.key))
                elif event.key == control['down']:
                    move_list.append((0, 1, SOUTH, event.key))
                elif event.key == control['left']:
                    move_list.append((-1, 0, WEST, event.key))
                elif event.key == control['right']:
                    move_list.append((1, 0, EAST, event.key))
            elif event.type == SETHEALTHEVENT:
                field.set_health()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(W // 2 - 15, W // 2 + 5) and event.pos[1] in range(5, 25):
                    if not paused(display, bar, field):
                        for i in groups:
                            i.empty()
                        pygame.mixer.quit()
                        pygame.register_quit(start_menu())
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
        tm += 1000 / FPS
        bar.update(int(tm), map)
        display.blit(bar, (0, 0))
        sprites.draw(display)
        pygame.display.update()
        clock.tick(FPS)


class Top_bar(pygame.Surface):  # класс верхней информационной панели
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
            self.blit(m, (W // 2 - 35, BAR_HEIGHT // 2 - TILE_SIZE // 2 + 5))
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
        pygame.draw.rect(self, (222, 175, 109), (W // 2 - 15, 5, 20, 20))
        pygame.draw.rect(self, (255, 229, 180), (W // 2 - 11, 8, 4, 14))
        pygame.draw.rect(self, (255, 229, 180), (W // 2 - 3, 8, 4, 14))

    def set_health(self, *player):  # функция отображения здоровья персонажей
        self.health = []
        for i in range(len(player)):
            self.health.append(player[i])


class CapturePoints(pygame.sprite.Sprite):  # класс точек захвата
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
            snd.set_volume(VOLUMES["CAPTURE_VOLUME"])
            self.mixer.Channel(capture_channel).play(snd)
        self.color = player.color
        self.image = eval(f"CapturePoints.{player.color}")


# начальный экран
def start_menu():
    pygame.init()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/start.png")
    display.blit(image, (0, 0))
    manager = pygame_gui.UIManager((W, H), f"{DATA_DIR}/{SETTINGS_FILES}/startmenu.json")
    x = 1100
    y = 300
    btn_settings = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 150, 700), (300, 75)),
                                                text='Настройки', manager=manager)
    end = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 150, 800), (300, 75)),
                                       text='Выход', manager=manager)
    mode1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 300, 500), (300, 75)),
                                         text='Захват точек', manager=manager)
    mode2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 + 10, 500), (300, 75)),
                                         text='Быстрая игра', manager=manager)
    # image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/settings.jpg")
    clock = pygame.time.Clock()
    while True:
        cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()
        cursor.rect.x -= 11
        cursor.rect.y -= 11
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == btn_settings:
                        settings()
                    elif event.ui_element == end:
                        terminate()
                    elif event.ui_element == mode1:
                        main(1)
                    elif event.ui_element == mode2:
                        main(2)
            manager.process_events(event)
        display.fill((0, 0, 0))
        display.blit(image, (0, 0))
        manager.update(time_delta)
        manager.draw_ui(display)
        sprites.draw(display)
        pygame.display.update()


def settings():
    pygame.init()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/start.png")
    display.blit(image, (0, 0))
    manager = pygame_gui.UIManager((W, H), f"{DATA_DIR}/{SETTINGS_FILES}/startmenu.json")
    come_back = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 150, 800), (300, 75)),
                                             text='Назад / Применить', manager=manager)
    control = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 150, 600), (300, 75)),
                                           text='Управление', manager=manager)
    volume = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 150, 500), (300, 75)),
                                          text='Звуки и громкость', manager=manager)
    clock = pygame.time.Clock()
    running = True
    while running:
        cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()
        cursor.rect.x -= 11
        cursor.rect.y -= 11
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == come_back:
                        display.fill((0, 0, 0))
                        display.blit(image, (0, 0))
                        running = False
                        return True
                    elif event.ui_element == control:
                        main(1)
                    elif event.ui_element == volume:
                        Volume()
            manager.process_events(event)
        display.fill((0, 0, 0))
        display.blit(image, (0, 0))
        manager.update(time_delta)
        manager.draw_ui(display)
        sprites.draw(display)
        pygame.display.update()


def Volume():
    global VOLUMES
    pygame.init()
    display = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    image = load_image(f"{DATA_DIR}/{PATTERNS_DIR}/start.png")
    display.blit(image, (0, 0))
    manager = pygame_gui.UIManager((W, H), f"{DATA_DIR}/{SETTINGS_FILES}/startmenu.json")
    come_back = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 750), (300, 75)),
                                             text='Назад / Применить', manager=manager)
    font = pygame.font.Font(None, 46)
    text_music_value = font.render(f"Music volume", True, (255, 229, 180))
    music_value = font.render(f"{VOLUMES['MUSIC_VOLUME']}", True, (255, 229, 180))
    music = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((750, 400), (250, 25)),
                                                   start_value=VOLUMES['MUSIC_VOLUME'] * 100, value_range=(0, 100),
                                                   manager=manager)
    text_shot_volume = font.render(f"Shot volume", True, (255, 229, 180))
    shot_volume = font.render(f"{VOLUMES['SHOT_VOLUME']}", True, (255, 229, 180))
    shot = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((750, 460), (250, 25)),
                                                  start_value=VOLUMES['SHOT_VOLUME'] * 100, value_range=(0, 100), manager=manager)
    text_bullet_volume = font.render(f"Bullet volume", True, (255, 229, 180))
    bullet_volume = font.render(f"{VOLUMES['BULLET_VOLUME']}", True, (255, 229, 180))
    bullet = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((750, 520), (250, 25)),
                                                    start_value=VOLUMES['BULLET_VOLUME'] * 100, value_range=(0, 100),
                                                    manager=manager)
    text_health_volume = font.render(f"Health volume", True, (255, 229, 180))
    health_volume = font.render(f"{VOLUMES['HEALTH_VOLUME']}", True, (255, 229, 180))
    health = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((750, 580), (250, 25)),
                                                    start_value=VOLUMES['HEALTH_VOLUME'] * 100, value_range=(0, 100),
                                                    manager=manager)
    text_capture_volume = font.render(f"Capture volume", True, (255, 229, 180))
    capture_volume = font.render(f"{VOLUMES['CAPTURE_VOLUME']}", True, (255, 229, 180))
    capture = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((750, 640), (250, 25)),
                                                     start_value=VOLUMES['CAPTURE_VOLUME'] * 100, value_range=(0, 100),
                                                     manager=manager)
    clock = pygame.time.Clock()
    running = True
    while running:
        cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()
        cursor.rect.x -= 11
        cursor.rect.y -= 11
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == come_back:
                        display.fill((0, 0, 0))
                        display.blit(image, (0, 0))
                        running = False
                        return True
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == music:
                        VOLUMES['MUSIC_VOLUME'] = music.get_current_value() // 1 / 100
                        music_value = font.render(f"{VOLUMES['MUSIC_VOLUME']}", True, (255, 229, 180))
                    elif event.ui_element == shot:
                        VOLUMES['SHOT_VOLUME'] = shot.get_current_value() // 1 / 100
                        shot_volume = font.render(f"{VOLUMES['SHOT_VOLUME']}", True, (255, 229, 180))
                    elif event.ui_element == bullet:
                        VOLUMES['BULLET_VOLUME'] = bullet.get_current_value() // 1 / 100
                        bullet_volume = font.render(f"{VOLUMES['BULLET_VOLUME']}", True, (255, 229, 180))
                    elif event.ui_element == health:
                        VOLUMES['HEALTH_VOLUME'] = health.get_current_value() // 1 / 100
                        health_volume = font.render(f"{VOLUMES['HEALTH_VOLUME']}", True, (255, 229, 180))
                    elif event.ui_element == capture:
                        VOLUMES['CAPTURE_VOLUME'] = capture.get_current_value() // 1 / 100
                        capture_volume = font.render(f"{VOLUMES['CAPTURE_VOLUME']}", True, (255, 229, 180))
                    with open(f"{DATA_DIR}/{SETTINGS_FILES}/volumes.info", "w") as t:
                        for vol in VOLUMES:
                            t.write(f"{vol} = {VOLUMES[vol]}\n")
            manager.process_events(event)
        display.blit(image, (0, 0))
        display.blit(text_music_value, (480, 400))
        display.blit(text_capture_volume, (480, 640))
        display.blit(text_health_volume, (480, 580))
        display.blit(text_bullet_volume, (480, 520))
        display.blit(text_shot_volume, (480, 460))
        display.blit(music_value, (1010, 400))
        display.blit(capture_volume, (1010, 640))
        display.blit(health_volume, (1010, 580))
        display.blit(bullet_volume, (1010, 520))
        display.blit(shot_volume, (1010, 460))
        manager.update(time_delta)
        manager.draw_ui(display)
        sprites.draw(display)
        pygame.display.update()


# пауза
def paused(display, bar, field):
    clock = pygame.time.Clock()
    background = pygame.Surface((320, 180))
    background.fill((255, 229, 180))
    time_delta = clock.tick(FPS) / 1000.0
    manager = pygame_gui.UIManager((W, H), f"{DATA_DIR}/{SETTINGS_FILES}/set.json")
    resume_game = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 140, H // 2 - 40), (280, 30)),
                                               text='Возобновить игру', manager=manager)
    exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 140, H // 2 + 40), (280, 30)),
                                               text='Завершить игру', manager=manager)
    open_settings = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((W // 2 - 140, H // 2), (280, 30)),
                                                 text='Настройки', manager=manager)
    running = True
    pygame.mouse.set_pos(W // 2 - 160, H // 2 - 90)
    while running:
        if pygame.mouse.get_pos()[0] in range(W // 2 - 160, W // 2 + 160)\
                and pygame.mouse.get_pos()[1] in range(H // 2 - 90, H // 2 + 90):
            cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()
            cursor.rect.x -= 11
            cursor.rect.y -= 11
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == resume_game:
                        running = False
                        return True
                    elif event.ui_element == exit_button:
                        running = False
                        return False
                    elif event.ui_element == open_settings:
                        settings()
                        map_objects.draw(display)
                        field.render(display)
                        all_sprites.update()
                        all_sprites.draw(display)
                        bar.update(pygame.time.get_ticks(), map)
                        display.blit(bar, (0, 0))
                        pygame.display.update()
                        snd = pygame.mixer.Sound(f"{DATA_DIR}/sounds/music.wav")
                        snd.set_volume(VOLUMES["MUSIC_VOLUME"])
                        pygame.mixer.Channel(music_channel).play(snd)
            manager.process_events(event)
        if pygame.mouse.get_pos()[0] < W // 2 - 149:
            pygame.mouse.set_pos(W // 2 - 149, pygame.mouse.get_pos()[1])
        if pygame.mouse.get_pos()[0] > W // 2 + 149:
            pygame.mouse.set_pos(W // 2 + 149, pygame.mouse.get_pos()[1])
        if pygame.mouse.get_pos()[1] < H // 2 - 79:
            pygame.mouse.set_pos(pygame.mouse.get_pos()[0], H // 2 - 79)
        if pygame.mouse.get_pos()[1] > H // 2 + 79:
            pygame.mouse.set_pos(pygame.mouse.get_pos()[0], H // 2 + 79)
        display.fill((0, 0, 0))
        map_objects.draw(display)
        field.render(display)
        all_sprites.update()
        all_sprites.draw(display)
        display.blit(bar, (0, 0))
        display.blit(background, (W // 2 - 160, H // 2 - 90))
        manager.draw_ui(display)
        manager.update(time_delta)
        sprites.draw(display)
        pygame.display.update()


# окончание игры, здесь окошко с конечным счетом или надписью имени победителя
# запускается при срабатывании GAMEENDEVENT в основном цикле

def end():
    pass


# функция заставки
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
        cursor.rect.x, cursor.rect.y = pygame.mouse.get_pos()
        cursor.rect.x -= 11
        cursor.rect.y -= 11
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_RETURN:
                    start_menu()
        display.fill((0, 0, 0))
        display.blit(image, (0, 0))
        display.blit(t, (1400, 870))
        display.blit(t1, (1400, 850))
        sprites.draw(display)
        pygame.display.update()


if __name__ == "__main__":
    pygame.mixer.init()
    welcome_screen()

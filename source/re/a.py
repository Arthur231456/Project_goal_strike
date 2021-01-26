import pygame
import pytmx
import sys


FPS = 40  # частота обновления экрана

EAST = 0    # направления игрока
NORTH = 1
WEST = 2
SOUTH = 3

W = 1600
H = 900

block1 = pygame.image.load(f"source/block1.jpg")
heard_f = pygame.image.load(f"source/life1.jpg")
heard_s = pygame.image.load(f"source/life2.jpg")

MAPS_DIR = "source/map"
battle_map = "map.tmx"


class Field:
    def __init__(self, map):
        self.execution = True
        self.game_over = False
        self.SIZE = (W, H)  # размеры игрового поля
        self.bullets = []
        pygame.init()
        self.display = pygame.display.set_mode(self.SIZE, pygame.DOUBLEBUF | pygame.FULLSCREEN)  # создание окна игры
        self.display.fill((128, 128, 128))
        self.clock = pygame.time.Clock()
        self.blocks = [(block1, (210, 210)), (block1, (210, 180)), (block1, (210, 150)), (block1, (210, 120))]
        self.map = pytmx.load_pygame(f"{MAPS_DIR}/{map}")
        pygame.display.update()

    def start_game(self):
        x, y = 0, 0
        x1, y1 = 0, 0
        try:
            self.player = Player(self.display, 2)
            self.player2 = Player(self.display, 1)
            while self.execution:  # основной цикл
                self.clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  # кнопка для выхода из игры
                            try:
                                self.exit()
                            except:
                                pass

                        # далее события связанные с обработкой действий игрока

                        if event.key == pygame.K_w:
                            if self.player.orient == NORTH:
                                y = -5
                            self.player.orient = NORTH
                        elif event.key == pygame.K_s:
                            if self.player.orient == SOUTH:
                                y = 5
                            self.player.orient = SOUTH
                        elif event.key == pygame.K_a:
                            if self.player.orient == WEST:
                                x = -5
                            self.player.orient = WEST
                        elif event.key == pygame.K_d:
                            if self.player.orient == EAST:
                                x = 5
                            self.player.orient = EAST
                        elif event.key == pygame.K_SPACE:
                            pygame.event.clear()
                        elif event.key == pygame.K_g:
                            self.bullets.append(Bullet(self, self.display,
                                                       self.player.cords,
                                                       self.player.orient))
                        elif event.key == pygame.K_UP:
                            if self.player2.orient == NORTH:
                                y1 = -5
                            self.player2.orient = NORTH
                        elif event.key == pygame.K_DOWN:
                            if self.player2.orient == SOUTH:
                                y1 = 5
                            self.player2.orient = SOUTH
                        elif event.key == pygame.K_LEFT:
                            if self.player2.orient == WEST:
                                x1 = -5
                            self.player2.orient = WEST
                        elif event.key == pygame.K_RIGHT:
                            if self.player2.orient == EAST:
                                x1 = 5
                            self.player2.orient = EAST
                        elif event.key == pygame.K_SPACE:
                            pygame.event.clear()
                        elif event.key == pygame.K_SLASH:
                            self.bullets.append(Bullet(self, self.display,
                                                       self.player2.cords,
                                                       self.player2.orient))
                        elif event.key == pygame.K_p:
                            ev = True
                            while ev:
                                if pygame.event.wait().type == pygame.KEYDOWN:
                                    if pygame.event.wait().key == pygame.K_p:
                                        ev = False
                    elif event.type == pygame.KEYUP:
                        if event.key in [pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s]:
                            x, y = 0, 0
                        elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            x1, y1 = 0, 0
                self.display.fill((0, 0, 0))

                # отрисовка персонажей

                self.render()

                try:
                    if self.player.check_wall(self, x, y):
                        x, y = 0, 0
                    self.bullets = list(filter(lambda p: p not in self.player.check_shot(self.bullets),
                                          self.bullets))
                    self.player.render(x, y)
                except:
                    pass
                try:
                    if self.player2.check_wall(self, x1, y1):
                        x1, y1 = 0, 0
                    self.bullets = list(filter(lambda p: p not in self.player2.check_shot(self.bullets),
                                               self.bullets))
                    self.player2.render(x1, y1)
                except:
                    pass

                # отрисовка пуль

                b = []
                for i in self.bullets:
                    if i.on_field():
                        i.move()
                        b.append(i)
                self.bullets = b.copy()
                pygame.display.update()
            pygame.quit()

        except Exception as e:
            print(e, 1)

    def render(self):
        for i in range(self.map.width):
            for j in range(self.map.height):
                image = self.map.get_tile_image(i, j, 0)
                self.display.blit(image, (i * 30, j * 30))

    def exit(self):
        pygame.quit()


class Player:       # класс игрока
    def __init__(self, display, character):
        self.cords = [W // 2, H // 2]
        self.orient = WEST
        self.fire_on = False
        self.display = display
        self.character = character
        self.health = 5

    def check_wall(self, field, x, y):
        for i in field.blocks:
            a = list(range(self.cords[0] + x, self.cords[0] + x + 30)) + list(range(i[1][0], i[1][0] + 30))
            b = list(range(self.cords[1] + y, self.cords[1] + y + 30)) + list(range(i[1][1], i[1][1] + 30))
            if len(a) != len(list(set(a))) and len(b) != len(list(set(b))):
                return True

    def render(self, x, y):

        # проверка, не вышел ли игрок за край поля

        if self.cords[1] + y >= H - 30:
            self.cords[1] = H - 30
            y = 0
        elif self.cords[1] + y < 30:
            self.cords[1] = 30
            y = 0
        if self.cords[0] + x >= W - 30:
            self.cords[0] = W - 30
            x = 0
        elif self.cords[0] < 0:
            self.cords[0] = 0
            x = 0

        # отрисовка персонажа в соответствии его ориентации

        self.cords[0] += x
        self.cords[1] += y
        self.display.blit(load_image(f"source/image{self.orient}{self.character}.jpg", -1),
                          (self.cords[0], self.cords[1]))
        life_bar = pygame.Surface((175, 30))
        if self.character == 1:
            for i in range(self.health):
                life_bar.blit(heard_f, (30 * i + 5, 0))
            self.display.blit(life_bar, (W - 175, 0))
        else:
            for i in range(self.health):
                life_bar.blit(heard_s, (30 * i + 5, 0))
            self.display.blit(life_bar, (0, 0))

    def check_shot(self, bullets):
        in_body = []
        for i in bullets:
            if i.size[0] in range(self.cords[0], self.cords[0] + 30) \
                    and i.size[1] in range(self.cords[1], self.cords[1] + 30):
                self.health -= 1
                in_body.append(i)
        return in_body


class Enemy:       # класс врага
    def __init__(self):
        self.cords = [W // 2, H // 2]
        self.orient = WEST
        self.fire_on = False

    def check_wall(self, field, x, y):
        for i in field.blocks:
            a = list(range(self.cords[0] + x, self.cords[0] + x + 30)) + list(range(i[1][0], i[1][0] + 30))
            b = list(range(self.cords[1] + y, self.cords[1] + y + 30)) + list(range(i[1][1], i[1][1] + 30))
            if len(a) != len(list(set(a))) and len(b) != len(list(set(b))):
                return True


class Bullet:
    def __init__(self,field, display, cords, orient):
        self.surf = display
        self.size = []
        self.field = field
        if orient == WEST:
            self.dx = -250 // FPS
            self.dy = 0
            self.size = [cords[0] - 1, cords[1] + 14, 5, 2]
        elif orient == EAST:
            self.dx = 250 // FPS
            self.dy = 0
            self.size = [cords[0] + 30, cords[1] + 14, 5, 2]
        elif orient == NORTH:
            self.dy = -250 // FPS
            self.dx = 0
            self.size = [cords[0] + 15, cords[1] - 1, 2, 5]
        elif orient == SOUTH:
            self.dy = 250 // FPS
            self.dx = 0
            self.size = [cords[0] + 15, cords[1] + 30, 2, 5]
        pygame.draw.rect(display, (181, 166, 66), self.size)
        pygame.display.flip()

    def move(self):
        try:
            self.size = [self.size[0] + self.dx, self.size[1] + self.dy, self.size[2], self.size[3]]
            pygame.draw.rect(self.surf, (181, 166, 66), self.size)
        except Exception as e:
            print(e)

    def on_field(self):
        for i in self.field.blocks:
            if self.size[0] in range(i[1][0], i[1][0] + 30) \
                    and self.size[1] in range(i[1][1], i[1][1] + 30):
                return False
        if 0 < self.size[0] < 1600 and 0 < self.size[1] < 900:
            return True
        else:
            return False


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    image = image.convert()
    if colorkey == -1:
        image.set_colorkey(image.get_at((3, 2)))

    return image


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    ex = Field(battle_map)
    pygame.mixer.init()
    music = pygame.mixer.music
    music.load("source/music.mp3")
    music.play()
    ex.start_game()
    sys.excepthook = except_hook

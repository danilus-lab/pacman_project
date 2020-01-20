import pygame
import sys
import os

pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
screen.fill(pygame.Color("black"))
pygame.display.set_caption('PACMAN INFOMAT EDITION')

sounds = {'click': pygame.mixer.Sound('sounds/ckick.wav'),
          'eat': pygame.mixer.Sound('sounds/waka_waka.wav'),
          'ghost': pygame.mixer.Sound('sounds/ghosts.wav'),
          'death': pygame.mixer.Sound('sounds/death.wav'),
          'cherry': pygame.mixer.Sound('sounds/eating_cherry.wav')}

MUSIC_K = 0
GAMEPLAY_K = 0
CLICK_K = 0
number = 1
SCORE = 0

MUSIC_SOUNDS = True
GAMEPLAY_SOUNDS = True
CLICK_SOUNDS = True

MODE = 'arrows'

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
food = pygame.sprite.Group()
cursor_sprites = pygame.sprite.Group()
back_sprites = pygame.sprite.Group()
pause_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
bots = pygame.sprite.Group()
life = pygame.sprite.Group()
cherries = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def write_max_score(score):
    fname = open('max_score.txt', mode='w', encoding='utf-8')
    fname.write(str(score))


def convert_image(image, x, y):
    image1 = pygame.transform.scale(image, (x, y))
    return image1


tile_images = {'1': load_image('1.png'), '2': load_image('2.png'), '3': load_image('3.png'),
               '4': load_image('4.png'), '5': load_image('5.png'),
               '6': load_image('6.png'), '7': load_image('7.png'), '8': load_image('8.png'),
               '9': load_image('9.png'), '0': load_image('0.png'),
               'dot': load_image('dot.png'), 'empty': load_image('empty.png'),
               'pacman': load_image('pacman_right.png'), 'a': load_image('a.png'),
               'b': load_image('b.png'),
               'c': load_image('c.png'), 'v': convert_image(load_image('cherry.png'), 30, 30)}
tile_width = tile_height = 30


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type != 'dot':
            tile_group.add(self)


class Food(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(food)
        self.image = tile_images['dot']
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y
        self.radius = 5

    def update(self, pacman):
        if pygame.sprite.collide_circle(self, pacman):
            self.kill()
            pacman.score += 20
            pacman.score_for_level += 20
            new_sprite = pygame.sprite.Sprite(food)
            new_sprite.image = tile_images['empty']
            new_sprite.rect = new_sprite.image.get_rect()
            new_sprite.rect = new_sprite.rect.move(tile_width * self.x, tile_height * self.y)
            if GAMEPLAY_SOUNDS:
                sounds['eat'].set_volume(0.02)
                sounds['eat'].play(0)


class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(cursor_sprites)
        self.image = convert_image(load_image('pakman_cursor.png', -1), 20, 20)
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(0)

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y
        cursor_sprites.update()
        cursor_sprites.draw(screen)


class BackButton(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(back_sprites)
        self.image = convert_image(load_image('back_button.png', -1), 100, 50)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check(self, event):
        x, y = event.pos[0], event.pos[1]
        return self.rect.x <= x <= self.rect.x + 100 and self.rect.y <= y <= self.rect.y + 50

    def place(self):
        back_sprites.update()
        back_sprites.draw(screen)


class PauseButton(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(back_sprites)
        self.image = load_image('pause_button.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check(self, event):
        x, y = event.pos[0], event.pos[1]
        return self.rect.x <= x <= self.rect.x + 60 and self.rect.y <= y <= self.rect.y + 60

    def place(self):
        pause_sprites.update()
        pause_sprites.draw(screen)


class Cherry(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(cherries)
        self.image = tile_images['v']
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y
        self.radius = 5

    def update(self, pacman):
        if pygame.sprite.collide_circle(self, pacman):
            self.kill()
            pacman.score += 100
            pacman.score_for_level += 100
            new_sprite = pygame.sprite.Sprite(cherries)
            new_sprite.image = tile_images['empty']
            new_sprite.rect = new_sprite.image.get_rect()
            new_sprite.rect = new_sprite.rect.move(tile_width * self.x, tile_height * self.y)
            if GAMEPLAY_SOUNDS:
                sounds['cherry'].set_volume(0.02)
                sounds['cherry'].play(0)


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Pacman(pygame.sprite.Sprite):
    def __init__(self, x, y, score, number_level):
        super().__init__(player_group, all_sprites)
        self.image = convert_image(load_image('pacman_right.png'), 30, 30)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.radius = 2
        self.k_food = 0
        self.k_cherries = 0
        self.k_ghosts = 0
        self.score_for_level = 0
        self.number_level = number_level
        if self.number_level == 1:
            self.k_food = 143
            self.k_cherries = 7
        elif self.number_level == 2:
            self.k_food = 142
            self.k_cherries = 8
        elif self.number_level == 3:
            self.k_food = 198
            self.k_cherries = 6
        elif self.number_level == 4:
            self.k_food = 198
            self.k_cherries = 6
        elif self.number_level == 5:
            self.k_food = 219
            self.k_cherries = 6
        elif self.number_level == 6:
            self.k_food = 219
            self.k_cherries = 6
        elif self.number_level == 7:
            self.k_food = 218
            self.k_cherries = 9
        elif self.number_level == 8:
            self.k_food = 219
            self.k_cherries = 8
        self.x = x
        self.y = y
        self.score = score
        self.moveUp = self.moveLeft = self.moveDown = self.moveRight = False

        self.right = [load_image('pacman_right.png'), load_image('pacman_right_a.png'),
                      load_image('pacman_right_b.png')]

        self.left = [load_image('pacman_left.png'), load_image('pacman_left_a.png'),
                     load_image('pacman_left_b.png')]

        self.up = [load_image('pacman_up.png'), load_image('pacman_up_a.png'),
                   load_image('pacman_up_b.png')]

        self.down = [load_image('pacman_down.png'), load_image('pacman_down_a.png'),
                     load_image('pacman_down_b.png')]

        self.jizn = pygame.sprite.Sprite(life)
        self.jizn.image = convert_image(load_image('life.png', -1), 100, 100)
        self.jizn.rect = self.jizn.image.get_rect()
        self.jizn.rect.x = 650
        self.jizn.rect.y = 250

        self.lives = 3
        self.i = 0

    def move(self, event):
        if MODE == 'arrows':
            if event.key == pygame.K_UP:
                self.image = convert_image(load_image('pacman_up.png'), 30, 30)
                self.moveUp = True
                self.moveLeft = self.moveDown = self.moveRight = False
            elif event.key == pygame.K_DOWN:
                self.image = convert_image(load_image('pacman_down.png'), 30, 30)
                self.moveDown = True
                self.moveUp = self.moveLeft = self.moveRight = False
            elif event.key == pygame.K_RIGHT:
                self.image = convert_image(self.right[self.i % 3], 30, 30)
                self.moveRight = True
                self.moveUp = self.moveLeft = self.moveDown = False
            elif event.key == pygame.K_LEFT:
                self.image = convert_image(load_image('pacman_left.png', -1), 30, 30)
                self.moveLeft = True
                self.moveUp = self.moveDown = self.moveRight = False
        else:
            if event.key == pygame.K_w:
                self.image = convert_image(load_image('pacman_up.png'), 30, 30)
                self.moveUp = True
                self.moveLeft = self.moveDown = self.moveRight = False
            elif event.key == pygame.K_s:
                self.image = convert_image(load_image('pacman_down.png'), 30, 30)
                self.moveDown = True
                self.moveUp = self.moveLeft = self.moveRight = False
            elif event.key == pygame.K_d:
                self.image = convert_image(load_image('pacman_right.png'), 30, 30)
                self.moveRight = True
                self.moveUp = self.moveLeft = self.moveDown = False
            elif event.key == pygame.K_a:
                self.image = convert_image(load_image('pacman_left.png', -1), 30, 30)
                self.moveLeft = True
                self.moveUp = self.moveDown = self.moveRight = False

    def return_to_the_start(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def check(self):
        if pygame.sprite.spritecollideany(self, bots):
            self.lives -= 1
            self.score -= 300
            self.score_for_level -= 300
            self.k_ghosts += 1
            if GAMEPLAY_SOUNDS:
                sounds['ghost'].set_volume(0.05)
                sounds['ghost'].play()
            self.return_to_the_start()

    def update(self):
        self.i += 1
        if self.moveRight:
            if self.i % 10 == 0:
                self.image = convert_image(self.right[self.i % 3], 30, 30)
            self.rect = self.rect.move(1, 0)
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.rect = self.rect.move(-1, 0)
        elif self.moveLeft:
            self.rect = self.rect.move(-1, 0)
            if self.i % 10 == 0:
                self.image = convert_image(self.left[self.i % 3], 30, 30)
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.rect = self.rect.move(1, 0)
        elif self.moveDown:
            self.rect = self.rect.move(0, 1)
            if self.i % 10 == 0:
                self.image = convert_image(self.down[self.i % 3], 30, 30)
            if pygame.sprite.spritecollideany(self, horizontal_borders):
                self.rect = self.rect.move(0, -1)
        elif self.moveUp:
            self.rect = self.rect.move(0, -1)
            if self.i % 10 == 0:
                self.image = convert_image(self.up[self.i % 3], 30, 30)
            if pygame.sprite.spritecollideany(self, horizontal_borders):
                self.rect = self.rect.move(0, 1)

    def if_max_score(self):
        return self.score_for_level == 20 * self.k_food + \
               100 * self.k_cherries - 300 * self.k_ghosts

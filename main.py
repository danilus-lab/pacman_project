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

    def otrisovka(self):
        font = pygame.font.SysFont("comicsansms", 30)
        screen.fill((0, 0, 0))
        score = font.render('SCORE: ' + str(self.score), 1,
                            (255, 165, 0))
        screen.blit(score, (600, 10))
        font = pygame.font.SysFont("comicsansms", 60)
        lives = font.render('x ' + str(self.lives), 1,
                            (255, 165, 0))
        screen.blit(lives, (750, 260))

    def end_of_game(self):
        if self.lives == 0:
            return True


class Bots_a(pygame.sprite.Sprite):
    def __init__(self, x, y, bucva, number):
        super().__init__(bots, all_sprites)
        self.image = convert_image(load_image(bucva + '.png'), 30, 30)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.spid_x = 1
        self.spid_y = 1
        self.number = number
        self.radius = 10
        self.r_l = True
        self.u_d = True
        self.moveUp = self.moveLeft = self.moveDown = self.moveRight = True

    def update(self):
        level = load_level('level' + str(self.number) + '.txt')
        if self.r_l:
            self.rect.x += self.spid_x
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.spid_x *= (-1)
                self.rect.x += self.spid_x
                self.r_l = False
                self.u_d = True
        if self.u_d:
            self.rect.y += self.spid_y
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.spid_y *= (-1)
                self.rect.y += self.spid_y
                self.u_d = False
                self.r_l = True


class Bots_b(pygame.sprite.Sprite):
    def __init__(self, x, y, bucva, number):
        super().__init__(bots, all_sprites)
        self.image = convert_image(load_image(bucva + '.png'), 30, 30)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.spid_x = 1
        self.spid_y = 1
        self.number = number
        self.r_l = True
        self.u_d = True
        self.moveUp = self.moveLeft = self.moveDown = self.moveRight = True

    def update(self):
        level = load_level('level' + str(self.number) + '.txt')
        if self.r_l:
            self.rect.x += self.spid_x
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.spid_x *= (-1)
                self.rect.x += self.spid_x
                self.r_l = False
                self.u_d = True
        if self.u_d:
            self.rect.y += self.spid_y
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.spid_y *= (-1)
                self.rect.y += self.spid_y
                self.u_d = False
                self.r_l = True


class Bots_c(pygame.sprite.Sprite):
    def __init__(self, x, y, bucva, number):
        super().__init__(bots, all_sprites)
        self.image = convert_image(load_image(bucva + '.png'), 30, 30)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.spid_x = 1
        self.spid_y = 1
        self.number = number
        self.r_l = True
        self.u_d = True
        self.moveUp = self.moveLeft = self.moveDown = self.moveRight = True

    def update(self):
        level = load_level('level' + str(self.number) + '.txt')
        if self.r_l:
            self.rect.x += self.spid_x
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.spid_x *= (-1)
                self.rect.x += self.spid_x
                self.r_l = False
                self.u_d = True
        if self.u_d:
            self.rect.y += self.spid_y
            if pygame.sprite.spritecollideany(self, vertical_borders):
                self.spid_y *= (-1)
                self.rect.y += self.spid_y
                self.u_d = False
                self.r_l = True


def terminate():
    pygame.quit()
    sys.exit()


def click_sound():
    if CLICK_SOUNDS:
        sounds['click'].set_volume(0.02)
        sounds['click'].play()


cursor = Cursor()


def start_screen():
    global number
    pygame.display.set_caption('PACMAN INFOMAT EDITION')
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    if MUSIC_SOUNDS:
        pygame.mixer.music.load('music/start_screen_music.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)
    x, y = pygame.mouse.get_pos()
    running = True
    all_sprites = pygame.sprite.Group()
    arrow = pygame.sprite.Sprite(all_sprites)
    arrow.image = load_image('arrow.png', -1)
    arrow.rect = arrow.image.get_rect()
    arrow.rect.x = 20
    arrow.rect.y = 30

    nadpis = pygame.sprite.Sprite(all_sprites)
    nadpis.image = load_image('nadpis.png', -1)
    nadpis.rect = nadpis.image.get_rect()
    nadpis.rect.x = 125
    nadpis.rect.y = 2
    pacman_start_screen = pygame.sprite.Sprite(all_sprites)
    pacman_start_screen.image = convert_image(load_image('main_menu_pic.jpg', -1), 600, 160)
    pacman_start_screen.rect = pacman_start_screen.image.get_rect()
    pacman_start_screen.rect.x = 10
    pacman_start_screen.rect.y = 400
    while running:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("comicsansms", 50)
        menu = font.render("PLAY", 1, (255, 165, 0))
        text_x = width // 2 - menu.get_width() // 2
        text_y = height // 2 - menu.get_height() // 2 - 250
        screen.blit(menu, (text_x, text_y + 100))
        settings = font.render("SETTINGS", 1, (255, 165, 0))
        screen.blit(settings, (text_x, text_y + 200))
        exit = font.render("EXIT", 1, (255, 165, 0))
        screen.blit(exit, (text_x, text_y + 300))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if arrow.rect.y < 150:
                        arrow.rect.y += 100
                elif event.key == pygame.K_UP:
                    if arrow.rect.y > 105:
                        arrow.rect.y -= 100
                elif event.key == pygame.K_RETURN:
                    if arrow.rect.y == 30:
                        pygame.mixer.music.stop()
                        main()
                        break
                    elif arrow.rect.y == 130:
                        pygame.mixer.music.stop()
                        nast()
                    elif arrow.rect.y == 230:
                        pygame.mixer.music.stop()
                        terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_sound()
                if 216 < event.pos[0] < 354 and 130 < event.pos[1] < 177:
                    pygame.mixer.music.stop()
                    main()
                    break
                elif 238 < event.pos[0] < 517 and 228 < event.pos[1] < 284:
                    pygame.mixer.music.stop()
                    nast()
                    break
                elif 238 < event.pos[0] < 378 and 327 < event.pos[1] < 378:
                    pygame.mixer.music.stop()
                    terminate()
            elif event.type == pygame.MOUSEMOTION:
                if 226 < event.pos[0] < 354 and 130 < event.pos[1] < 177:
                    arrow.rect.y = 30
                elif 238 < event.pos[0] < 517 and 228 < event.pos[1] < 284:
                    arrow.rect.y = 130
                elif 238 < event.pos[0] < 378 and 327 < event.pos[1] < 378:
                    arrow.rect.y = 230
        all_sprites.update()
        all_sprites.draw(screen)
        x, y = pygame.mouse.get_pos()
        cursor.move(x, y)
        pygame.display.flip()


def nast():
    pygame.display.set_caption('SETTINGS')
    running = True
    settings_sprites = pygame.sprite.Group()
    picture = pygame.sprite.Sprite(settings_sprites)
    picture.image = load_image('settings_screen.jpg', -1)
    picture.rect = picture.image.get_rect()
    picture.rect.x = 0
    picture.rect.y = 350
    back = BackButton(20, 30)
    all_sprites = pygame.sprite.Group()
    underline = pygame.sprite.Sprite(all_sprites)
    underline.image = convert_image(load_image('underline.png'), 500, 60)
    underline.rect = underline.image.get_rect()
    underline.rect.x = 10
    underline.rect.y = 160
    while running:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("comicsansms", 50)
        settings = font.render("SETTINGS", 1, (255, 165, 0))
        text_x = width // 2 - settings.get_width() // 2
        text_y = height // 2 - settings.get_height() // 2 - 250
        screen.blit(settings, (text_x, text_y))
        font_small = pygame.font.SysFont("comicsansms", 60)
        controlling_text = font_small.render("CONTROLLING", 1, (255, 255, 0))
        controlling_text_x = 20
        controlling_text_y = 100
        screen.blit(controlling_text, (controlling_text_x, controlling_text_y))
        volume_text = font_small.render("VOLUME", 1, (255, 255, 0))
        volume_text_x = 20
        volume_text_y = 250
        screen.blit(volume_text, (volume_text_x, volume_text_y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back.kill()
                    start_screen()
                elif event.key == pygame.K_DOWN:
                    if underline.rect.y < 250:
                        underline.rect.y += 150
                elif event.key == pygame.K_UP:
                    if underline.rect.y > 250:
                        underline.rect.y -= 150
                elif event.key == pygame.K_RETURN:
                    if underline.rect.y == 160:
                        back.kill()
                        nast_of_controlling()
                    else:
                        back.kill()
                        nast_of_volume()
            elif event.type == pygame.MOUSEMOTION:
                x = event.pos[0]
                y = event.pos[1]
                if 17 <= x <= 474 and 116 <= y <= 177:
                    underline.rect.y = 160
                elif 18 <= x <= 275 and 272 <= y <= 322:
                    underline.rect.y = 310
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_sound()
                x = event.pos[0]
                y = event.pos[1]
                if back.check(event):
                    back.kill()
                    start_screen()
                if 17 <= x <= 474 and 116 <= y <= 177:
                    back.kill()
                    nast_of_controlling()
                elif 18 <= x <= 275 and 272 <= y <= 322:
                    back.kill()
                    nast_of_volume()
        x, y = pygame.mouse.get_pos()
        cursor.move(x, y)
        all_sprites.update()
        all_sprites.draw(screen)
        settings_sprites.update()
        settings_sprites.draw(screen)
        back.place()
        cursor_sprites.update()
        cursor_sprites.draw(screen)
        pygame.display.flip()


def nast_of_controlling():
    global MODE, number
    pygame.display.set_caption('CONTROL SETTINGS')
    running = True
    back = BackButton(10, 30)
    all_sprites = pygame.sprite.Group()
    wasd = pygame.sprite.Sprite(all_sprites)
    wasd.image = load_image('wasd_buttons.png')
    wasd.rect = wasd.image.get_rect()
    wasd.rect.x = 30
    wasd.rect.y = 120
    arrows_keys = pygame.sprite.Sprite(all_sprites)
    arrows_keys.image = load_image('arrows_buttons.png')
    arrows_keys.rect = arrows_keys.image.get_rect()
    arrows_keys.rect.x = 30
    arrows_keys.rect.y = 350
    confirming_sprites = pygame.sprite.Group()
    galka = pygame.sprite.Sprite(confirming_sprites)
    galka.image = convert_image(load_image('galka.png'), 200, 200)
    galka.rect = galka.image.get_rect()
    kvadrat = pygame.sprite.Sprite(confirming_sprites)
    kvadrat.image = convert_image(load_image('kvadrat.png'), 200, 200)
    kvadrat.rect = kvadrat.image.get_rect()
    if MODE == 'arrows':
        galka.rect.x = 350
        galka.rect.y = 350
        kvadrat.rect.x = 350
        kvadrat.rect.y = 120
    else:
        galka.rect.x = 350
        galka.rect.y = 120
        kvadrat.rect.x = 350
        kvadrat.rect.y = 350
    while running:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("comicsansms", 50)
        settings = font.render("CONTROLLING", 1, (255, 165, 0))
        text_x = width // 2 - settings.get_width() // 2
        text_y = height // 2 - settings.get_height() // 2 - 250
        screen.blit(settings, (text_x, text_y))
        font_small = pygame.font.SysFont("comicsansms", 25)
        instruction = font_small.render("Сhoose convenient control buttons", 1, (255, 165, 0))
        instruction_x = 20
        instruction_y = 85
        screen.blit(instruction, (instruction_x, instruction_y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back.kill()
                    nast()
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    coords = galka.rect.x, galka.rect.y
                    galka.rect.x, galka.rect.y = kvadrat.rect.x, kvadrat.rect.y
                    kvadrat.rect.x, kvadrat.rect.y = coords
                    if galka.rect.y == 120:
                        MODE = 'wasd'
                    else:
                        MODE = 'arrows'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_sound()
                x = event.pos[0]
                y = event.pos[1]
                if back.check(event):
                    back.kill()
                    nast()
                if 350 < x < 540 and 120 < y < 295:
                    galka.rect.y = 120
                    kvadrat.rect.y = 350
                    MODE = 'wasd'
                elif 350 < x < 540 and 350 < y < 535:
                    galka.rect.y = 350
                    kvadrat.rect.y = 120
                    MODE = 'arrows'
        all_sprites.update()
        all_sprites.draw(screen)
        confirming_sprites.update()
        confirming_sprites.draw(screen)
        back.place()
        x, y = pygame.mouse.get_pos()
        cursor.move(x, y)
        pygame.display.flip()


def nast_of_volume():
    global MUSIC_SOUNDS, MUSIC_K, CLICK_K, CLICK_SOUNDS, GAMEPLAY_K, GAMEPLAY_SOUNDS, number
    pygame.display.set_caption('VOLUME SETTINGS')
    back = BackButton(20, 30)
    running = True
    buttons_group = pygame.sprite.Group()
    music_sprite = pygame.sprite.Sprite(buttons_group)
    if MUSIC_SOUNDS:
        music_sprite.image = convert_image(load_image('vkl.png'), 100, 100)
    else:
        music_sprite.image = convert_image(load_image('vikl.png'), 100, 100)
    music_sprite.rect = music_sprite.image.get_rect()
    music_sprite.rect.x = 350
    music_sprite.rect.y = 90
    gameplay_sprite = pygame.sprite.Sprite(buttons_group)
    if GAMEPLAY_SOUNDS:
        gameplay_sprite.image = convert_image(load_image('vkl.png'), 100, 100)
    else:
        gameplay_sprite.image = convert_image(load_image('vikl.png'), 100, 100)
    gameplay_sprite.rect = gameplay_sprite.image.get_rect()
    gameplay_sprite.rect.x = 400
    gameplay_sprite.rect.y = 240
    click_sprite = pygame.sprite.Sprite(buttons_group)
    if CLICK_SOUNDS:
        click_sprite.image = convert_image(load_image('vkl.png'), 100, 100)
    else:
        click_sprite.image = convert_image(load_image('vikl.png'), 100, 100)
    click_sprite.rect = click_sprite.image.get_rect()
    click_sprite.rect.x = 350
    click_sprite.rect.y = 390
    while running:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("comicsansms", 50)
        volume = font.render("VOLUME", 1, (255, 165, 0))
        text_x = width // 2 - volume.get_width() // 2
        text_y = height // 2 - volume.get_height() // 2 - 250
        screen.blit(volume, (text_x, text_y))
        font_small = pygame.font.SysFont("comicsansms", 60)
        music_text = font_small.render("MUSIC:", 1, (255, 255, 0))
        music_text_x = 20
        music_text_y = 100
        screen.blit(music_text, (music_text_x, music_text_y))
        gameplay_text = font_small.render("GAMEPLAY:", 1, (255, 255, 0))
        gameplay_text_x = 20
        gameplay_text_y = 250
        screen.blit(gameplay_text, (gameplay_text_x, gameplay_text_y))
        click_sounds_text = font_small.render("CLICKS:", 1, (255, 255, 0))
        click_sounds_text_x = 20
        click_sounds_text_y = 400
        screen.blit(click_sounds_text, (click_sounds_text_x, click_sounds_text_y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back.kill()
                    nast()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                if 346 <= x <= 453 and 94 <= y <= 185:
                    MUSIC_K += 1
                    if MUSIC_K % 2 != 0:
                        music_sprite.image = convert_image(load_image('vikl.png'), 100, 100)
                        MUSIC_SOUNDS = False
                    else:
                        music_sprite.image = convert_image(load_image('vkl.png'), 100, 100)
                        MUSIC_SOUNDS = True
                elif 397 <= x <= 504 and 242 <= y <= 337:
                    GAMEPLAY_K += 1
                    if GAMEPLAY_K % 2 != 0:
                        gameplay_sprite.image = convert_image(load_image('vikl.png'), 100, 100)
                        GAMEPLAY_SOUNDS = False
                    else:
                        gameplay_sprite.image = convert_image(load_image('vkl.png'), 100, 100)
                        GAMEPLAY_SOUNDS = True
                elif 346 <= x <= 453 and 392 <= y <= 491:
                    CLICK_K += 1
                    if CLICK_K % 2 != 0:
                        click_sprite.image = convert_image(load_image('vikl.png'), 100, 100)
                        CLICK_SOUNDS = False
                    else:
                        click_sprite.image = convert_image(load_image('vkl.png'), 100, 100)
                        CLICK_SOUNDS = True
                click_sound()
                if back.check(event):
                    back.kill()
                    nast()
        buttons_group.update()
        buttons_group.draw(screen)
        back.place()
        x, y = pygame.mouse.get_pos()
        cursor.move(x, y)
        pygame.display.flip()


def load_level(fullname):
    filename = "levels/" + fullname
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def draw_border(x, y):
    Border(30 * x + 5, 30 * y + 5, 30 * (x + 1) - 5, 30 * y + 5)
    Border(30 * x + 5, 30 * (y + 1) - 5, 30 * (x + 1) - 5, 30 * (y + 1) - 5)
    Border(30 * x + 5, 30 * y + 5, 30 * x + 5, 30 * (y + 1) - 5)
    Border(30 * (x + 1) - 5, 30 * y + 5, 30 * (x + 1) - 5, 30 * (y + 1) - 5)


def find_border_cords(level):
    for y in range(len(level)):
        for x in range(len(level)):
            if level[y][x] == '0':
                draw_border(x, y)
            elif level[y][x] == '1':
                draw_border(x, y)
            elif level[y][x] == '2':
                draw_border(x, y)
            elif level[y][x] == '3':
                draw_border(x, y)
            elif level[y][x] == '4':
                draw_border(x, y)
            elif level[y][x] == '5':
                draw_border(x, y)
            elif level[y][x] == '6':
                draw_border(x, y)
            elif level[y][x] == '7':
                draw_border(x, y)
            elif level[y][x] == '8':
                draw_border(x, y)
            elif level[y][x] == '9':
                draw_border(x, y)


def generator_level(level):
    global number
    print(number)
    ghosts = []
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level)):
            if level[y][x] == '0':
                Tile('0', x, y)
            elif level[y][x] == '1':
                Tile('1', x, y)
            elif level[y][x] == '@':
                new_player = Pacman(x * 30, y * 30, SCORE, number)
            elif level[y][x] == '2':
                Tile('2', x, y)
            elif level[y][x] == '3':
                Tile('3', x, y)
            elif level[y][x] == '4':
                Tile('4', x, y)
            elif level[y][x] == '5':
                Tile('5', x, y)
            elif level[y][x] == '6':
                Tile('6', x, y)
            elif level[y][x] == '7':
                Tile('7', x, y)
            elif level[y][x] == '8':
                Tile('8', x, y)
            elif level[y][x] == '9':
                Tile('9', x, y)
            elif level[y][x] == '*':
                Food(x, y)
            elif level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == 'a':
                Food(x, y)
                ghost = Bots_a(x * 30, y * 30, 'a', number)
                ghosts.append(ghost)
            elif level[y][x] == 'b':
                Food(x, y)
                ghost = Bots_b(x * 30, y * 30, 'b', number)
                ghosts.append(ghost)
            elif level[y][x] == 'c':
                Food(x, y)
                ghost = Bots_c(x * 30, y * 30, 'c', number)
                ghosts.append(ghost)
            elif level[y][x] == 'v':
                Tile('empty', x, y)
                Cherry(x, y)
    return new_player, x, y, ghosts

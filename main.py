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

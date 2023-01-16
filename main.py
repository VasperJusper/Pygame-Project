import pygame
import sys
import os
import math


TILE_SIZE = 128
BRUSH = 'h'
tile_images = {
    '0': pygame.image.load(os.path.join('Data', 'Blank.png')),
    'furnace': pygame.image.load(os.path.join('Data', 'furnace.png')),
    'drill': pygame.image.load(os.path.join('Data', 'drill.png')),
    'heater': pygame.image.load(os.path.join('Data', 'heater.png'))
}
tile_codes = {
    '0': '0',
    'f': 'furnace',
    'd': 'drill',
    'h': 'heater'
}
for e in tile_images:
    if e != '0':
        tile_images[e] = pygame.transform.scale(tile_images[e], (TILE_SIZE, TILE_SIZE))


class Crosshair(pygame.sprite.Sprite):
    def __init__(self, picture):
        super().__init__()
        self.image = pygame.image.load(os.path.join('Data', picture))
        self.image = pygame.transform.scale(self.image, (75, 75))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(pos_x * TILE_SIZE, pos_y * TILE_SIZE)
        self.tile_type = tile_type
        self.recharge = 0
        self.x = pos_x
        self.y = pos_y

    def update(self):
        global resources
        self.tile_type = tile_codes[level[self.y - offset_y][self.x - offset_x]]
        self.image = tile_images[self.tile_type]
        if self.tile_type == 'heater':
            resources['elec'] += 0.1
        elif self.tile_type == 'drill':
            if self.recharge == 0:
                if resources['elec'] >= 10:
                    resources['raw_ore'] += 1
                    resources['elec'] -= 10
                    self.recharge = 100
            else:
                self.recharge -= 1
        elif self.tile_type == 'furnace':
            if self.recharge == 0:
                if resources['elec'] >= 20 and resources['raw_ore'] >= 2:
                    resources['smelt_ore'] += 1
                    resources['raw_ore'] -= 2
                    resources['elec'] -= 20
                    self.recharge = 200
            else:
                self.recharge -= 1


pygame.init()
pygame.font.init()
test_font = pygame.font.SysFont('Comic Sans MS', 30)
clock = pygame.time.Clock()
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
background = pygame.image.load(os.path.join('Data', 'BGlava.png'))
background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
pygame.mouse.set_visible(False)

level_width = 10
level_height = 6
offset_x = 2
offset_y = 2


# resources
resources = {
    'raw_ore': 0,
    'elec': 0,
    'smelt_ore': 0
}

level = [['0'] * level_width for _ in range(level_height)]

crosshair = Crosshair("cursor.png")

ui_group = pygame.sprite.Group()
ui_group.add(crosshair)
tiles_group = pygame.sprite.Group()


def create_level(width, height):
    for y in range(offset_y, height + offset_y):
        for x in range(offset_x, width + offset_x):
            tile = level[y - offset_y][x - offset_x]
            Tile(tile_codes[tile], x, y)


def get_click(pos):
    cell = (pos[0] - offset_x * TILE_SIZE) // TILE_SIZE, (pos[1] - offset_y * TILE_SIZE) // TILE_SIZE
    if 0 <= cell[0] <= level_width - 1 and 0 <= cell[1] <= level_height - 1:
        level[cell[1]][cell[0]] = BRUSH


create_level(level_width, level_height)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            get_click(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.key.key_code('e'):
                BRUSH = '0'
            elif event.key == pygame.key.key_code('1'):
                BRUSH = 'h'
            elif event.key == pygame.key.key_code('2'):
                BRUSH = 'd'
            elif event.key == pygame.key.key_code('3'):
                BRUSH = 'f'
    screen.blit(background, (0, 0))
    tiles_group.draw(screen)
    ui_group.draw(screen)
    ui_group.update()
    tiles_group.update()
    screen.blit(test_font.render(f'Electricity: {math.floor(resources["elec"])}', False, (255, 255, 255)), (100, 1000))
    screen.blit(test_font.render(f'Raw ore: {resources["raw_ore"]}', False, (255, 255, 255)), (600, 1000))
    screen.blit(test_font.render(f'Smelted ore: {resources["smelt_ore"]}', False, (255, 255, 255)), (1500, 1000))
    pygame.display.update()

import pygame
import sys
import os
import math

pygame.init()
pygame.font.init()
test_font = pygame.font.SysFont('couriernew', 30)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width = screen.get_width()
screen_height = screen.get_height()
background = pygame.image.load(os.path.join('Data', 'BGlava.png'))
background = pygame.transform.scale(background, (screen_width, screen_height))
pygame.mouse.set_visible(False)
TILE_SIZE = (screen_width + screen_height) // 25
BRUSH = 'h'
GAMEMODE = 'building'
tile_images = {
    '0': pygame.image.load(os.path.join('Data', 'tile_sprites', 'Blank.png')),
    'furnace': pygame.image.load(os.path.join('Data', 'tile_sprites', 'furnace.png')),
    'drill': pygame.image.load(os.path.join('Data', 'tile_sprites', 'drill.png')),
    'heater': pygame.image.load(os.path.join('Data', 'tile_sprites', 'heater.png')),
    'turret': pygame.image.load(os.path.join('Data', 'turret_sprites', '1.png'))
}
tile_codes = {
    '0': '0',
    'f': 'furnace',
    'd': 'drill',
    'h': 'heater',
    't': 'turret'
}
modes = ['building', 'turret control']
for e in tile_images:
    if e != '0':
        tile_images[e] = pygame.transform.scale(tile_images[e], (TILE_SIZE, TILE_SIZE))

turret_sprites = []

debug = 0

for i in range(1, 65):
    t_frame = pygame.transform.scale(pygame.image.load(os.path.join('Data', 'turret_sprites', f'{i}.png')),
                                     (TILE_SIZE * 2, TILE_SIZE * 2))
    turret_sprites.append(t_frame)


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
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(pos_x * TILE_SIZE, pos_y * TILE_SIZE)
        self.recharge = 0
        self.angle = 0
        self.x = pos_x
        self.y = pos_y

    def update(self):
        global resources
        self.tile_type = tile_codes[level[self.y - offset_y][self.x - offset_x]]
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
        if self.tile_type == 'turret':
            self.handle_turret()
            self.rect = self.image.get_rect().move(self.x * TILE_SIZE - TILE_SIZE // 2,
                                                   self.y * TILE_SIZE - TILE_SIZE // 2)
        else:
            self.image = tile_images[self.tile_type]
            self.rect = self.image.get_rect().move(self.x * TILE_SIZE, self.y * TILE_SIZE)

    def handle_turret(self):
        global debug
        if GAMEMODE == 'turret control':
            mouse_x, mouse_y = crosshair.rect.center
            rel_x, rel_y = mouse_x - self.rect.center[0] - TILE_SIZE // 2, mouse_y - self.rect.center[1] - TILE_SIZE // 2
            self.angle = math.degrees(math.atan2(rel_y, rel_x)) - 270
            if self.angle < 0:
                self.angle += 360
            if self.angle < 0:
                self.angle += 360
            debug = self.angle
        self.image = turret_sprites[int(self.angle / 5.625)]


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
    if GAMEMODE == 'building':
        if 0 <= cell[0] <= level_width - 1 and 0 <= cell[1] <= level_height - 1:
            level[cell[1]][cell[0]] = BRUSH


def ui_draw():
    txt_y = screen_height - 100
    screen.blit(test_font.render(f'Electricity: {math.floor(resources["elec"])}', False, (255, 255, 255)), (100, txt_y))
    screen.blit(test_font.render(f'Gamemode: {GAMEMODE}', False, (255, 255, 255)), (100, 100))
    screen.blit(test_font.render(f'Raw ore: {resources["raw_ore"]}', False, (255, 255, 255)), (600, txt_y))
    screen.blit(test_font.render(f'Smelted ore: {resources["smelt_ore"]}', False, (255, 255, 255)), (1100, txt_y))
    screen.blit(test_font.render(f'FPS: {int(clock.get_fps())}', False, (255, 255, 255)), (1600, txt_y))
    screen.blit(test_font.render(f'Debug: {debug}', False, (255, 255, 255)), (2100, txt_y))


create_level(level_width, level_height)
m = 0

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
            elif event.key == pygame.key.key_code('4'):
                BRUSH = 't'
            elif event.key == pygame.key.key_code('m'):
                m = (m + 1) % len(modes)
                GAMEMODE = modes[m]
    screen.blit(background, (0, 0))
    tiles_group.draw(screen)
    ui_group.draw(screen)
    ui_group.update()
    ui_draw()
    tiles_group.update()
    pygame.display.update()
    clock.tick(60)

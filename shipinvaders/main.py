import ntpath
import os
import random
import pygame as pg

HEIGHT = 700
WIDTH = 580
FPS = 40
updates = 0
PAUSE = False
healthpoints = 100
BLACK = 0, 0, 0
WHITE = 255, 255, 255
GRAY = 128, 128, 128
LIGHT_GRAY = 200, 200, 200
DARK_GRAY = 90, 90, 90
LIGHT = 254, 254, 254
CIAN = 0, 165, 190
GREEN = 0, 0, 255
last_time = 0

pg.init()
pg.mixer.init()
window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Ship Invaders')
clc = pg.time.Clock()
game_folder = os.path.dirname(__file__)
images_folder = os.path.join(game_folder, 'images')
sounds_folder = os.path.join(game_folder, 'sounds')
player_img = pg.image.load(os.path.join(images_folder, 'Player.jpg')).convert()
boat_img = pg.image.load(os.path.join(images_folder, 'peasant_boat1.jpg')).convert(), \
           pg.image.load(os.path.join(images_folder, 'peasant_boat2.jpg')).convert(),\
           pg.image.load(os.path.join(images_folder, 'peasant_boat2.jpg')).convert()
background = pg.image.load(os.path.join(images_folder, 'background.jpg')).convert()

pg.mixer.music.load(os.path.join(sounds_folder, 'map.wav'))
pg.mixer.music.set_volume(0.8)
shoot_sound = pg.mixer.Sound(os.path.join(sounds_folder, 'Laser_Shoot.wav'))
shoot_sound.set_volume(0.6)
exp_sound = pg.mixer.Sound(os.path.join(sounds_folder, 'Explosion.wav'))
exp_sound.set_volume(0.6)
hit_sound = pg.mixer.Sound(os.path.join(sounds_folder, 'Hit_Hurt.wav'))
hit_sound.set_volume(0.6)

background_rect = background.get_rect()

font_name = pg.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    pg.draw.rect(surf, (1, 241, 1), fill_rect)
    pg.draw.rect(surf, GREEN, outline_rect, 2)


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey((254, 254, 254))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shoot_delay = 500
        self.last_shot = pg.time.get_ticks()

    def update(self):
        self.speedx = 0
        if self.rect.right > WIDTH:
            self.rect.centerx -= 8
        if self.rect.top < 0:
            self.rect.centery += 8
        if self.rect.left < 0:
            self.rect.centerx += 8
        if self.rect.bottom > HEIGHT:
            self.rect.centerx -= 8
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.speedx = -4
        if keystate[pg.K_RIGHT]:
            self.speedx = 4
        self.rect.x += self.speedx

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
            self.last_shot = pg.time.get_ticks()


class PeasantBoat(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.flp = random.randint(0, 1)
        self.image = random.choice(boat_img)
        if not self.flp:
            self.image = pg.transform.flip(self.image, True, False)
        self.image.set_colorkey(LIGHT)
        self.rect = self.image.get_rect()

        if self.flp:
            self.rect.x = random.randrange(-500, -400)
            self.speedx = random.randint(1, 3)

        else:
            self.rect.x = random.randrange(WIDTH + 500, WIDTH + 600)
            self.speedx = random.randint(-3, -1)

        self.rect.y = random.randrange(100, HEIGHT - 400)

    def update(self):
        self.rect.x += self.speedx


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        self.last_update = pg.time.get_ticks()
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((20, 20))
        self.image.set_colorkey(LIGHT)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pg.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


def newmob(en):
    m = en()
    all_sprites.add(m)
    enemy.add(m)


bullets = pg.sprite.Group()
all_sprites = pg.sprite.Group()
enemy = pg.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(4):
    newmob(PeasantBoat)
score = 0
pg.mixer.music.play(loops=-1)

running = True
while running:
    updates += 1
    clc.tick(FPS)
    all_sprites.update()
    updates += 1
    if PAUSE:
        running = False
    hits = pg.sprite.spritecollide(player, enemy, True)
    mhits = pg.sprite.groupcollide(enemy, bullets, True, True)
    for hit in mhits:
        exp_sound.play()
        score += 1
        newmob(PeasantBoat)
    if hits:
        healthpoints -= 20
        newmob(PeasantBoat)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                player.shoot()

    window.fill(CIAN)
    time = updates//1000
    if time != last_time and time < 13:
        last_time = time
        newmob(PeasantBoat)
    window.blit(background, background_rect)
    all_sprites.draw(window)
    if healthpoints <= 0:
        draw_text(window, 'GAME OVER', 100, WIDTH/2, 100)
        FPS = 1
        player.kill()
        PAUSE = False
    draw_text(window, str(score), 50, 40, 10)
    draw_health_bar(window, 5, 5, healthpoints)
    pg.display.flip()
pg.quit()

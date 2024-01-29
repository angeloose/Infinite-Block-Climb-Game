import random
import sys
import time

import pygame
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2  # 2 for two-dimensional

HEIGHT = 500
WIDTH = 400
ACC = 1     # acceleration/player horiontal movement speed
FRIC = -0.12  # friction
FPS = 60

FramesPerSec = pygame.time.Clock()  # tick/update rate

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))   # screen
pygame.display.set_caption('Game')  # name of application when opened


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30))    # object size
        self.surf.fill((128, 255, 40))          # color
        self.rect = self.surf.get_rect()

        self.pos = vec((WIDTH / 2, HEIGHT - 30))   # starting pos
        self.vel = vec(0, 0)        # movement variables thru use of vectors
        self.acc = vec(0, 0)

        self.jumping = False        # determines if player is currently jumping
        self.score = 0

    def move(self):
        self.acc = vec(0, 0.5)    # resets x horizontal accel to 0, y vertical gravity 0.5

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_a]:   # moving left
            self.acc.x = -ACC
        if pressed_keys[K_d]:   # moving right
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC     # equation for acceleration due to friction and velocity
        self.vel += self.acc                  # velocity increases or decreases depending on acceleration
        self.pos += self.vel + 0.5 * self.acc   # movement changes due to the acceleration and velocity

        if self.pos.x > WIDTH:      # if player goes off screen to the right, warp to the left
            self.pos.x = 0
        if self.pos.x < 0:          # if player goes off screen to the left, warp to the right
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < 3:  # cancel jump after player reaches a certain vertical speed
                self.vel.y = -3

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        # collision function that returns list of True or False, (sprite, group of sprites, delete sprite if touching)
        if self.vel.y > 0:
            if hits:
                if self.pos.y < hits[0].rect.bottom:    # player landing doesnt register until above platform
                    if hits[0].point is True:           # if player lands on a platform, update score by 1
                        hits[0].point = False
                        self.score += 1
                    self.vel.y = 0
                    self.pos.y = hits[0].rect.top + 1
                    self.jumping = False


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((random.randint(50, 100), 12))   # platform width
        self.surf.fill((0, 255, 0))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH-10), random.randint(0, HEIGHT - 30)))
        # center= is start pos

        self.point = True    # when true, player gets a point for landing on platform

        if P1.score < 50:    # speed of platforms changes depending on score
            self.speed = random.randint(-1, 1)  # movement speed will be left, right, or none at all
        elif P1.score < 100:
            self. speed = random.randint(-2, 2)  # speed increases in difficulty when score is above 50
        elif P1.score > 100:
            self.speed = random.randint(-3, 3)
        self.moving = True

    def move(self):
        if self.moving is True:
            self.rect.move_ip(self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:  # warps platform to other side if goes off screen
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH


def plat_gen():    # platform generation
    while len(platforms) < 9:
        width = random.randrange(50, 100)                           # platform width
        C = True
        tries = 0

        while C and tries != 60:
            p = Platform()
            p.rect.center = (random.randrange(0, WIDTH - width), random.randrange(-100, 0))
            # moves platform right above screen so it is hidden at first
            C = check(p, platforms)     # check if platforms are touching
            tries += 1

        platforms.add(p)
        all_sprites.add(p)



def check(platform, groupies):  # return True if platforms are too close, False if generation successful
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 50) and (abs(platform.rect.bottom - entity.rect.top) < 50):
            # checks surrounding area around newly generated plaforms, return True if so
                return True
        pass #change!!!

# initializing sprites and objects ----------------------------------------------------------------------------

P1 = Player()           
PT1 = Platform()                        # platform 1 gets special code since it is the bottom
PT1.surf = pygame.Surface((WIDTH, 20))
PT1.surf.fill((255, 0,0))
PT1.rect = PT1.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

PT1.moving = False  # initial red platform does not move and does not give points
PT1.point = False



all_sprites = pygame.sprite.Group()     # list of all sprites
all_sprites.add(PT1)
all_sprites.add(P1)

platforms = pygame.sprite.Group()       # list of all platforms
platforms.add(PT1)

for x in range(random.randint(6, 7)):  # initially generates platforms
    C = True
    pl = Platform()
    while C:
        pl = Platform()
        C = check(pl, platforms)
    platforms.add(pl)
    all_sprites.add(pl)

# game loop =====================================================================================================

while True:            # special event types (quitting, certain player actions, etc.)
    P1.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:    # KEYDOWN represents pressing a key and vice-versa for KEYUP
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                P1.cancel_jump()

    if P1.rect.top > HEIGHT:    # player falls below screen, game over
        for entity in all_sprites:
            entity.kill()
            time.sleep(1)
            displaysurface.fill((255, 0, 0))
            pygame.display.update()  # pushes out display/blit changes
            time.sleep(1)

            font = pygame.font.SysFont("Verdana", 40)                         # font type
            gameover_text = font.render('Game Over!', True, (255, 255, 255))  # object with text
            highscore = font.render(str(P1.score), True, (255, 255, 255))
            displaysurface.blit(gameover_text, (80, HEIGHT/3))                # draw to screen text
            if P1.score < 10:                                   # positions score text in the middle of screen nicely
                displaysurface.blit(highscore, (WIDTH/2 - 10, HEIGHT/3 * 2))
            if P1.score >= 10:
                displaysurface.blit(highscore, (WIDTH/2 - 30, HEIGHT/3 * 2))



            pygame.display.update()
            time.sleep(5)
            pygame.quit()
            sys.exit()

    if P1.rect.top <= HEIGHT / 3:       # if player passes a certain point of the screen
        P1. pos.y += abs(P1.vel.y)      # move player and other sprites down with the screen, illusion of moving up
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()

    displaysurface.fill((0, 0, 0))

                         # updates player movement
    plat_gen()                 # platform generation

    displaysurface.fill((0, 0, 0))      # displays player score at the top
    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(P1.score), True, (123, 255, 0))
    displaysurface.blit(g, (WIDTH / 2, 10))


    for entity in all_sprites:  # draw all sprites to the screen
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()


    pygame.display.update()     # updates game and pushes changes out
    FramesPerSec.tick(FPS)      # refreshes every tick



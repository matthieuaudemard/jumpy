# sprite classes for jumpy game
import pygame as pg
from random import choice

from settings import *

vec = pg.math.Vector2


class Spritesheet:
    """
    Utility class for loading and parsing spritesheets
    """
    def __init__(self, filename):
        self.sheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        """
        grab an image out of the spritesheet
        :param x:
        :param y:
        :param width:
        :param height:
        :return:
        """
        image = pg.Surface((width, height))
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        image.set_colorkey(BLACK)
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.game.spritesheet.get_image(614, 1063, 120, 191)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = vec(30, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        """
        Load all images from the spritesheet
        :return:
        """
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201), ]
        self.walking_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                                 self.game.spritesheet.get_image(692, 1458, 120, 207), ]
        self.walking_frames_l = [pg.transform.flip(frame, True, False) for frame in self.walking_frames_r]
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)

    def jump(self):
        """
        Make the player jump only if standing on a platform
        TODO: enable double jumping
        :return:
        """
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1
        if hits:
            self.vel.y = -20

    def animate(self):
        """
        Switch frames for character animation while jumping, walking and idle
        :return:
        """
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.vel.y < 0:
            self.jumping = True
        else:
            self.jumping = False

        # show jump animation
        if self.jumping:
            self.current_frame = 0
            self.image = self.jump_frame

        # show walk animation
        if self.walking and not self.jumping:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walking_frames_r[self.current_frame]
                else:
                    self.image = self.walking_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION

        # equation of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        elif self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(0, 384, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100),
                  self.game.spritesheet.get_image(382, 204, 200, 100),
                  ]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


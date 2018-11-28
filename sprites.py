# sprite classes for jumpy game
import xml.etree.ElementTree
from random import choice, randrange

import pygame as pg

from settings import *

vec = pg.math.Vector2


class Spritesheet:
    """
    Utility class for loading and parsing spritesheets
    """
    def __init__(self, filename):
        self.sheet = pg.image.load(filename).convert()
        self.elements = xml.etree.ElementTree.parse(filename.replace('.png', '.xml')).getroot().findall('SubTexture')

    def get_image(self, name):
        """
        grab an image out of the spritesheet by its name in the xml file
        :param name: name of the image i.e: 'bunny1_jump.png'
        :return: pygame.Surface
        """
        for elt in self.elements:
            if elt.get('name') == name:
                return self._get_image(int(elt.get('x')), int(elt.get('y')), int(elt.get('width')), int(elt.get('height')))

    def _get_image(self, x, y, width, height):
        """
        grab an image out of the spritesheet by its coordonates
        :param x:
        :param y:
        :param width:
        :param height:
        :return: pygame.Surface
        """
        image = pg.Surface((width, height))
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        image.set_colorkey(BLACK)
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.hurted = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.game.spritesheet.get_image('bunny2_ready.png')
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
        self.standing_frames = [self.game.spritesheet.get_image('bunny1_stand.png'),
                                self.game.spritesheet.get_image('bunny1_ready.png'), ]
        self.walking_frames_r = [self.game.spritesheet.get_image('bunny1_walk1.png'),
                                 self.game.spritesheet.get_image('bunny1_walk2.png'), ]
        self.walking_frames_l = [pg.transform.flip(frame, True, False) for frame in self.walking_frames_r]
        self.jump_frame = self.game.spritesheet.get_image('bunny1_jump.png')
        self.hurted_frame = self.game.spritesheet.get_image('bunny1_hurt.png')

    def jump(self):
        """
        Make the player jump only if standing on a platform
        TODO: enable double jumping
        :return:
        """
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.game.jump_sound.set_volume(0.1)
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def jump_cut(self):
        """
        Cut the jump in case of a quick space key press
        :return:
        """
        if self.jumping and self.vel.y < 0:
            self.vel.y = -8

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

        # show hurted frame
        if self.hurted:
            self.image = self.hurted_frame
            self.current_frame += 1

        # show jump animation
        if self.jumping and not self.hurted:
            self.current_frame = 0
            self.image = self.jump_frame

        # show walk animation
        if self.walking and not self.jumping and not self.hurted:
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
        if not self.jumping and not self.walking and not self.hurted:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        """
        motion management with gravity and friction
        :return:
        """
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
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image('ground_grass.png'),
                  # self.game.spritesheet.get_image('ground_grass_broken.png'),
                  self.game.spritesheet.get_image('ground_grass_small.png'),
                  # self.game.spritesheet.get_image('ground_grass_small_broken.png'),
                  ]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPWAN_PCT:
            Pow(self.game, self)


class Pow(pg.sprite.Sprite):

    pow_span_pct = POW_SPWAN_PCT

    def __init__(self, game, platform):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.platform = platform
        self.type = choice(['spring'])
        self.normal_frame = self.game.spritesheet.get_image('spring.png')
        self.engaged_frames = [self.game.spritesheet.get_image('spring_in.png'),
                               self.game.spritesheet.get_image('spring.png'),
                               self.game.spritesheet.get_image('spring_out.png'),
                               self.game.spritesheet.get_image('spring_out.png'),
                               self.game.spritesheet.get_image('spring_out.png'), ]
        self.image = self.normal_frame
        self.current_frame = 0
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top
        self.engaged = False
        self.last_update = 0

    def update(self, *args):
        if self.game.platforms.has(self.platform):
            self.animate()
        else:
            self.kill()

    def animate(self):
        now = pg.time.get_ticks()

        if self.engaged and now - self.last_update > 1500 and \
           self.current_frame < len(self.engaged_frames):
                self.image = self.engaged_frames[self.current_frame]
                self.current_frame += 1
                self.rect = self.image.get_rect()
                self.rect.centerx = self.platform.rect.centerx
                self.rect.bottom = self.platform.rect.top

        elif not self.engaged or self.current_frame >= len(self.engaged_frames):
            self.image = self.normal_frame
            self.current_frame = 0
            self.engaged = False
            self.rect = self.image.get_rect()
            self.rect.centerx = self.platform.rect.centerx
            self.rect.bottom = self.platform.rect.top


class Mob(pg.sprite.Sprite):

    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image('flyMan_fly.png')
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image('flyMan_jump.png')
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-self.rect.width, WIDTH + self.rect.width])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx = -self.vx
        self.rect.y = HEIGHT / 3  # randrange(HEIGHT / 2)  # the mob spawns in the high middle of the screen
        self.vy = 0
        self.dy = 0.5

    def update(self, *args):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy = -self.dy
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 50 or self.rect.right < -50:
            self.kill()


# Jumpy
# Graphics by Kenney @ https://kenney.nl/assets/jumper-pack
# Music - Mushroom-dance @ https://opengameart.org/content/mushroom-dance
#       - Jump and run tropical mix @ https://opengameart.org/content/jump-and-run-tropical-mix
import random
from os import path

from sprites import *


class Game:
    def __init__(self):
        """
        initialize game window, etc
        """
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.dir = path.dirname(__file__)
        self.snd_dir = path.join(self.dir, 'snd')
        self.img_dir = path.join(self.dir, 'img')
        self.highscore = 0
        self.load_data()  # loading data and textures
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = False
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.score = 0

    def load_data(self):
        """
        load spritesheet and highscore
        :return:
        """
        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET))
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump42.wav'))
        # load high score
        open_rights = 'w'
        hs_file = path.join(self.dir, HS_FILE)
        if path.isfile(hs_file):
            open_rights = 'r'
        with open(hs_file, open_rights) as f:
            try:
                self.highscore = int(f.read())
            except ValueError:  # file doesn't exists or is empty
                self.highscore = 0

    def new(self):
        """
        start a new game
        :return:
        """
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        for platform in PLATFORM_LIST:
            p = Platform(self, *platform)
            self.all_sprites.add(p)
            self.platforms.add(p)
        self.all_sprites.add(self.player)
        pg.mixer.music.load(path.join(self.snd_dir, PLAY_MUSIC))
        self.run()

    def run(self):
        """
        game loop
        :return:
        """
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(50)

    def update(self):
        """
        game loop - update
        :return:
        """
        self.all_sprites.update()
        # check if player hits on a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.centery:
                    self.player.pos.y = hits[0].rect.top
                    self.player.vel.y = 0
                    self.player.jumping = False

        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.vel.y), 2)
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 10
        # die !
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep some average number
        while len(self.platforms) < 5:
            p = Platform(self, random.randrange(0, WIDTH - 30),
                         random.randrange(-75, -50))
            self.platforms.add(p)
            self.all_sprites.add(p)

    def events(self):
        """
        game loop - events
        :return:
        """
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # check for keydown event
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                if event.key == pg.K_ESCAPE:
                    pg.event.post(pg.event.Event(pg.QUIT))
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        """
        game loop - draw
        :return:
        """
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)  # to make sure the player is always in front
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()  # *after* drawing everything, flip the display

    def show_start_screen(self):
        """
        game start screen
        :return:
        """
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Arrows to move, Space to jump', 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press enter to play or esc to quit ', 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text('High Score: ' + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        """
        game over / continue
        :return:
        """
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        pg.mixer.music.load(path.join(self.snd_dir, SCREEN_MUSIC))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.3)
        self.draw_text('GAME OVER', 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score : " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press enter play again or esc to quit", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('NEW HIGH SCORE!', 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text('High Score: ' + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.stop()

    def draw_text(self, text, size, color, x, y):
        """
        draw text on the game surface at (x, y) position whith given color
        :param text: string to draw
        :param size: size of the text
        :param color: color of the text
        :param x: x coordinate of the text
        :param y: y coordiante of the text
        :return: None
        """
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        pg.event.post(pg.event.Event(pg.QUIT))
                    elif event.key == pg.K_RETURN:
                        waiting = False


if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_go_screen()
    pg.quit()

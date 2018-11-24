# Plateformer
import pygame as pg

from settings import *


class Game:
    def __init__(self):
        """
        initialize game window, etc
        """
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = False
        self.all_sprites = pg.sprite.Group()

    def new(self):
        """
        start a new game
        :return:
        """
        self.all_sprites = pg.sprite.Group()
        self.run()

    def run(self):
        """
        game loop
        :return:
        """
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        """
        game loop - update
        :return:
        """
        pass

    def events(self):
        """
        gamme loop - events
        :return:
        """
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        """
        game loop - draw
        :return:
        """
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        """
        game start screen
        :return:
        """
        pass

    def show_go_screen(self):
        """
        game over / continue
        :return:
        """
        pass


if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_go_screen()
    pg.quit()

# -*- coding: utf-8 -*-
"""
Teach players when to yield and when to drive in traffic.

Note: Rules are for continental Europe (yield to traffic on the right).
"""

import pygame

from pygame.locals import *

from utils.scene import IntersectionScene


class App:
    def __init__(self):
        self._running = True
        self.screen = None
        self.fps = 30
        self.clock = pygame.time.Clock()
        self.playtime = 0.0
        self.size = None
        self._debug = True
        self.scores = []

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Priorities")

        self.setup_screen()

        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((192, 192, 192))
        self.font = pygame.font.SysFont('Courier', 15)
        self.scene = IntersectionScene(self, 0)
        self._running = True

    def on_event(self, event):
        """ Events: key presses, mouse moved etc """
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._running = False
            elif event.key == pygame.K_F3:
                self._debug = not self._debug
            else:
                self.scene.on_event(event)

    def on_loop(self):
        """ Compute changes in game world """
        self.milliseconds = self.clock.tick(self.fps)
        self.playtime += self.milliseconds / 1000.0
        self.scene.on_loop()

    def on_render(self):
        """ Draw game world on screen """
        self.screen.blit(self.background, (0, 0))
        self.scene.on_render()

        if self._debug:
            self.draw_text(
                "FPS: {:6.3}{}TIME: {:6.3} SECONDS{}MAX SCORE: {}".format(
                    self.clock.get_fps(),
                    " "*5,
                    self.playtime,
                    " "*5,
                    self.scene.max_score,
                )
            )
        pygame.display.flip()

    def renew_scene(self):
        self.scores.append(self.scene.score)
        if self.scene.score < 0:
            raise ValueError('WRONG')
        self.scene = IntersectionScene(self, self.scene.score)

    def on_cleanup(self):
        if self.scene.score is not None:
            self.scores.append(self.scene.score)
        if self.scores:
            wins = len([s for s in self.scores if s > 0])
            print(
                "Congrats! Scores: {}\nPlays: {}\nMean score:{:3.2}\n"
                "Wins: {}\nFails: {}".format(
                    self.scores,
                    len(self.scores),
                    sum(self.scores)/len(self.scores),
                    wins,
                    len(self.scores) - wins
                )
            )

        # TODO: have an "endscore" state at the end, with how many successful tries, reaction time etc.
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def draw_text(self, text, position=(0, 0), color=(255, 255, 0)):
        """
        Draw text in window

        @param position: tuple with top-left pixel coordinates, OR
                         string with the text "center"
        @param color: tuple with R, G, B values
        """
        fw, fh = self.font.size(text)  # fw: font width,  fh: font height
        surface = self.font.render(text, True, color, (0,0,0))

        # // makes integer division in python3
        if position == 'center':
            position = ((self.width - fw) // 2, (self.height - fh)*.8)
        else:
            position = [position[0] - fw / 2, position[1] - fh / 2]

            # Ensure text still on screen
            position[0] = max(0, position[0])
            position[1] = max(0, position[1])

        self.screen.blit(surface, position)

    def draw_image(self, sprite, position=(0, 0), angle=0, rescale=1):
        """
        Draw such that the sprite center is at the specified position.
        """

        rotated = pygame.transform.rotozoom(sprite, angle, rescale)

        rot_w = rotated.get_width()
        rot_h = rotated.get_height()

        adj_position = (
            position[0] - rot_w/2,
            position[1] - rot_h/2,
        )
        self.screen.blit(rotated, adj_position)

    def setup_screen(self):
        """
        Sets up the screen resolution and center points
        """

        display_info = pygame.display.Info()

        # TODO: move resolution and choice of windowed/fullscreen to config file

        ### Windowed: get size of screen, and make a slightly smaller window
        # (Uses entire screen area if you have multiple monitors)

        self.size = (1024, 768)
        self.screen = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        ###


        ### Full screen
        #self.screen = pygame.display.set_mode(
            #(0,0),
            #pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN
        #)

        #self.size = \
            #display_info.current_w, display_info.current_h
        ###

        self.width, self.height = self.size

        self.center = (self.width/2, self.height/2)

        assert self.screen is not None
        print(self.size, self.width, self.height)

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()

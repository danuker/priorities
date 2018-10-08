# -*- coding: utf-8 -*-
"""
Teach players when to yield and when to drive in traffic.

Note: Rules are for continental Europe (yield to traffic on the right).
"""

import pygame

from pygame.locals import *

from code.scene import IntersectionScene


class App:
    def __init__(self):
        self._running = True
        self.screen = None
        self.size = self.width, self.height = 1800, 900
        self.center = (self.width/2, self.height/2)
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.playtime = 0.0
        self._debug = True
        self.scores = []

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Priorities")
        self.screen = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((192, 192, 192))
        self.font = pygame.font.SysFont('Courier', 20, bold=True)
        self.scene = IntersectionScene(self)
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
                "FPS: {:6.3}{}TIME: {:6.3} SECONDS".format(
                    self.clock.get_fps(),
                    " "*5,
                    self.playtime
                )
            )
        pygame.display.flip()

    def renew_scene(self):
        self.scores.append(self.scene.score)
        self.scene = IntersectionScene(self)

    def on_cleanup(self):
        if self.scene.score is not None:
            self.scores.append(self.scene.score)
        if self.scores:
            wins = len([s for s in self.scores if s > 0])
            print(
                "Congrats! Scores: {}\nPlays: {}\nMean score:{}\n"
                "Wins: {}\nFails: {}".format(
                    self.scores,
                    len(self.scores),
                    sum(self.scores)/len(self.scores),
                    wins,
                    len(self.scores) - wins
                )
            )
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
            position = ((self.width - fw) // 2, (self.height - fh) // 2)

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


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()

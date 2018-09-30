# -*- coding: utf-8 -*-
"""
Teach players when to yield and when to drive in traffic.

Note: Rules are for continental Europe (yield to traffic on the right).
"""

import pygame
from pygame.locals import *
from os import path

from code.scene import IntersectionScene

class App:
    def __init__(self):
        self._running = True
        self.screen = None
        self.size = self.width, self.height = 1800, 900
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.playtime = 0.0
        self._debug = False

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Priorities")
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
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

        self.scene.on_event(event)

    def on_loop(self):
        """ Compute changes in game world """
        self.milliseconds = self.clock.tick(self.fps)
        self.playtime += self.milliseconds / 1000.0
        self.scene.on_loop()

    def on_render(self):
        """ Draw game world on screen """
        if self._debug:
            self.draw_text(
                "FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
                        self.clock.get_fps(),
                        " "*5,
                        self.playtime)
            )

        self.screen.blit(self.background, (0, 0))
        self.scene.on_render()
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while( self._running ):
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
        fw, fh = self.font.size(text) # fw: font width,  fh: font height
        surface = self.font.render(text, True, color)

        # // makes integer division in python3
        if position == 'center':
            position = ((self.width - fw) // 2, (self.height - fh) // 2)

        self.screen.blit(surface, position)

    def draw_image(self, sprite, position=(0, 0), angle=0, rescale=1):
        """
        Draw such that the unrotated equivalent would have its top-left corner
        at the specified position.
        """

        w = sprite.get_width() * rescale
        h = sprite.get_height() * rescale

        rotated = pygame.transform.rotozoom(sprite, angle, rescale)

        rot_w = rotated.get_width()
        rot_h = rotated.get_height()


        w_difference = (rot_w - w)
        h_difference = (rot_h - h)

        adj_position = (
            position[0] - 0.5*w_difference,
            position[1] - 0.5*h_difference,
        )
        self.screen.blit(rotated, adj_position)


if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()

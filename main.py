# -*- coding: utf-8 -*-
"""
Teach players when to yield and when to drive in traffic.

Note: Rules are for continental Europe (yield to traffic on the right).
"""

import pygame
from pygame.locals import *

class App:
    def __init__(self):
        self._running = True
        self.screen = None
        self.size = self.width, self.height = 800, 600
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

    def on_loop(self):
        """ Compute changes in game world """
        milliseconds = self.clock.tick(self.fps)
        self.playtime += milliseconds / 1000.0

    def on_render(self):
        """ Draw game world on screen """
        if self._debug:
            self.draw_text(
                "FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
                        self.clock.get_fps(),
                        " "*5,
                        self.playtime),

            )

        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))

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


if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()

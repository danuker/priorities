#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 13:31:35 2018

@author: dan
"""
import pygame
from os import path


class GameObject:
    """ Object that has a visible representation on screen """

    def __init__(self, app):
        self.app = app

    def on_event(self, event):
        pass

    def on_loop(self):
        pass

    def on_render(self):
        pass


class Car(GameObject):
    def __init__(self, app, road, pos, signal):
        self.road = road
        self._x, self._y = pos  # pixels relative to center of intersection
        self._speed = 0  # pixels / second
        self._angle = 0  # go up
        self.signal = signal  # left, right or None
        self._images = {
            'straight': pygame.image.load(path.join('images', 'car.png')),
            'right': pygame.image.load(path.join('images', 'car_signal_right.png')),
            'left': pygame.image.load(path.join('images', 'car_signal_left.png'))
        }
        self._car = self._images['straight']
        super().__init__(app)

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if uparrow(event):
                self._speed = 300

        if event.type == pygame.KEYUP:
            if uparrow(event):
                self._speed = 0


    def on_loop(self):
        to_move_px = self.app.milliseconds * self._speed / 1000
        self._y += to_move_px

    def on_render(self):
        self.app.draw_image(
            self._car,
            (self._x, self._y),
            self._angle,
            0.3
        )


def uparrow(event):
    return event.key == pygame.K_UP or event.key == pygame.K_w


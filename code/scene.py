#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scene abstractions for priorities
Created on Sun Sep 30 13:19:15 2018

@author: dan
"""

import random


class Scene:
    def __init__(self, app):
        # Game objects to notify
        self._objects = {}
        self._app = app

    def on_event(self, event):
        for object in self._objects:
            object.on_event(event)

    def on_loop(self):
        for object in self._objects:
            object.on_loop()

    def on_render(self):
        for object in self._objects:
            object.on_render()


class IntersectionScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.num_roads = random.choice([3, 4])
        self.type = random.choice([
            'uncontrolled', 'yield-sign-only', 'controlled'
            ])

        self._init_roads()
        self._init_signs()
        self._init_vehicles()




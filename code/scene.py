#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scene abstractions for priorities
Created on Sun Sep 30 13:19:15 2018

@author: dan
"""

import random
from code.game_objects import Car

class Scene:
    def __init__(self, app):
        # Game objects to notify
        self.objects = set()
        self.app = app

    def on_event(self, event):
        for object in self.objects:
            object.on_event(event)

    def on_loop(self):
        for object in self.objects:
            object.on_loop()

    def on_render(self):
        for object in self.objects:
            object.on_render()


class IntersectionScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.num_roads = random.choice([3, 4])
        self.type = random.choice([
            'uncontrolled', 'yield-sign-only', 'controlled'
            ])

#        self._init_roads()
#        self._init_signs()
        self._init_vehicles()

    def _init_vehicles(self):
        me = Car(self.app, None, (100, 100), None)
        self.objects.add(me)

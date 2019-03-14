#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scene abstractions for priorities
Created on Sun Sep 30 13:19:15 2018

@author: dan
"""

import pygame
import random
from itertools import chain
from utils.game_objects import PlayerCar, TrafficCar, Road, IntersectionCenter,\
    PrioSign, YieldSign


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
    def __init__(self, app, score):
        super().__init__(app)
        self.num_roads = random.choice([3, 4])

        # We want yield-only and controlled intersections more often
        self.type = random.choices(
            ['uncontrolled', 'yield-sign-only', 'controlled'],
            weights=[1, 2, 3]
        )[0]
        self.reaction_time = Road.car_seconds

        self.roads = self._init_roads()
        self.signs = self._init_signs()
        self.vehicles = self._init_vehicles()
        self.objects = set(chain(self.roads, self.signs, self.vehicles))
        self.start_time = self.app.playtime

        self.action_time = None
        self.user_action = None
        self.state = 'running'
        self.max_score = score  # Max score seen
        self.score = score  # Successful rounds

    def _init_roads(self):
        center = IntersectionCenter(self.app)
        self.start_road = Road(self.app, 0)

        angle = {'right': 90, 'ahead': 180, 'left': -90}

        self.road_names = random.sample(angle.keys(), self.num_roads-1)

        self.watch_out_roads = {
            name: Road(
                self.app,
                random.uniform(angle[name]+22.4, angle[name]-22.4)
            )
            for name in self.road_names
        }

        self.named_roads = {'behind': self.start_road}
        self.named_roads.update(self.watch_out_roads)

        return set(self.watch_out_roads.values())\
            .union({self.start_road, center})

    def _init_signs(self):
        def _set_roads_priority(roads, priority=True):
            for road in roads:
                road.has_right_of_way = True
            print('setting priority of roads {}'.format(roads))

        if self.type == 'yield-sign-only':
            # We can only have a straight road
            possible_pairs = []
            for road_start in self.named_roads.values():
                for road_end in self.named_roads.values():
                    if road_start.is_opposite(road_end):
                        possible_pairs.append([road_start, road_end])

            print('semicontr', self.named_roads)

            _set_roads_priority(random.choice(possible_pairs))


        elif self.type == 'controlled':
            # Any 2 roads have priority
            print('contr', self.named_roads)
            _set_roads_priority(random.sample(list(self.named_roads.values()), 2))

        signs = set()

        if self.type != 'uncontrolled':
            print('type: {}'.format(self.type))
            for road in self.named_roads.values():
                if road.has_right_of_way:
                    if self.type != 'yield-sign-only':
                        signs.add(PrioSign(self.app, self, road))
                else:
                    signs.add(YieldSign(
                            self.app, self, road, self.type != 'yield-sign-only'
                    ))

        return signs

    def _init_vehicles(self):
        desired_direction = random.choice(list(self.watch_out_roads.keys()))
        desired_road = self.watch_out_roads[desired_direction]
        signal = self.start_road.needed_turn(desired_road)

        self.player_car = PlayerCar(self.app, self.start_road, signal=signal)

        cars = {self.player_car}

        for road_name in self.watch_out_roads:
            road = self.watch_out_roads[road_name]

            if random.random() < 0.5:
                possible_directions = [
                    key for key in self.named_roads
                    if self.named_roads[key] != road
                ]

                desired_direction = random.choice(possible_directions)
                desired_road = self.named_roads[desired_direction]
                signal = road.needed_turn(desired_road)

                cars.add(TrafficCar(self.app, road, signal=signal))

        return cars

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.user_action:
                if uparrow(event):
                    self.set_user_action('ahead')
                elif rightarrow(event):
                    self.set_user_action('right')
                elif leftarrow(event):
                    self.set_user_action('left')
                elif downarrow(event):
                    self.set_user_action('behind')

                if self.user_action:
                    waited = self.app.playtime - self.start_time
                    must_yield, reason = self.player_car.have_to_yield()
                    if must_yield:
                        if self.user_action == 'behind':
                            self.state = 'correct'
                        else:
                            self.state = 'accident'
                    else:
                        if self.user_action == self.player_car.signal:
                            self.state = 'correct'
                        else:
                            self.state = 'accident'

                    if self.state == 'correct':
                        self.score += 1
                    elif self.state == 'accident':
                        self.score = -21.0
                    self.max_score = max(self.score, self.max_score)
            else:
                # The user made an action.
                # We wait for the user to see the feedback.
                # Then we want to continue.
                if self.app.playtime - self.action_time > 0.25:
                    self.app.renew_scene()

    def on_loop(self):
        waited = self.app.playtime - self.start_time
        if self.user_action:
            pass  # Do not update world state anymore
        elif waited > self.reaction_time:
            self.set_user_action('dozed_off')
            self.state = 'timeout'
            self.score = -6.0
        else:
            for object in self.objects:
                object.on_loop()

    def on_render(self):
        for road in self.roads:
            road.on_render()
        for vehicle in self.vehicles:
            vehicle.on_render()
        for sign in self.signs:
            sign.on_render()

        must_yield, reason = self.player_car.have_to_yield()

        color = (255, 0, 0)
        if self.state in ['accident', 'timeout']:
            if must_yield:
                text = 'You needed to yield! {}'.format(reason)
            else:
                text = 'You needed to drive {}!'.format(self.player_car.signal)

        if self.state == 'timeout':
            text = 'You did not react within {} seconds! {}'.format(
                self.reaction_time, text
            )

        elif self.state == 'correct':
            color = (0, 255, 0)
            if self.user_action == 'behind':
                text = "You correctly yielded!"
            else:
                text = "You correctly drove!"

        if self.state != 'running':
            self.app.draw_text(
                "{}".format(text),
                position='center',
                color=color
             )

    def set_user_action(self, action):
        self.user_action = action
        self.action_time = self.app.playtime


def uparrow(event):
    return event.key == pygame.K_UP or event.key == pygame.K_w


def downarrow(event):
    return event.key == pygame.K_DOWN or event.key == pygame.K_s


def leftarrow(event):
    return event.key == pygame.K_LEFT or event.key == pygame.K_a


def rightarrow(event):
    return event.key == pygame.K_RIGHT or event.key == pygame.K_d

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 13:31:35 2018

@author: dan
"""
import pygame
from os import path

from code.yield_resolver import must_yield
from code.motion import move_polar


class GameObject:
    """
    Object that has a visible representation on screen, or can interact
    """

    def __init__(self, app):
        self.app = app

    def on_event(self, event):
        pass

    def on_loop(self):
        pass

    def on_render(self):
        pass


class Car(GameObject):
    max_speed = 20  # px/second

    def __init__(self, app, road, pos=None, signal='ahead'):
        self.signal = signal  # left, right or ahead (no signalling)
        self.exited_intersection = False

        self._images = {
            'ahead': load_image('car.png'),
            'right': load_image('car_signal_right.png'),
            'left': load_image('car_signal_left.png')
        }
        self._car_image = self._images['ahead']

        if road:
            self.road = road
            self._x, self._y = road.get_car_initial_coord()
            self._angle = road.angle
        else:
            self._x, self._y = pos  # pixels relative to center of intersection
            self._angle = 0  # go up

        self._speed = 0  # pixels / second
        super().__init__(app)

    def _signal_on_render(self):
        if self.signal != 'ahead':
            if self.app.playtime % 0.5 < 0.1:
                self._car_image = self._images['ahead']
            else:
                self._car_image = self._images[self.signal]

    def on_loop(self):
        to_move_px = self.app.milliseconds * self._speed / 1000
        self._x, self._y = \
            move_polar((self._x, self._y), to_move_px, self._angle)

    def on_render(self):
        self._signal_on_render()
        self.app.draw_image(
            self._car_image,
            (self._x, self._y),
            self._angle,
            0.2
        )

    def have_to_yield(self):
        """ Check if car has to yield to any other car in the intersection """
        for other_car in self.app.scene.vehicles:
            if self != other_car:
                relative_position = self.road.needed_turn(other_car.road)

                my, reason = must_yield(
                    my_right_of_way=self.road.has_right_of_way,
                    my_turn=self.signal,
                    other_right_of_way=other_car.road.has_right_of_way,
                    other_turn=other_car.signal,
                    other_relative_position=relative_position
                )

                if my:
                    return my, reason

        # We don't have to yield to anyone in the intersection
        return False, \
            "Other cars either won't cross your path, or need to yield to you."


class PlayerCar(Car):
    def __init__(self, app, road, pos=None, signal='ahead'):
        super().__init__(app, road, pos, signal)
        self._speed = self.max_speed


class TrafficCar(Car):
    def __init__(self, app, road, pos=None, signal='ahead'):
        super().__init__(app, road, pos, signal)
        self._speed = self.max_speed


class Road(GameObject):
    lane_width = 100
    road_color = (92, 92, 100)
    # How far to place car, in seconds at max speed
    car_seconds = 5

    def __init__(self, app, angle=0, has_right_of_way=False):
        """Angle of road, angle 0 = upwards, 90 = right"""
        super().__init__(app)
        self.angle = angle
        self.origin = self.app.center
        self.pointlist = self._init_points()
        self.has_right_of_way = has_right_of_way

    def _init_points(self):
        # We need 4 points, starting from the center of the screen

        point_NW = move_polar(self.origin, self.lane_width, self.angle + 90)
        point_SW = move_polar(point_NW, self.app.width, self.angle + 180)
        point_NE = move_polar(self.origin, self.lane_width, self.angle - 90)
        point_SE = move_polar(point_NE, self.app.width, self.angle + 180)

        return [point_NW, point_SW, point_SE, point_NE]

    def on_render(self):
        pygame.draw.polygon(
            self.app.screen,
            self.road_color,
            self.pointlist
        )

    def get_car_initial_coord(self):
        """
        Get the coords of the center of the car sprite on screen

        Car is placed car_seconds away from intersection center area,
        on the right-hand-drive lane.
        """

        road_center = move_polar(
            self.origin,
            Road.car_seconds * Car.max_speed + self.lane_width*2,
            self.angle + 180
        )

        return move_polar(
            road_center,
            self.lane_width/2,
            self.angle - 90
        )

    def is_opposite(self, other_road):
        # 180 degrees +- 45
        return 135 < (self.angle - other_road.angle) % 360 < 225

    def is_90_right_of(self, other_road):
        # 90 degrees +- 45
        return 45 < (self.angle - other_road.angle) % 360 < 135

    def needed_turn(self, target):
        if self.is_opposite(target):
            return 'ahead'
        elif target.is_90_right_of(self):
            return 'right'
        elif self.is_90_right_of(target):
            return 'left'
        else:
            raise ValueError('Target road is neither left, right, nor ahead')

    def overlaps(self, target):
        return -45 > self.angle - target.angle > 45


class IntersectionCenter(Road):
    def __init__(self, app):
        super().__init__(app)

    def on_render(self):
        pygame.draw.circle(
            self.app.screen,
            self.road_color,
            tuple(int(coord) for coord in self.origin),
            self.lane_width
        )


def load_image(name):
    return pygame.image.load(path.join('images', name))

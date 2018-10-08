#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 23:41:06 2018

@author: dan
"""

# Cases:

# Me:
# I am on right-of-way road
# I am not on right-of-way road

# Me turning:
# Want right turn
# Want straight
# Want left turn

# Other car:
# Other car is on right-of-way road
# Other car is not on right-of-way road

# Other car turning:
# Want right turn
# Want straight
# Want left turn

# Relative positions:
# Other car to my right
# Other car in front of me
# Other car to my left

# Total possible cases for 2 cars:
# Card(Me) * Card(Me turn) * Card (Other) * Card (Other turn) * Card(positions)
# = 2 * 3 * 2 * 3 * 3 = 108

# Directions one can go
directions = ['behind', 'right', 'ahead', 'left']

# Corners of the intersection one can drive over
corners = ['near-right', 'far-right', 'far-left', 'near-left']
###########
# FL # FR #
###########
# NL # NR #
###########
# Reality has a better model (every corner here is split into 4).
# (i.e. two cars facing each other can turn left, if they keep left of center)
# We won't model this for now.


def _resulting_position(start_index, turn_index):
    """
        Find out which way a vehicle starting from start_position ends up,
    after taking turn.

        All data (input and output) is an index in the `directions` vector.

    Starting from behind (neutral position), the turn dictates the direction
    >>> _resulting_position(0, 0)
    0
    >>> _resulting_position(0, 1)
    1
    >>> _resulting_position(0, 2)
    2
    >>> _resulting_position(0, 3)
    3

    Starting from ahead (opposite of me), the direction is reversed
    >>> _resulting_position(2, 0)
    2
    >>> _resulting_position(2, 1)
    3
    >>> _resulting_position(2, 2)
    0
    >>> _resulting_position(2, 3)
    1

    From right, turning right, gives ahead
    >>> _resulting_position(1, 1)
    2

    From left, turning right, gives behind
    >>> _resulting_position(3, 1)
    0
    """

    return (start_index + turn_index) % len(directions)


def _needed_corners(start_position, turn):
    """
    Returns the needed segments of the intersecton to make a turn
    >>> _needed_corners('behind', 'ahead')
    ['near-right', 'far-right']
    >>> _needed_corners('right', 'right')
    ['far-right']
    >>> _needed_corners('left', 'right')
    ['near-left']
    >>> _needed_corners('left', 'left')
    ['near-left', 'near-right', 'far-right']

    """

    # Count of needed corners for a given turn
    needed_count = {'behind': 4, 'right': 1, 'ahead': 2, 'left': 3}

    try:
        pos_index = directions.index(start_position)
    except ValueError:
        raise ValueError(
            'Relative position {} not valid!'.format(start_position)
        )

    entrance_corner_index = pos_index
    exit_corner_index_modclass = pos_index + needed_count[turn]

    corner_indices_modclass = \
        range(entrance_corner_index, exit_corner_index_modclass)

    corner_indices = [corner % 4 for corner in corner_indices_modclass]
    return [corners[corner_index] for corner_index in corner_indices]


def paths_intersect(my_turn, other_relative_position, other_turn):
    """
    >>> paths_intersect('left', 'left', 'right')
    False
    >>> paths_intersect('left', 'ahead', 'right')
    True
    """

    my_needed_corners = _needed_corners('behind', my_turn)
    other_needed_corners = _needed_corners(other_relative_position, other_turn)

    return len(set(my_needed_corners).intersection(other_needed_corners)) > 0


def must_yield(
        my_right_of_way,
        my_turn,
        other_right_of_way,
        other_turn,
        other_relative_position
        ):
    """
        Figure out if we have to yield to another specific car.
        Note: This only checks yielding vs one single car. You have to check
    all cars in an intersection.

        Returns Boolean (whether we must yield), and String
    (why we must yield)

    # Must not yield to car from ahead turning left
    >>> must_yield(False, 'right', False, 'left', 'ahead')
    (False, None)

    # Must yield to car from right, continuing forward
    >>> must_yield(True, 'left', True, 'ahead', 'right')
    (True, 'The car on your right has right-of-way, and your paths would intersect.')

    # No need to yield to car from left going straight,
    # if other car goes out of the right-of-way
    # (we can tell the ROW bends because he is to my left, and we both have ROW)
    >>> must_yield(True, 'left', True, 'ahead', 'left')
    (False, None)
    """

    reason = None

    # If there's a right-of-way equality case, yield to right-hand side instead
    if my_right_of_way == other_right_of_way:
        if other_relative_position == 'right':
            other_right_of_way = True
            my_right_of_way = False
            reason = 'The car on your right has right-of-way, and your paths would intersect.'
        if other_relative_position == 'left':
            other_right_of_way = False
            my_right_of_way = True

    # If we are facing the other car, we still have equality,
    #   and have to yield if we go left (other car coming from our right).
    # This case is handled in the catch-all at the end.
    #
    # But if the other car wants to go left and we don't,
    #   then we have priority.
    #
    # Note: this can lead to deadlocks (say both cars want left),
    #   but humans can negociate after stopping.
    if my_right_of_way == other_right_of_way:
        if other_turn == 'left' and my_turn in ['ahead', 'right']:
            my_right_of_way = True
            other_right_of_way = False

    if my_right_of_way and not other_right_of_way:
        return False, None

    if paths_intersect(my_turn, other_relative_position, other_turn):
        if not reason:
            reason = 'Your path would intersect with the car from {}.'.format(
                other_relative_position
            )
        return True, reason

    else:
        return False, None


if __name__ == '__main__':
    import doctest
    doctest.testmod()

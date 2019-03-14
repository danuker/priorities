from math import sin, cos, radians


def move_polar(pos, distance, angle):
    # Assume angle is degrees CCW from upwards=0

    angle_rad = radians(angle + 180)
    return (
        pos[0] + distance * sin(angle_rad),
        pos[1] + distance * cos(angle_rad)
    )


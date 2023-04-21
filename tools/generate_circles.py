"""
Generates the maps/circles.json map.

This map is a square map with two concentric circles with 4 entrances each.
There are four spawns, one at each corner of the map.
"""
import json
import math
import sys
from typing import Callable

sys.path.append(".")

from tank_wars_iit._engine.map import MapJson, WallJson  # noqa

FILENAME = "src/tank_wars_iit/_engine/maps/circles.json"

NUM_CIRCLE_SEGMENTS = 32
WALL_THICKNESS = 32

WIDTH = 1536
HEIGHT = 1536

INNER_RADIUS = WIDTH // 16 * 3
OUTER_RADIUS = WIDTH // 8 * 3

Predicate = Callable[[int], bool]


def create_circle(radius: int, predicate: Predicate) -> list[WallJson]:
    """
    Creates a circle of a specified radius, and uses a predicate to determine
    which circle segments to include, given the index of the segment.

    Index 0 corresponds to the first segment starting from the positive X axis,
    moving towards the positive Y axis.
    """
    dangle = 2 * math.pi / NUM_CIRCLE_SEGMENTS
    outer_radius = radius + WALL_THICKNESS / 2
    segment_length = math.tan(dangle / 2) * outer_radius * 2

    circle_walls: list[WallJson] = []

    for i in range(NUM_CIRCLE_SEGMENTS):
        if not predicate(i):
            continue
        angle = dangle * i
        circle_walls.append({
            "position": {
                "x": WIDTH / 2 + math.cos(angle + dangle/2) * radius,
                "y": HEIGHT / 2 + math.sin(angle + dangle/2) * radius,
            },
            "size": {
                "width": WALL_THICKNESS,
                "height": segment_length
            },
            "rotation": math.degrees(angle + dangle/2)
        })

    return circle_walls


def left_right_up_down_predicate(i: int):
    """
    Predicate which returns `True` for the left, right, up, and down eighths of
    the circle.
    """
    eighth = NUM_CIRCLE_SEGMENTS // 8
    # Add eighth // 2 to i to shift period down one half of an eighth;
    # otherwise it would be up-left, up-right, down-left, down-right
    return ((i + eighth // 2) // eighth) % 2 == 0


if __name__ == "__main__":
    walls = create_circle(INNER_RADIUS,
                          lambda i: not left_right_up_down_predicate(i))
    walls += create_circle(OUTER_RADIUS, left_right_up_down_predicate)

    map: MapJson = {
        "size": {
            "width": WIDTH,
            "height": HEIGHT
        },
        "walls": walls,
        "spawns": [
            {
                "x": 128,
                "y": 128
            },
            {
                "x": WIDTH - 128,
                "y": HEIGHT - 128
            }
        ]
    }

    with open(FILENAME, "w") as file:
        json.dump(map, file, indent=4)

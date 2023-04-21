"""
Generates the maps/lock.json map.

This map is a square map with many concentric circles, each with a narrow hole.
There are five spawns at the center of the map and the corners.

This map is mainly meant for testing pathfinding.
"""
import json
import math
from random import randrange, seed
import sys
from typing import Callable

sys.path.append(".")

from tank_wars_iit._engine.map import MapJson, WallJson  # noqa

FILENAME = "src/tank_wars_iit/_engine/maps/lock.json"

NUM_CIRCLE_SEGMENTS = 32
WALL_THICKNESS = 32

WIDTH = 2048
HEIGHT = 2048

RADIUS_STEP = WIDTH // 8
NUM_CIRCLES = 3

SEED = 128938120

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


def hole_predicate_factory(hole_index: int):
    """
    Generates a predicate for creating a circle with a narrow hole at a
    specified hole_index.
    """
    def predicate(i: int):
        return (i - hole_index) % NUM_CIRCLE_SEGMENTS > 4
    return predicate


if __name__ == "__main__":
    # Set random seed
    seed(SEED)

    walls = []

    for i in range(NUM_CIRCLES):
        hole_index = randrange(0, NUM_CIRCLE_SEGMENTS)
        walls += create_circle(RADIUS_STEP * (i + 1),
                               hole_predicate_factory(hole_index))

    map: MapJson = {
        "size": {
            "width": WIDTH,
            "height": HEIGHT
        },
        "walls": walls,
        "spawns": [
            {
                "x": WIDTH // 2,
                "y": HEIGHT // 2
            },
            {
                "x": 128,
                "y": 128
            },
            {
                "x": 128,
                "y": HEIGHT - 128
            },
            {
                "x": WIDTH - 128,
                "y": HEIGHT - 128
            },
            {
                "x": WIDTH - 128,
                "y": 128
            }
        ]
    }

    with open(FILENAME, "w") as file:
        json.dump(map, file, indent=4)

import json
import math
from typing import Callable

from map import MapJson, WallJson

NUM_CIRCLE_SEGMENTS = 32
WALL_THICKNESS = 32

WIDTH = 1536
HEIGHT = 1536

INNER_RADIUS = WIDTH // 16 * 3
OUTER_RADIUS = WIDTH // 8 * 3

walls: list[WallJson] = []

def create_circle(radius: int, predicate: Callable[[int], bool] = lambda x: True) -> list[WallJson]:
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

quarter_segments = NUM_CIRCLE_SEGMENTS // 4

walls += create_circle(INNER_RADIUS, lambda x: x % quarter_segments >= quarter_segments // 4 and x % quarter_segments < 3 * quarter_segments // 4)
walls += create_circle(OUTER_RADIUS, lambda x: x % quarter_segments < quarter_segments // 4 or x % quarter_segments >= 3 * quarter_segments // 4)

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

with open("circles.json", "w") as file:
    json.dump(map, file, indent=4)

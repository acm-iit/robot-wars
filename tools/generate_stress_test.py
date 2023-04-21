"""
Generates the maps/stress_test.json map.

This map is a large square map with no walls and 64 spawns, meant for stress
testing the engine.
"""
import json
import sys

sys.path.append(".")

from tank_wars_iit._engine.map import MapJson, PositionJson  # noqa

FILENAME = "src/tank_wars_iit/_engine/maps/stress_test.json"

WIDTH = 8192
HEIGHT = 8192

SPAWNS_PER_DIMENSION = 8

if __name__ == "__main__":
    spawn_width = WIDTH / SPAWNS_PER_DIMENSION
    spawn_height = HEIGHT / SPAWNS_PER_DIMENSION
    spawns: list[PositionJson] = [
        {
            "x": spawn_width * (x + 0.5),
            "y": spawn_height * (y + 0.5)
        }
        for x in range(SPAWNS_PER_DIMENSION)
        for y in range(SPAWNS_PER_DIMENSION)
    ]

    map: MapJson = {
        "size": {
            "width": WIDTH,
            "height": HEIGHT
        },
        "walls": [],
        "spawns": spawns
    }

    with open(FILENAME, "w") as file:
        json.dump(map, file, indent=4)

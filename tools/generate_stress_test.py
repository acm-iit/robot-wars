"""
Generates the maps/stress_test.json map.

This map is a large square map with no walls and 64 spawns, meant for stress
testing the engine.
"""
import json
import sys

sys.path.append(".")

from engine.map import MapJson, PositionJson

FILENAME = "engine/maps/stress_test.json"

WIDTH = 2048
HEIGHT = 2048

SPAWNS_PER_DIMENSION = 8

if __name__ == "__main__":
    spawns: list[PositionJson] = [{
        "x": WIDTH // SPAWNS_PER_DIMENSION * x + WIDTH // SPAWNS_PER_DIMENSION // 2,
        "y": HEIGHT // SPAWNS_PER_DIMENSION * y + HEIGHT // SPAWNS_PER_DIMENSION // 2
    } for x in range(SPAWNS_PER_DIMENSION) for y in range(SPAWNS_PER_DIMENSION)]

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

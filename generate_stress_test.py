import json

from engine import MapJson, PositionJson

WIDTH = 2048
HEIGHT = 2048

SPAWNS_PER_DIMENSION = 8

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

with open("stress_test.json", "w") as file:
    json.dump(map, file, indent=4)

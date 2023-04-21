"""
Generates the maps/maze.json map.

This map is a square map with a maze.

This map is mainly meant for testing pathfinding.
"""
import json
from random import choice, randrange, seed
import sys

sys.path.append(".")

from tank_wars_iit._engine.map import MapJson, WallJson  # noqa

FILENAME = "src/tank_wars_iit/_engine/maps/maze.json"

WALL_THICKNESS = 32

WIDTH = 1536

NODE_COUNT = 6      # Number of nodes per dimension
NODE_SIZE = WIDTH // NODE_COUNT

SEED = 897328942


class Node:
    """Represents a node of the maze."""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.neighbors = list[tuple[int, Node]]()
        self.edges = [False, False, False, False]


def index_to_direction(i: int):
    if i == 0:
        return (1, 0)
    elif i == 1:
        return (0, 1)
    elif i == 2:
        return (-1, 0)
    else:  # i == 3
        return (0, -1)


def opposite_direction(i: int):
    if i == 0:
        return 2
    elif i == 1:
        return 3
    elif i == 2:
        return 0
    else:  # i == 3
        return 1


def create_graph():
    nodes = list[Node]()
    for i in range(NODE_COUNT):
        for j in range(NODE_COUNT):
            node = Node(NODE_SIZE // 2 + NODE_SIZE * i,
                        NODE_SIZE // 2 + NODE_SIZE * j)
            nodes.append(node)

    for i in range(NODE_COUNT):
        for j in range(NODE_COUNT):
            node = nodes[i * NODE_COUNT + j]
            for k in range(4):
                di, dj = index_to_direction(k)
                ni, nj = i + di, j + dj
                if ni < 0 or ni >= NODE_COUNT or nj < 0 or nj >= NODE_COUNT:
                    continue
                neighbor = nodes[ni * NODE_COUNT + nj]
                node.neighbors.append((k, neighbor))

    return nodes


def create_tree(graph: list[Node]):
    root = choice(graph)
    edges = [(d, root, neighbor) for d, neighbor in root.neighbors]

    while len(edges) > 0:
        d, fro, to = edges.pop(randrange(len(edges)))
        if any(to.edges):
            continue
        fro.edges[d] = True
        to.edges[opposite_direction(d)] = True
        edges += [(d, to, neighbor)
                  for d, neighbor in to.neighbors
                  if not any(neighbor.edges)]


def create_walls(graph: list[Node]):
    walls = list[WallJson]()

    for i in range(NODE_COUNT):
        for j in range(NODE_COUNT):
            node = graph[i * NODE_COUNT + j]
            if i < NODE_COUNT - 1 and not node.edges[0]:
                walls.append({
                    "position": {
                        "x": node.x + NODE_SIZE // 2,
                        "y": node.y
                    },
                    "size": {
                        "width": WALL_THICKNESS,
                        "height": NODE_SIZE + WALL_THICKNESS
                    },
                    "rotation": 0
                })
            if j < NODE_COUNT - 1 and not node.edges[1]:
                walls.append({
                    "position": {
                        "x": node.x,
                        "y": node.y + NODE_SIZE // 2
                    },
                    "size": {
                        "width": NODE_SIZE + WALL_THICKNESS,
                        "height": WALL_THICKNESS
                    },
                    "rotation": 0
                })

    return walls


if __name__ == "__main__":
    # Set random seed
    seed(SEED)

    graph = create_graph()
    create_tree(graph)
    walls = create_walls(graph)

    map: MapJson = {
        "size": {
            "width": WIDTH,
            "height": WIDTH
        },
        "walls": walls,
        "spawns": [
            {
                "x": NODE_SIZE // 2,
                "y": NODE_SIZE // 2
            },
            {
                "x": NODE_SIZE // 2,
                "y": WIDTH - NODE_SIZE // 2
            },
            {
                "x": WIDTH - NODE_SIZE // 2,
                "y": WIDTH - NODE_SIZE // 2
            },
            {
                "x": WIDTH - NODE_SIZE // 2,
                "y": NODE_SIZE // 2
            }
        ]
    }

    with open(FILENAME, "w") as file:
        json.dump(map, file, indent=4)

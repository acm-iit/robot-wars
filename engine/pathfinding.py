from __future__ import annotations
from collections import defaultdict
import heapq
import math
from typing import Optional

import pygame

from engine.entity.robot import ROBOT_HITBOX_WIDTH, ROBOT_HITBOX_LENGTH
from engine.quadtree import Quadtree
from engine.util import check_polygon_collision

Rect = pygame.Rect
Vector2 = pygame.Vector2

NODE_SIZE = 64


class Node:
    """Node of a PathfindingGraph."""
    def __init__(self, position: Vector2):
        self.position = position

        self.neighbors: list[Node] = []

    # Define these two comparison operators to avoid edge case in a_star where
    # two nodes have the same f_score and need to be compared
    def __lt__(self, _: Node):
        return True

    def __le__(self, _: Node):
        return True

    @staticmethod
    def a_star(start: Node, goal: Node) -> Optional[list[Node]]:
        """Computes the path from start to goal using A*."""
        # Define h (heuristic) as distance between nodes
        def h(node: Node):
            return (goal.position - node.position).magnitude()
        h_start = h(start)

        # Heap of reachable nodes, sorted by f-value
        open_set = list[tuple[float, Node]]()
        heapq.heappush(open_set, (h_start, start))

        # Map of node to node preceding it on the path
        came_from = dict[Node, Node]()

        def get_path(node) -> list[Node]:
            """Constructs the path to node via came_from."""
            path = [node]
            while node in came_from:
                node = came_from[node]
                path.append(node)
            return path[::-1]

        # Map of node to g-score (total distance travelled)
        # Default to infinity for all nodes besides start, which is 0
        g_score = defaultdict[Node, float](lambda: math.inf)
        g_score[start] = 0

        # Map of node to f-score (g + h)
        # Default to infinity for all nodes besides start, which is h(start)
        f_score = defaultdict[Node, float](lambda: math.inf)
        f_score[start] = h_start

        # Set of seen nodes
        seen = set[Node]()

        # Keep track of node with minimum h-score in case we don't find a path
        min_h_score = h_start
        min_h_node = start

        while len(open_set) > 0:
            _, current = heapq.heappop(open_set)

            if current in seen:
                continue

            if current == goal:
                # We found our goal, return the path
                return get_path(current)

            for neighbor in current.neighbors:
                distance = (neighbor.position - current.position).magnitude()
                tentative_g_score = g_score[current] + distance
                # If this new g-score for the neighbor is lower, then update
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + h(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

            h_current = h(current)
            if h_current < min_h_score:
                min_h_score = h_current
                min_h_node = current

            seen.add(current)

        # Couldn't find path, just give path to closest node
        return get_path(min_h_node)


class PathfindingGraph:
    """
    Graph of pathfinding nodes used to aid Robots to navigate around Walls.
    """
    def __init__(self, size: Vector2, quadtree: Quadtree):
        self.__size = size
        self.__nodes = self.__construct_nodes(size, quadtree)

    def __construct_nodes(self, size: Vector2, quadtree: Quadtree
                          ) -> list[list[Node]]:
        """
        Constructs 2D array of nodes evenly spaced around the Arena, and
        determines the edges between the nodes.
        """
        width = int(size.x / NODE_SIZE)
        height = int(size.y / NODE_SIZE)
        nodes = [[Node(Vector2(NODE_SIZE * (i + 0.5), NODE_SIZE * (j + 0.5)))
                  for i in range(width)] for j in range(height)]

        # Connect nodes
        for j1 in range(height):
            for i1 in range(width):
                node1 = nodes[j1][i1]
                for dj in range(-1, 2):
                    for di in range(-1, 2):
                        if dj == 0 and di == 0:
                            continue
                        j2, i2 = j1 + dj, i1 + di
                        if j2 < 0 or j2 >= height or i2 < 0 or i2 >= width:
                            continue
                        node2 = nodes[j2][i2]
                        if self.__can_connect(node1, node2, quadtree):
                            node1.neighbors.append(node2)

        return nodes

    def __can_connect(self, node1: Node, node2: Node, quadtree: Quadtree
                      ) -> bool:
        """Determines if node1 can reach node2 directly."""
        direction = (node2.position - node1.position).normalize()
        normal = direction.rotate_rad(math.pi / 2)

        # Construct a box-cast of the Robot shape between the two nodes
        look_offset = direction * ROBOT_HITBOX_LENGTH / 2
        side_offset = normal * ROBOT_HITBOX_WIDTH / 2
        rectangle = [
            node1.position + side_offset,
            node1.position - side_offset,
            node2.position - side_offset + look_offset,
            node2.position + side_offset + look_offset
        ]

        # Get the bounding rect of the rectangle
        min_x, min_y = math.inf, math.inf
        max_x, max_y = -math.inf, -math.inf
        for vertex in rectangle:
            min_x = min(min_x, vertex.x)
            min_y = min(min_y, vertex.y)
            max_x = max(max_x, vertex.x)
            max_y = max(max_y, vertex.y)
        bounding_rectangle = Rect(min_x, min_y, max_x - min_x, max_y - min_y)

        # Query the quadtree with the bounding rectangle
        entities = quadtree.query(bounding_rectangle)
        # Note that `entities` must only consist of Walls, since this is
        # performed at the beginning of a round and is not intended to
        # consider collisions with other Entities

        # Check for polygon collisions with the original rectangle
        for entity in entities:
            if check_polygon_collision(entity.absolute_hitbox, rectangle):
                return False
        return True

    def get_closest_node(self, point: Vector2) -> Node:
        """Determines the closest node to a point."""
        j = int(point.y / NODE_SIZE)
        i = int(point.x / NODE_SIZE)
        return self.__nodes[j][i]

    def pathfind(self, point1: Vector2, point2: Vector2
                 ) -> Optional[list[Vector2]]:
        """Finds a path between point1 and point2 in the PathfindingGraph."""
        # First, determine if these points can map to nodes in the graph.
        rect = Rect(Vector2(), self.__size)
        if not rect.contains(Rect(point1, Vector2())):
            return None
        if not rect.contains(Rect(point2, Vector2())):
            return None

        node1 = self.get_closest_node(point1)
        node2 = self.get_closest_node(point2)

        node_path = Node.a_star(node1, node2)
        if node_path is None:
            return None

        return [node.position for node in node_path]

    def render(self, surface: pygame.Surface):
        """Draws the PathfindingGraph onto a surface."""
        for row in self.__nodes:
            for node in row:
                for neighbor in node.neighbors:
                    pygame.draw.line(surface, "#FF00FF", node.position,
                                     neighbor.position)

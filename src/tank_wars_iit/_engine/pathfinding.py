from __future__ import annotations
from collections import defaultdict
import heapq
import math
from typing import cast, Optional

import pygame

import tank_wars_iit._engine.arena as arena
from tank_wars_iit._engine.entity import Wall
from tank_wars_iit._engine.entity.robot import (ROBOT_MOVE_SPEED,
                                                ROBOT_TURN_SPEED)
from tank_wars_iit._engine.quadtree import Quadtree
from tank_wars_iit._engine.util import (angle_difference, can_see_walls,
                                        check_polygon_collision,
                                        is_point_in_polygon)

Vector2 = pygame.Vector2


def evaluate_cost(start: Vector2, rotation: float, end: Vector2):
    """
    Returns the cost of moving from start with defined rotation to end, in
    seconds.
    """
    difference = end - start
    distance_cost = difference.magnitude() / ROBOT_MOVE_SPEED

    angle = math.atan2(difference.y, difference.x)
    turn_cost = abs(angle_difference(rotation, angle)) / ROBOT_TURN_SPEED
    return distance_cost + turn_cost


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
    def a_star(start: Node, goal: Node, start_rotation: float
               ) -> Optional[list[Node]]:
        """Computes the path from start to goal using A*."""
        # Map of node to node preceding it on the path
        came_from = dict[Node, Node]()

        # Define h (heuristic) as distance between nodes
        def h(node: Node):
            rotation = 0
            if node == start:
                rotation = start_rotation
            elif node in came_from:
                previous = came_from[node]
                difference = node.position - previous.position
                rotation = math.atan2(difference.y, difference.x)
            return evaluate_cost(node.position, rotation, goal.position)
        h_start = h(start)

        # Heap of reachable nodes, sorted by f-value
        open_set = list[tuple[float, Node]]()
        heapq.heappush(open_set, (h_start, start))

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

            rotation = 0
            if current == start:
                rotation = start_rotation
            if current in came_from:
                previous = came_from[current]
                difference = current.position - previous.position
                rotation = math.atan2(difference.y, difference.x)

            for neighbor in current.neighbors:
                cost = evaluate_cost(current.position, rotation,
                                     neighbor.position)
                tentative_g_score = g_score[current] + cost
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
    def __init__(self, arena: arena.Arena):
        self.__arena = arena
        walls = cast(list[Wall], arena.get_entities_of_type(Wall))

        self.__construct_quadtree(walls)
        self.__create_graph(walls)

    def __construct_quadtree(self, walls: list[Wall]):
        """Constructs a pathfinding Quadtree with a list of walls."""
        self.__quadtree = Quadtree.from_objects(walls,
                                                lambda e: e.pathfinding_rect,
                                                lambda e: e.position)

    def __create_graph(self, walls: list[Wall]):
        hitboxes = list[list[Vector2]]()
        node_set = set[tuple[float, float]]()

        # Record all nodes, including ones that may be in other hitboxes
        for wall in walls:
            hitbox = wall.pathfinding_hitbox
            hitboxes.append(hitbox)
            for vertex in hitbox:
                node_set.add((vertex.x, vertex.y))

        remove_set = set[tuple[float, float]]()

        for i in range(len(hitboxes) - 1):
            for j in range(i + 1, len(hitboxes)):
                hitbox1 = hitboxes[i]
                hitbox2 = hitboxes[j]

                if not check_polygon_collision(hitbox1, hitbox2):
                    continue

                # Remove nodes contained in other hitboxes
                for vertex in hitbox1:
                    if is_point_in_polygon(vertex, hitbox2):
                        remove_set.add((vertex.x, vertex.y))
                for vertex in hitbox2:
                    if is_point_in_polygon(vertex, hitbox1):
                        remove_set.add((vertex.x, vertex.y))

        node_set.difference_update(remove_set)

        nodes = [Node(Vector2(x, y)) for x, y in node_set]

        # Set node position epsilon to a generous amount to account for
        # floating point error in can_see
        for node in nodes:
            node.position.epsilon = 1e-4

        # Connect nodes by visibility
        for i in range(len(nodes) - 1):
            node1 = nodes[i]
            for j in range(i + 1, len(nodes)):
                node2 = nodes[j]
                if can_see_walls(node1.position, node2.position,
                                 self.__quadtree):
                    node1.neighbors.append(node2)
                    node2.neighbors.append(node1)

        self.__nodes = nodes

    def get_visible_nodes(self, point: Vector2, rotation: Optional[float]):
        """Returns a list of up to 8 visible nodes, sorted by closeness."""
        def cost(node: Node):
            if rotation is not None:
                return evaluate_cost(point, rotation, node.position)
            else:
                return (point - node.position).magnitude_squared()

        node_costs = [(cost(node), node) for node in self.__nodes]

        sorted_nodes = sorted(node_costs)

        result = list[Node]()
        i = 0

        while (len(result) == 0 or i < 8) and i < len(sorted_nodes):
            _, node = sorted_nodes[i]
            if can_see_walls(point, node.position, self.__quadtree):
                result.append(node)
            i += 1

        return result

    def pathfind(self, start: Vector2, rotation: float, end: Vector2
                 ) -> Optional[list[Vector2]]:
        """Finds a path between start and end in the PathfindingGraph."""
        # Handle case where a straight line works
        if can_see_walls(start, end, self.__quadtree):
            return [start, end]

        # Create temporary start and end nodes.
        # NOTE: this won't work in parallel!
        start_node = Node(start)
        start_node.neighbors = self.get_visible_nodes(start, rotation)
        end_node = Node(end)
        end_neighbors = self.get_visible_nodes(end, None)
        for neighbor in end_neighbors:
            neighbor.neighbors.append(end_node)

        node_path = Node.a_star(start_node, end_node, rotation)

        # Remove end_node from it's neighbors' neighbors arrays
        for neighbor in end_neighbors:
            neighbor.neighbors.remove(end_node)

        if node_path is None:
            return None

        return [node.position for node in node_path]

    def get_available_nodes(self) -> list[Vector2]:
        """Returns positions of all nodes with at least one neighbor."""
        arena = self.__arena
        return [node.position
                for node in self.__nodes
                if len(node.neighbors) > 0
                if node.position.x > arena.origin.x
                if node.position.x < arena.origin.x + arena.size.x
                if node.position.y > arena.origin.y
                if node.position.y < arena.origin.y + arena.size.y]

    def render(self, surface: pygame.Surface):
        """Draws the PathfindingGraph onto a surface."""
        for node in self.__nodes:
            pygame.draw.circle(surface, "#FF00FF", node.position, 4)
            for neighbor in node.neighbors:
                pygame.draw.line(surface, "#FF00FF", node.position,
                                 neighbor.position)

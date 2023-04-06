from __future__ import annotations
import json
import math
from random import sample
from typing import Optional

import pygame

from engine.entity import Entity, Robot, Wall
from engine.map import is_map
from engine.pathfinding import PathfindingGraph
from engine.quadtree import Quadtree

Rect = pygame.Rect
Vector2 = pygame.Vector2

WALL_THICKNESS = 100
FRAME_RATE = 60
MAX_WINDOW_WIDTH = 1536
MAX_WINDOW_HEIGHT = 768


class Arena:
    """
    Class representing a round of Robot Wars.

    Contains and simulates Entities and provides rendering support.
    """
    def __init__(self, size: Vector2):
        self.__entities: list[Entity] = []
        self.__size = size
        self.__surface = pygame.Surface(size)
        self.__quadtree: Optional[Quadtree] = None
        self.__path_graph: Optional[PathfindingGraph] = None
        self.__paths = list[list[Vector2]]()

        self.spawns: list[Vector2] = []

        # Debug settings
        self.show_hitboxes = False
        self.show_fps = False
        self.show_quadtree = False
        self.show_nearest_robot = False
        self.show_path_graph = False
        self.show_paths = False
        self.show_robot_nodes = False

        # Add surrounding walls
        north_wall = Wall(Vector2(size.x / 2, -WALL_THICKNESS / 2 - 1),
                          Vector2(size.x, WALL_THICKNESS))
        south_wall = Wall(Vector2(size.x / 2, size.y + WALL_THICKNESS / 2 + 1),
                          Vector2(size.x, WALL_THICKNESS))
        west_wall = Wall(Vector2(-WALL_THICKNESS / 2 - 1, size.y / 2),
                         Vector2(WALL_THICKNESS, size.y))
        east_wall = Wall(Vector2(size.x + WALL_THICKNESS / 2 + 1, size.y / 2),
                         Vector2(WALL_THICKNESS, size.y))

        self.add_entity(north_wall)
        self.add_entity(south_wall)
        self.add_entity(west_wall)
        self.add_entity(east_wall)

    @property
    def entities(self) -> list[Entity]:
        """Read-only property that provides list of arena entities."""
        return self.__entities.copy()

    @property
    def surface(self) -> pygame.Surface:
        """
        Read-only property that provides reference to drawn arena surface.
        """
        return self.__surface

    @property
    def window_size(self) -> Vector2:
        """
        Read-only property that provides the size of the window surface.
        """
        window_rect = Rect(0, 0, MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT)
        arena_rect = Rect(Vector2(), self.__size)
        return Vector2(arena_rect.fit(window_rect).size)

    @staticmethod
    def from_map_json(filename: str) -> Optional[Arena]:
        """Constructs an Arena from a map config JSON file."""
        with open(filename, "r") as file:
            arena_data = json.load(file)
            assert is_map(arena_data), "Map JSON is malformed"

            arena_size = Vector2(arena_data["size"]["width"],
                                 arena_data["size"]["height"])
            arena = Arena(arena_size)

            for wall_data in arena_data["walls"]:
                wall_position = Vector2(wall_data["position"]["x"],
                                        wall_data["position"]["y"])
                wall_size = Vector2(wall_data["size"]["width"],
                                    wall_data["size"]["height"])
                wall = Wall(wall_position, wall_size,
                            math.radians(wall_data["rotation"]))
                arena.add_entity(wall)

            arena.spawns = [Vector2(spawn_data["x"], spawn_data["y"])
                            for spawn_data in arena_data["spawns"]]

            # Calculate pathfinding graph
            arena.prepare_path_graph()

            return arena

    def add_entity(self, entity: Entity):
        """
        Adds an entity to this Arena. Entity must not already be in the Arena.
        """
        assert entity not in self.__entities, "Entity already in Arena"

        entity.arena = self
        self.__entities.append(entity)

    def remove_entity(self, entity: Entity):
        """Removes an entity from this Arena. Entity must be in the Arena."""
        assert entity in self.__entities, "Entity not in Arena"

        self.__entities.remove(entity)
        entity.arena = None

    def spawn_robots(self, robots: list[Robot]):
        """
        Spawns a list of robots into unique spawn locations. The number of
        robots must be lower than the number of arena spawns.
        """
        assert len(robots) <= len(self.spawns), "# of entities > # of spawns"

        positions: list[Vector2] = sample(self.spawns, k=len(robots))

        for robot in robots:
            self.add_entity(robot)
            robot.position = positions.pop()

    def get_entities_of_type(self, typeVal: type) -> list[Entity]:
        """Returns a filtered list of entities of a certain class."""
        return [entity
                for entity in self.__entities
                if type(entity) is typeVal]

    def solve_collisions(self):
        """Solves collisions between entities."""
        assert self.__quadtree is not None, "Quadtree should exist"
        for entity1, entity2 in self.__quadtree.find_all_intersections():
            entity1.handle_collision(entity2)

    def nearest_robot(self, robot: Robot) -> Optional[Robot]:
        """Returns the Robot closest to another Robot."""
        # Robot.on_update may call this, and the quadtree won't exist on the
        # first update, so just return None
        if self.__quadtree is None:
            return None

        neighbor = self.__quadtree.nearest_neighbor(
            robot.position,
            lambda e: type(e) is Robot and e is not robot
        )
        assert neighbor is None or type(neighbor) is Robot, "Shouldn't happen"

        return neighbor

    def prepare_path_graph(self):
        """
        Prepares the PathfindingGraph for this Arena, based on the Walls it
        currently haves.
        """
        self.__construct_quadtree()
        assert self.__quadtree is not None
        self.__path_graph = PathfindingGraph(self.__size, self.__quadtree)

    def pathfind(self, robot: Robot, point: Vector2
                 ) -> Optional[list[Vector2]]:
        """
        Finds a path between the robot and a provided point, if there is one.
        """
        assert self.__path_graph is not None, "Path graph should exist"
        path = self.__path_graph.pathfind(robot.position, point)
        if self.show_paths and path is not None:
            self.__paths.append(path)
        return path

    def window_to_arena(self, point: Vector2) -> Vector2:
        """
        Converts a point on the window surface to a point on the arena surface.
        """
        ratio = self.__size.x / self.window_size.x
        return point * ratio

    def __filter_entities(self):
        """
        Filter out any entities that were destroyed during updating.

        An entity can be destroyed in various ways:

        * It destroyed itself (i.e. bullet reaches max distance)
        * It was destroyed by another entity (i.e. robot destroyed by bullet)

        An entity is destroyed if its `arena` field is set to `None`.
        """
        self.__entities[:] = [entity
                              for entity in self.__entities
                              if entity.arena is self]

    def __construct_quadtree(self):
        """Constructs a Quadtree with the entities in the arena."""
        # Calculate Quadtree bounds
        min_x, min_y = math.inf, math.inf
        max_x, max_y = -math.inf, -math.inf

        for entity in self.__entities:
            rect = entity.rect
            min_x = min(min_x, rect.left)
            min_y = min(min_y, rect.top)
            max_x = max(max_x, rect.right)
            max_y = max(max_y, rect.bottom)

        quadtree_top_left = Vector2(min_x, min_y)
        quadtree_size = Vector2(max_x - min_x, max_y - min_y)

        # Construct Quadtree
        self.__quadtree = Quadtree(Rect(quadtree_top_left, quadtree_size))
        for entity in self.__entities:
            self.__quadtree.add(entity)

    def __render_scene(self):
        """Renders the Arena onto self.__surface."""
        # Draw updated entities onto the surface
        for entity in self.__entities:
            entity.render(self.__surface)
        for entity in self.__entities:
            entity.post_render(self.__surface)

        # Draw hitboxes
        if self.show_hitboxes:
            for entity in self.__entities:
                pygame.draw.lines(self.__surface, "#FF0000", True,
                                  entity.absolute_hitbox)

        # Draw quadtree
        if self.show_quadtree:
            assert self.__quadtree, "Quadtree should exist"
            self.__quadtree.render(self.__surface)

        # Draw closest robot lines
        if self.show_nearest_robot:
            for robot in self.get_entities_of_type(Robot):
                assert type(robot) is Robot, "Shouldn't happen"

                closest = self.nearest_robot(robot)
                if closest is None:
                    continue

                point1 = robot.position
                point2 = closest.position

                middle = (point1 + point2) / 2
                direction = (point2 - point1).normalize()
                normal = direction.rotate_rad(math.pi / 2)

                tip_base = middle - direction * 8 * math.sqrt(3)
                tip_left = tip_base - normal * 8
                tip_right = tip_base + normal * 8

                pygame.draw.line(self.__surface, "#00FF00", point1, point2)
                pygame.draw.polygon(self.__surface, "#00FF00",
                                    [middle, tip_left, tip_right])

        # Draw pathfinding graph
        if self.show_path_graph:
            assert self.__path_graph is not None
            self.__path_graph.render(self.__surface)

        # Draw paths
        if self.show_paths:
            for path in self.__paths:
                if len(path) < 2:
                    continue
                pygame.draw.lines(self.__surface, "#FFFF00", False, path)
            # Clear paths to avoid memory leak
            self.__paths = []

        # Draw Robot nodes
        if self.show_robot_nodes:
            assert self.__path_graph is not None
            for robot in self.get_entities_of_type(Robot):
                node = self.__path_graph.get_closest_node(robot.position)
                pygame.draw.circle(self.__surface, "#00FFFF", node.position, 8)

    def update(self, dt: float):
        """Updates the state of the arena after time delta `dt`, in seconds."""
        # Fill the screen with a color to wipe away anything from last frame
        self.__surface.fill("#006600")

        # Update each entity's state
        for entity in self.__entities:
            entity.update(dt)

        # Filter destroyed entities
        self.__filter_entities()

        # Construct quadtree
        self.__construct_quadtree()

        # Solve collisions
        self.solve_collisions()

        # Filter destroyed entities (yes, again)
        self.__filter_entities()

        # Render the scene
        self.__render_scene()

    def run(self):
        """Runs simulation of the Arena."""
        has_path_graph = self.__path_graph is not None
        assert has_path_graph, ("Must call Arena.prepare_path_graph after "
                                "generating walls and before spawning other "
                                "entities!")

        # pygame setup
        pygame.init()

        window_size = self.window_size
        screen = pygame.display.set_mode(window_size)
        clock = pygame.time.Clock()
        running = True
        dt = 0

        # Font to render debug text
        font = pygame.font.SysFont("couriernew", 18)

        total_frames = 0
        total_time = 0

        while running:
            # Poll for events
            # pygame.QUIT event means the user clicked X to close the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            total_frames += 1
            total_time += dt

            # Simulate a time step
            # When dragging the window, the clock freezes and resumes once
            # finished dragging. This can cause large values of `dt`, which can
            # cause entities to move too far and avoid collisions, so we handle
            # that case here by splitting it into smaller time steps.
            remaining_dt = dt
            while remaining_dt > 10 / FRAME_RATE:
                self.update(10 / FRAME_RATE)
                remaining_dt -= 10 / FRAME_RATE
            self.update(remaining_dt)

            # Copy arena surface contents to screen
            ratio = self.__size.x / window_size.x
            if ratio > 2:
                # Use faster, normal scale if the ratio is too large
                pygame.transform.scale(self.__surface, window_size, screen)
            else:
                # Use slower, smooth scale if the ratio isn't too large
                pygame.transform.smoothscale(self.__surface, window_size,
                                             screen)

            # Draw framerate onto the screen
            if self.show_fps and dt > 0:
                screen.blit(
                    font.render(f"FPS: {int(1 / dt)}", False, "#FF0000",
                                "#000000"),
                    Vector2(),
                )

            # Display results on window
            pygame.display.flip()

            # Limits FPS to 60
            # `dt`` is delta time in seconds since last frame, used for
            # framerate-independent physics.
            dt = clock.tick(FRAME_RATE) / 1000

        pygame.quit()

        print(f"Overall FPS: {total_frames / total_time}")

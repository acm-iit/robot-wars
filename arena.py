import json
import math
import pygame
from random import sample
from typing import List, Optional

from entity import Entity
from map import is_map
from quadtree import Quadtree
from wall import Wall

Rect = pygame.Rect
Vector2 = pygame.Vector2

WALL_THICKNESS = 100
FRAME_RATE = 60
MAX_WINDOW_WIDTH = 1536
MAX_WINDOW_HEIGHT = 768

class Arena:
    def __init__(self, size: Vector2):
        self.__entities: List[Entity] = []
        self.__size = size
        self.__surface = pygame.Surface(size)

        self.spawns: List[Vector2] = []
        self.show_hitboxes = False
        self.show_fps = False

        # Add surrounding walls
        self.add_entity(Wall(Vector2(size.x / 2, -WALL_THICKNESS / 2 - 1), Vector2(size.x, WALL_THICKNESS)))
        self.add_entity(Wall(Vector2(size.x / 2, size.y + WALL_THICKNESS / 2 + 1), Vector2(size.x, WALL_THICKNESS)))
        self.add_entity(Wall(Vector2(-WALL_THICKNESS / 2 - 1, size.y / 2), Vector2(WALL_THICKNESS, size.y)))
        self.add_entity(Wall(Vector2(size.x + WALL_THICKNESS / 2 + 1, size.y / 2), Vector2(WALL_THICKNESS, size.y)))

    @property
    def entities(self) -> List[Entity]:
        """
        Read-only property that provides list of arena entities.
        """
        return self.__entities.copy()

    @property
    def surface(self) -> pygame.Surface:
        """
        Read-only property that provides reference to drawn arena surface
        """
        return self.__surface

    @staticmethod
    def from_map_json(filename: str) -> Optional["Arena"]:
        """
        Constructs an Arena from a map config JSON file.
        """
        with open(filename, "r") as file:
            arena_data = json.load(file)
            assert is_map(arena_data), "Map JSON is malformed"

            arena_size = Vector2(arena_data["size"]["width"], arena_data["size"]["height"])
            arena = Arena(arena_size)

            for wall_data in arena_data["walls"]:
                wall_position = Vector2(wall_data["position"]["x"], wall_data["position"]["y"])
                wall_size = Vector2(wall_data["size"]["width"], wall_data["size"]["height"])
                arena.add_entity(Wall(wall_position, wall_size, math.radians(wall_data["rotation"])))

            arena.spawns = [Vector2(spawn_data["x"], spawn_data["y"]) for spawn_data in arena_data["spawns"]]

            return arena

    def add_entity(self, entity: Entity):
        """
        Adds an entity to this Arena. Entity must not already be in the Arena.
        """
        assert entity not in self.__entities, "Entity already in Arena"

        entity.arena = self
        self.__entities.append(entity)

    def remove_entity(self, entity: Entity):
        """
        Removes an entity from this Arena. Entity must be in the Arena.
        """
        assert entity in self.__entities, "Entity not in Arena"
        
        self.__entities.remove(entity)
        entity.arena = None

    def spawn_entities(self, entities: List[Entity]):
        """
        Spawns a list of entities into unique spawn locations.
        The number of entities must be lower than the number of arena spawns.
        """
        assert len(entities) <= len(self.spawns), "Not enough spawns for amount of entities"

        positions: List[Vector2] = sample(self.spawns, k=len(entities))

        for entity in entities:
            self.add_entity(entity)
            entity.position = positions.pop()

    def get_entities_of_type(self, typeVal: type) -> List[Entity]:
        """
        Returns a filtered list of entities of a certain class.
        """
        return [entity for entity in self.__entities if type(entity) is typeVal]

    def solve_collisions(self, quadtree: Quadtree):
        """
        Solves collisions between entities.
        """
        for entity1, entity2 in quadtree.find_all_intersections():
            entity1.handle_collision(entity2)


    def __construct_quadtree(self) -> Quadtree:
        """
        Constructs a Quadtree with the entities in the arena.
        """
        # Calculate Quadtree bounds
        min_x = min(point.x for entity in self.__entities for point in entity.absolute_hitbox) - 10
        min_y = min(point.y for entity in self.__entities for point in entity.absolute_hitbox) - 10
        max_x = max(point.x for entity in self.__entities for point in entity.absolute_hitbox) + 10
        max_y = max(point.y for entity in self.__entities for point in entity.absolute_hitbox) + 10

        quadtree_top_left = Vector2(min_x, min_y)
        quadtree_size = Vector2(max_x, max_y) - quadtree_top_left

        # Construct Quadtree
        quadtree = Quadtree(Rect(quadtree_top_left, quadtree_size))
        for entity in self.__entities:
            quadtree.add(entity)

        return quadtree

    def update(self, dt: float):
        """
        Updates the state of the arena after time delta `dt`, in seconds.
        """
        # Fill the screen with a color to wipe away anything from last frame
        self.__surface.fill("#006600")

        # Update each entity's state
        for entity in self.__entities:
            entity.update(dt)
        
        # Filter out any entities that were destroyed during updating
        # An entity can be destroyed in various ways:
        #   1) It destroyed itself (i.e. bullet reaches max distance)
        #   2) It was destroyed by another entity (i.e. robot destroyed by bullet)
        # An entity is destroyed if its `arena` field is set to `None`.
        self.__entities[:] = [entity for entity in self.__entities if entity.arena is self]

        # Construct quadtree
        quadtree = self.__construct_quadtree()

        # Solve collisions
        self.solve_collisions(quadtree)

        # Draw updated entities onto the surface
        for entity in self.__entities:
            entity.render(self.__surface)

        # Draw hitboxes
        if self.show_hitboxes:
            for entity in self.__entities:
                pygame.draw.lines(self.__surface, "#FF0000", True, entity.absolute_hitbox)

    def run(self):
        """
        Runs simulation of the Arena.
        """
        # pygame setup
        pygame.init()

        # Clamp window size to be scaled down version of arena size
        window_size = self.__size.copy()
        if window_size.x > MAX_WINDOW_WIDTH:
            window_size *= MAX_WINDOW_WIDTH / window_size.x
        if window_size.y > MAX_WINDOW_HEIGHT:
            window_size *= MAX_WINDOW_HEIGHT / window_size.y

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
            # When dragging the window, the clock freezes and resumes once finished dragging.
            # This can cause large values of `dt`, which can cause entities to move too far
            # and avoid collisions, so we handle that case here by splitting it into smaller
            # time steps.
            remaining_dt = dt
            while remaining_dt > 10 / FRAME_RATE:
                self.update(10 / FRAME_RATE)
                remaining_dt -= 10 / FRAME_RATE
            self.update(remaining_dt)

            # Copy arena surface contents to screen
            pygame.transform.smoothscale(self.__surface, window_size, screen)

            # Draw framerate onto the screen
            if self.show_fps and dt > 0:
                screen.blit(
                    font.render(f"FPS: {int(1 / dt)}", False, "#FF0000", "#000000"),
                    Vector2(),
                )

            # Display results on window
            pygame.display.flip()

            # Limits FPS to 60
            # `dt`` is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = clock.tick(FRAME_RATE) / 1000

        pygame.quit()

        print(f"Overall FPS: {total_frames / total_time}")

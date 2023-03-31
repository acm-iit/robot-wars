import pygame
from typing import List

from entity import Entity
from wall import Wall

Vector2 = pygame.Vector2

WALL_THICKNESS = 100

class Arena:
    def __init__(self, size: Vector2):
        self.__entities: List[Entity] = []
        self.show_hitboxes = False
        self.__size = size
        self.__surface = pygame.Surface(size)

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
    def size(self) -> pygame.Surface:
        """
        Read-only property that provides reference to drawn arena surface
        """
        return self.__surface

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

    def get_entities_of_type(self, typeVal: type) -> List[Entity]:
        """
        Returns a filtered list of entities of a certain class.
        """
        return [entity for entity in self.__entities if type(entity) is typeVal]

    def solve_collisions(self):
        """
        Solves collisions between entities.
        """
        for i in range(len(self.__entities)-1):
            for j in range(i+1, len(self.__entities)):
                entity1 = self.__entities[i]
                entity2 = self.__entities[j]

                entity1.handle_collision(entity2)

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

        # Solve collisions
        self.solve_collisions()

        # Draw updated entities onto the surface
        for entity in self.__entities:
            entity.render(self.__surface)
            if self.show_hitboxes:
                pygame.draw.lines(self.__surface, "#FF0000", True, entity.absolute_hitbox)

    def run(self):
        """
        Runs simulation of the Arena.
        """
        # pygame setup
        pygame.init()
        screen = pygame.display.set_mode(self.__size)
        clock = pygame.time.Clock()
        running = True
        dt = 0

        while running:
            # Poll for events
            # pygame.QUIT event means the user clicked X to close the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Simulate a time step
            self.update(dt)

            # Copy arena surface contents to screen
            pygame.transform.scale(self.__surface, self.__size, screen)
            pygame.display.flip()

            # Limits FPS to 60
            # `dt`` is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = clock.tick(60) / 1000

        pygame.quit()

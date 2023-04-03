import pygame

import engine.entity as entity

Vector2 = pygame.Vector2

class Wall(entity.Entity):
    """
    Entity resembling an unmovable wall.
    """
    def __init__(self, position: Vector2, size: Vector2, rotation: float = 0):
        super().__init__()
        self.position = position
        self.rotation = rotation
        self.__size = size

    @property
    def hitbox(self) -> list[Vector2]:
        half_size = self.__size / 2
        return [
            half_size,
            Vector2(half_size.x, -half_size.y),
            -half_size,
            Vector2(-half_size.x, half_size.y)
        ]

    @property
    def is_static(self) -> bool:
        return True

    def render(self, screen: pygame.Surface):
        pygame.draw.polygon(screen, "#AAAAAA", self.absolute_hitbox)
import pygame
from typing import List

from entity import Entity

Vector2 = pygame.Vector2

class Wall(Entity):
    """
    Entity resembling an unmovable wall.
    """
    def __init__(self, position: Vector2, size: Vector2, rotation: float = 0):
        super().__init__()
        self.position = position
        self.rotation = rotation
        self.__size = size

    @property
    def hitbox(self) -> List[Vector2]:
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
        """
        Renders the wall onto the screen.
        """
        pygame.draw.polygon(screen, "#AAAAAA", self.absolute_hitbox)

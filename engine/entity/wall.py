import pygame

import engine.entity as entity
from engine.entity.robot import ROBOT_HITBOX_WIDTH

Vector2 = pygame.Vector2


class Wall(entity.Entity):
    """Entity resembling an unmovable wall."""
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
    def pathfinding_hitbox(self) -> list[Vector2]:
        """
        Hitbox of the Wall expanded by the Robot agent radius, in absolute
        coordinates.
        """
        half_size = self.__size / 2
        half_size_reflect = Vector2(half_size.x, -half_size.y)
        robot_size = Vector2(ROBOT_HITBOX_WIDTH + 2) / 2
        robot_size_reflect = Vector2(robot_size.x, -robot_size.y)
        expanded = [
            half_size + robot_size,
            half_size_reflect + robot_size_reflect,
            -half_size - robot_size,
            -half_size_reflect - robot_size_reflect
        ]
        return [vertex.rotate_rad(self.rotation) + self.position
                for vertex in expanded]

    @property
    def is_static(self) -> bool:
        return True

    def render(self, screen: pygame.Surface):
        pygame.draw.polygon(screen, "#AAAAAA", self.absolute_hitbox)

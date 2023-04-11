import math

import pygame

import engine.entity as entity

Vector2 = pygame.Vector2

NUM_HITBOX_VERTICES = 3
COIN_RADIUS = 8


class Coin(entity.Entity):
    """
    Coin spread throughout the map which Robots collect for their secondary
    objective.
    """
    def __init__(self, position: Vector2):
        super().__init__()
        self.position = position

    def hitbox(self) -> list[Vector2]:
        dangle = 2 * math.pi / NUM_HITBOX_VERTICES
        return [Vector2(COIN_RADIUS, 0).rotate_rad(i * dangle)
                for i in range(NUM_HITBOX_VERTICES)]

    def render(self, screen: pygame.Surface):
        pygame.draw.circle(screen, "#FFFF00", self.position, COIN_RADIUS)

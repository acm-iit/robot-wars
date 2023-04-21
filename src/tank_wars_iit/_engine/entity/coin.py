import math

import pygame

import tank_wars_iit._engine.entity as entity

Surface = pygame.Surface
Vector2 = pygame.Vector2

NUM_HITBOX_VERTICES = 3
COIN_RADIUS = 24
COIN_COLOR = "#FFCD38"
COIN_BORDER_THICKNESS = 6
COIN_BORDER_COLOR = "#C79B22"


class Coin(entity.Entity):
    """
    Coin spread throughout the map which Robots collect for their secondary
    objective.
    """
    def __init__(self, position: Vector2):
        super().__init__()
        self.position = position
        self.__animation_alpha = 0      # Animation progress in [0, 1)

    @property
    def hitbox(self) -> list[Vector2]:
        dangle = 2 * math.pi / NUM_HITBOX_VERTICES
        return [Vector2(COIN_RADIUS, 0).rotate_rad(i * dangle)
                for i in range(NUM_HITBOX_VERTICES)]

    @property
    def reacts_to_collisions(self) -> bool:
        # Prevent collision reactions
        return False

    def on_collide(self, other: entity.Entity, _: Vector2):
        # Only award coin if it's alive and it touches a Robot
        if self.arena is None or type(other) is not entity.Robot:
            return
        # Award coin and destroy Coin
        other.coins += 1
        self.destroy()

    def update(self, dt: float):
        self.__animation_alpha += dt
        self.__animation_alpha %= 1

    def render(self, screen: Surface):
        surface_size = Vector2(COIN_RADIUS * 2, COIN_RADIUS * 2)
        coin_surface = Surface(surface_size, flags=pygame.SRCALPHA)

        pygame.draw.circle(coin_surface, COIN_BORDER_COLOR, surface_size / 2,
                           COIN_RADIUS)

        inner_radius = COIN_RADIUS - COIN_BORDER_THICKNESS
        pygame.draw.circle(coin_surface, COIN_COLOR, surface_size / 2,
                           inner_radius)

        angle = self.__animation_alpha * 2 * math.pi
        coin_width = COIN_RADIUS * abs(math.cos(angle)) * 2
        coin_size = Vector2(coin_width, COIN_RADIUS * 2)
        coin_surface = pygame.transform.smoothscale(coin_surface, coin_size)

        screen.blit(coin_surface, self.position - coin_size / 2)

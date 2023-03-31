import math
import pygame
from typing import List

from entity import Entity
import robot
from wall import Wall

Vector2 = pygame.Vector2

BULLET_RADIUS = 8
BULLET_COLOR = "#222222"

NUM_HITBOX_VERTICES = 3

class Bullet(Entity):
    def __init__(self, rotation: float, origin: "robot.Robot"):
        super().__init__()
        self.__lifetime = 1.2
        self.__speed = 450
        self.rotation = rotation
        self.origin = origin
        self.collision_filter.add(origin)

    @property
    def hitbox(self) -> List[Vector2]:
        return [
            Vector2(BULLET_RADIUS, 0).rotate_rad(i * 2 * math.pi / NUM_HITBOX_VERTICES)
            for i in range(NUM_HITBOX_VERTICES)
        ]

    @property
    def is_static(self) -> bool:
        return False

    def update(self, dt: float):
        """
        Updates the lifetime of the bullet after a time delta `dt`, in seconds.
        """
        assert self.arena is not None, "Bullet does not have a corresponding Arena"

        self.position += Vector2(self.__speed * dt, 0).rotate_rad(self.rotation)
        self.__lifetime -= dt

        if self.__lifetime < 0:
            self.destroy()
            return

        # Check for collisions
        for enemy in self.arena.get_entities_of_type(robot.Robot):
            if enemy is self.origin:
                continue

            is_colliding, _ = self.is_colliding_with(enemy)
            if is_colliding:
                self.destroy()
                return

        for wall in self.arena.get_entities_of_type(Wall):
            is_colliding, normal = self.is_colliding_with(wall)
            
            if is_colliding:
                direction = Vector2(1, 0).rotate_rad(self.rotation).reflect(normal)
                self.rotation = math.atan2(direction.y, direction.x)

    def render(self, screen: pygame.Surface):
        """
        Renders the bullet onto the screen.
        """
        pygame.draw.circle(screen, BULLET_COLOR, self.position, BULLET_RADIUS)

import math
import pygame

from engine.draw_util import draw_gradient_path
from engine.entity import Entity
import engine.robot
from engine.wall import Wall

Vector2 = pygame.Vector2

BULLET_RADIUS = 8
BULLET_COLOR = "#222222"

TRAIL_LENGTH = 128
TRAIL_HEAD_COLOR = "#AAAAAA60"
TRAIL_TAIL_COLOR = "#AAAAAA00"

NUM_HITBOX_VERTICES = 3

class Bullet(Entity):
    def __init__(self, position: Vector2, rotation: float, origin: "engine.robot.Robot"):
        super().__init__()
        self.__lifetime = 2                     # Lifetime of the bullet, in seconds
        self.__speed = 500                      # Speed of the bullet, in pixels/sec
        self.origin = origin                    # Robot from which this bullet was created

        # Add origin to collision filter
        self.collision_filter.add(origin)

        # Set starting position and rotation
        self.position = position
        self.rotation = rotation

        # Vertices of bullet path
        self.__path: list[Vector2] = [self.position]

    @property
    def hitbox(self) -> list[Vector2]:
        return [
            Vector2(BULLET_RADIUS, 0).rotate_rad(i * 2 * math.pi / NUM_HITBOX_VERTICES)
            for i in range(NUM_HITBOX_VERTICES)
        ]

    @property
    def reacts_to_collisions(self) -> bool:
        return False

    def on_collide(self, other: Entity, translation: Vector2):
        if other is self.origin:
            return

        if type(other) is engine.robot.Robot:
            other.destroy()
            self.destroy()
        elif type(other) is Wall:
            # Fix collision
            self.position += translation

            # If the dot product is positive, then the normal is in the same direction as movement, so we don't reflect
            if Vector2(1, 0).rotate_rad(self.rotation).dot(translation) > 0:
                return

            # Add collision point to path
            self.__path.append(self.position)

            direction = Vector2(1, 0).rotate_rad(self.rotation).reflect(translation.normalize())
            self.rotation = math.atan2(direction.y, direction.x)

    def __compute_trail_vertices(self) -> list[Vector2]:
        """
        Computes vertices of the drawn trail and prunes old vertices from Bullet.__path
        """
        vertices = [self.position]
        total_distance = 0

        for i in range(len(self.__path)):
            vertex1 = vertices[i]
            vertex2 = self.__path[-i - 1]

            distance = (vertex1 - vertex2).magnitude()

            if total_distance + distance >= TRAIL_LENGTH:
                # Insert a vertex between vertex1 and vertex2 that caps length at TRAIL_LENGTH
                vertices.append(vertex1.lerp(vertex2, (TRAIL_LENGTH - total_distance) / distance))

                # Remove old vertices from self.__path that are too far away
                self.__path = self.__path[-i - 1:]
                break

            total_distance += distance
            vertices.append(vertex2)

        return vertices

    def update(self, dt: float):
        assert self.arena is not None, "Bullet does not have a corresponding Arena"

        self.position += Vector2(self.__speed * dt, 0).rotate_rad(self.rotation)
        self.__lifetime -= dt

        if self.__lifetime < 0:
            self.destroy()
            return

    def render(self, screen: pygame.Surface):
        # Draw trail
        draw_gradient_path(
            screen, TRAIL_HEAD_COLOR, TRAIL_TAIL_COLOR, self.__compute_trail_vertices(),
            BULLET_RADIUS * 2
        )

        # Draw bullet circle
        pygame.draw.circle(screen, BULLET_COLOR, self.position, BULLET_RADIUS)

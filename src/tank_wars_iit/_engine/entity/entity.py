from __future__ import annotations
import math
from typing import Optional

import pygame

import tank_wars_iit._engine.arena as arena
import tank_wars_iit._engine.util as util

Rect = pygame.Rect
Vector2 = pygame.Vector2


class Entity:
    """
    Object that can be rendered within an Arena. This is an abstract class for
    common entity behaviors. It is not meant to be instantiated in practice.
    Other classes, like the Robot, Bullet, and Wall, inherit this class.
    """
    def __init__(self):
        self.position = Vector2()
        self.rotation = 0
        self.arena: Optional[arena.Arena] = None        # Containing Arena
        self.collision_filter: set[Entity] = set()      # No-collide set

        # Cached absolute hitbox, w/ position and rotation
        self.__cached_ah: tuple[list[Vector2], Vector2, float] | None = None
        self.__cached_rect: tuple[Rect, Vector2, float] | None = None

    # Separate vector attributes into getter/setter to force copy on assign.
    # Otherwise, one could assign a position to an entity and then update that
    # entity's position via the original vector value!
    @property
    def position(self) -> Vector2:
        return self.__position.copy()

    @position.setter
    def position(self, position: Vector2):
        self.__position = position.copy()

    # Separate angle into getter/setter to keep it modulo 2pi
    @property
    def rotation(self) -> float:
        return self.__rotation

    @rotation.setter
    def rotation(self, rotation: float):
        self.__rotation = rotation % (2 * math.pi)

    @property
    def hitbox(self) -> list[Vector2]:
        """
        Hitbox of this entity, as a list of vertices in order (without position
        and rotation offset).
        """
        return [Vector2(1, 1), Vector2(1, -1), Vector2(-1, -1), Vector2(-1, 1)]

    @property
    def absolute_hitbox(self) -> list[Vector2]:
        """Absolute positions of entity hitbox vertices, in order."""
        # Return cached hitbox if it exists and is in the same place
        if self.__cached_ah is not None:
            old_hitbox, old_position, old_rotation = self.__cached_ah
            if old_position == self.position and old_rotation == self.rotation:
                return old_hitbox

        hitbox = [vertex.rotate_rad(self.rotation) + self.position
                  for vertex in self.hitbox]

        self.__cached_ah = (hitbox, self.position, self.rotation)

        return hitbox

    @property
    def rect(self) -> Rect:
        """Axis-aligned bounding rectangle of the entity."""
        # Return cached rect if it exists and is in the same place
        if self.__cached_rect is not None:
            old_rect, old_position, old_rotation = self.__cached_rect
            if old_position == self.position and old_rotation == self.rotation:
                return old_rect

        min_x, min_y = math.inf, math.inf
        max_x, max_y = -math.inf, -math.inf

        for point in self.absolute_hitbox:
            min_x = min(min_x, point.x)
            min_y = min(min_y, point.y)
            max_x = max(max_x, point.x)
            max_y = max(max_y, point.y)

        rect = Rect(Vector2(min_x, min_y),
                    Vector2(max_x - min_x, max_y - min_y))

        self.__cached_rect = (rect, self.position, self.rotation)

        return rect

    @property
    def is_static(self) -> bool:
        """If this entity is static, it cannot move or be displaced."""
        return False

    @property
    def reacts_to_collisions(self) -> bool:
        """
        If `False`, then the physics reaction to collision will be omitted. The
        `on_collide` method will still be called.
        """
        return True

    def update(self, dt: float):
        """Update the entity's state after a time delta `dt`, in seconds."""
        pass

    def render(self, screen: pygame.Surface):
        """Renders the entity onto a screen."""
        pass

    def post_render(self, screen: pygame.Surface):
        """Second stage of rendering, once all entities have rendered."""
        pass

    def destroy(self):
        """Removes the entity from its parent arena."""
        # TODO: Commented out the below assert temporarily, since this method
        # is idempotent. If this changes in the future, we need to uncomment
        # this assert and fix cases where it is triggered.
        # assert self.arena is not None, "Entity has already been destroyed"
        self.arena = None

    def on_collide(self, other: Entity, translation: Vector2):
        """Called when this entity collides with another entity."""
        pass

    def is_colliding_with(self, other: Entity) -> tuple[bool, Vector2]:
        """Determines if this entity is colliding with another entity."""
        if other in self.collision_filter or self in other.collision_filter:
            return False, Vector2()

        self_hitbox = self.absolute_hitbox
        other_hitbox = other.absolute_hitbox

        is_colliding = util.check_polygon_collision(self_hitbox, other_hitbox)
        if is_colliding:
            translation = util.get_minimum_translation_vector(self_hitbox,
                                                              other_hitbox)
            return True, translation
        else:
            return False, Vector2()

    def handle_collision(self, other: Entity):
        """
        Handles potential collision between this entity and another entity.
        """
        # If both entities are static, then collisions don't matter
        if self.is_static and other.is_static:
            return

        is_colliding, translation = self.is_colliding_with(other)

        if not is_colliding or translation.magnitude() == 0:
            return

        # Call both entity's `on_collide` method
        self.on_collide(other, translation)
        other.on_collide(self, -translation)

        # If one or more of the entities has react_to_collisions = False, then
        # don't displace them
        if not self.reacts_to_collisions or not other.reacts_to_collisions:
            return

        if not self.is_static and not other.is_static:
            # Displace both entities equally if both are dynamic
            self.position += translation / 2
            other.position -= translation / 2
        elif not self.is_static:
            # Displace only this entity if the other entity is static
            self.position += translation
        elif not other.is_static:
            # Displace only the other entity if this entity is static
            other.position -= translation

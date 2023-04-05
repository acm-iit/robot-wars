from __future__ import annotations
import math
from typing import Callable, Optional

import pygame

import engine.entity as entity

Rect = pygame.Rect
Vector2 = pygame.Vector2

# Dimensional constants (in pixels)
ROBOT_LENGTH = 120                  # Length of robot
ROBOT_WIDTH = 100                   # Width of robot
ROBOT_HEAD_RADIUS = 40              # Radius of robot's head
TURRET_LENGTH = 70                  # Length of turret barrel
TURRET_WIDTH = 16                   # Width of turret barrel
TREAD_LENGTH = 136                  # Length of treads on sides of robot
TREAD_WIDTH = 30                    # Width of treads on sides of robot
ARROW_SIZE = 10                     # Size of arrow to denote front of robot

NUM_TREAD_SEGMENTS = 6              # Number of lines on treads

# Color constants
ROBOT_COLOR = "#EE0000"             # Color of robot's body (rectangle)
ROBOT_HEAD_COLOR = "#CC0000"        # Color of robot's head (circle)
TURRET_COLOR = "#AAAAAA"            # Color of robot's turret barrel
TREADS_COLOR = "#888888"            # Color of robot's treads
TREADS_LINES_COLOR = "#555555"      # Color of lines on robot's treads
ARROW_COLOR = "#AAAAAA"             # Color of robot front arrow

MAX_HEALTH = 100                    # Default max robot health
HEALTH_COLOR = "#00BB00"            # Color of available health bar
HEALTH_DEFICIT_COLOR = "#CC0000"    # Color of deficit in health bar
HEALTH_BAR_LENGTH = 80              # Length of health bar
HEALTH_BAR_WIDTH = 8                # Width of health bar


def angle_difference(angle1: float, angle2: float) -> float:
    """
    Returns the angle difference that should be added to angle1 to direct it
    towards angle2.
    """
    diff = (angle2 - angle1) % (2 * math.pi)
    if diff < math.pi:
        return diff
    else:
        # The shorter direction is counter-clockwise
        return -(2 * math.pi - diff)


class Robot(entity.Entity):
    """Robot entity that can move, turn, and shoot."""
    def __init__(self):
        super().__init__()

        self.on_update: Optional[Callback] = None   # Callback on each `update`

        self.health = MAX_HEALTH                    # Robot health

        self.move_power = 0                         # Range: [-1, 1]
        self.turn_power = 0                         # Range: [-1, 1]
        self.turret_turn_power = 0                  # Range: [-1, 1]

        self.color = ROBOT_COLOR                    # Color of robot body
        self.head_color = ROBOT_HEAD_COLOR          # Color of robot head

        self.turret_rotation = 0                    # Turret rotation (radians)

        self.__move_speed = 300                     # Maximum move speed
        self.__turn_speed = math.pi                 # Maximum turn speed
        self.__turret_turn_speed = 1.5 * math.pi    # Maximum turret turn speed

        self.__left_tread_alpha = 0                 # Range: [0, 1)
        self.__right_tread_alpha = 0                # Range: [0, 1)

        self.__shot_cooldown = 0.5                  # Shoot cooldown (seconds)
        self.__time_until_next_shot = 0             # Remaining cooldown

    @property
    def hitbox(self) -> list[Vector2]:
        length = max(ROBOT_LENGTH, TREAD_LENGTH)
        width = ROBOT_WIDTH + TREAD_WIDTH
        return [
            Vector2(length / 2, width / 2),
            Vector2(length / 2, -width / 2),
            Vector2(-length / 2, -width / 2),
            Vector2(-length / 2, width / 2)
        ]

    @property
    def turret_rotation(self) -> float:
        """Rotation of the Robot's turret."""
        return self.__turret_rotation

    @turret_rotation.setter
    def turret_rotation(self, turret_rotation: float):
        self.__turret_rotation = turret_rotation % (2 * math.pi)

    @property
    def health(self) -> float:
        """Remaining health points of the Robot."""
        return self.__health

    @health.setter
    def health(self, health: float):
        self.__health = max(health, 0)

        # Destroy the robot if it runs out of health
        if self.__health == 0:
            self.destroy()

    @property
    def nearest_robot(self) -> Optional[Robot]:
        if self.arena is None:
            return
        return self.arena.nearest_robot(self)

    # We separate the `X_power` members into properties with specialized
    # setters so that we can clamp the values between [-1, 1].
    @property
    def move_power(self) -> float:
        """
        `move_power` is the current translational velocity of the robot,
        represented as a fraction of maximum movement speed.

        It is clamped between [-1, 1], where positive values of `move_power`
        correspond to moving forwards, while negative values correspond to
        moving backwards.
        """
        return self.__move_power

    @move_power.setter
    def move_power(self, move_power: float):
        self.__move_power = min(max(move_power, -1), 1)

    @property
    def turn_power(self) -> float:
        """
        `turn_power` is the current rotational velocity of the robot,
        represented as a fraction of maximum turning speed.

        It is clamped between [-1, 1], where positive values of `turn_power`
        correspond to turning clockwise, while negative values correspond to
        turning counter-clockwise.
        """
        return self.__turn_power

    @turn_power.setter
    def turn_power(self, turn_power: float):
        self.__turn_power = min(max(turn_power, -1), 1)

    @property
    def turret_turn_power(self) -> float:
        """
        `turret_turn_power` is the current rotational velocity of the robot's
        turret, represented as a fraction of maximum turret turning speed.

        It is clamped between [-1, 1], where positive values of
        `turret_turn_power` correspond to turning clockwise, while negative
        values correspond to turning counter-clockwise.
        """
        return self.__turret_turn_power

    @turret_turn_power.setter
    def turret_turn_power(self, turret_turn_power: float):
        self.__turret_turn_power = min(max(turret_turn_power, -1), 1)

    def __move(self, dt: float):
        """
        Moves the robot according to current `move_power`.

        `dt` represents the time delta in seconds.
        """
        displacement = self.__move_speed * self.move_power * dt
        self.position += Vector2(displacement, 0).rotate_rad(self.rotation)

        # Calculate tread segments/sec speed
        tread_speed = self.__move_speed / (TREAD_LENGTH / NUM_TREAD_SEGMENTS)
        # Move treads
        self.__left_tread_alpha += tread_speed * self.move_power * dt
        self.__right_tread_alpha += tread_speed * self.move_power * dt
        self.__left_tread_alpha %= 1
        self.__right_tread_alpha %= 1

    def __turn(self, dt: float):
        """
        Turns the robot according to current `turn_power`.

        `dt` represents the time delta in seconds.
        """
        drotation = self.__turn_speed * self.turn_power * dt
        self.rotation += drotation

        # Calculate tread segments/sec speed
        side_speed = (self.__turn_speed * ROBOT_WIDTH / 2)
        tread_speed = side_speed / (TREAD_LENGTH / NUM_TREAD_SEGMENTS)
        # Move treads
        self.__left_tread_alpha += tread_speed * self.turn_power * dt
        self.__right_tread_alpha -= tread_speed * self.turn_power * dt
        self.__left_tread_alpha %= 1
        self.__right_tread_alpha %= 1

    def __turn_turret(self, dt: float):
        """
        Turns the robot's turret according to current `turret_turn_power`.

        `dt` represents the time delta in seconds.
        """
        dturret = self.__turret_turn_speed * self.turret_turn_power * dt
        self.turret_rotation += dturret

    def shoot(self):
        """Makes the robot shoot a bullet in the direction of its turret."""
        assert self.arena is not None, "Robot doesn't have corresponding Arena"

        if self.__time_until_next_shot > 0:
            return

        offset = Vector2(TURRET_LENGTH, 0).rotate_rad(self.turret_rotation)
        position = self.position + offset
        bullet = entity.Bullet(position, self.turret_rotation, self)
        self.arena.add_entity(bullet)

        self.__time_until_next_shot = self.__shot_cooldown

    def aim_towards(self, point: Vector2, dt: float):
        """
        Sets the turret_turn_power such that the turret will aim towards a
        specified point.
        """
        direction = point - self.position

        current_angle = self.turret_rotation
        desired_angle = math.atan2(direction.y, direction.x)

        difference = angle_difference(current_angle, desired_angle)
        self.turret_turn_power = difference / (self.__turret_turn_speed * dt)

    def update(self, dt: float):
        if self.on_update is not None:
            self.on_update(self, dt)
        self.__move(dt)
        self.__turn(dt)
        self.__turn_turret(dt)

        # Update shot cooldown
        self.__time_until_next_shot = max(self.__time_until_next_shot - dt, 0)

    def render(self, screen: pygame.Surface):
        # Pixel offsets of treads vertices relative to the center of the treads
        tread_vertex_offsets = [
            Vector2(TREAD_LENGTH / 2, TREAD_WIDTH / 2),
            Vector2(TREAD_LENGTH / 2, -TREAD_WIDTH / 2),
            Vector2(-TREAD_LENGTH / 2, -TREAD_WIDTH / 2),
            Vector2(-TREAD_LENGTH / 2, TREAD_WIDTH / 2)
        ]

        # Vertices (in absolute coordinates) of the left and right treads
        left_tread_vertices = [
            self.position + (Vector2(0, -ROBOT_WIDTH / 2)
                             + tread_offset).rotate_rad(self.rotation)
            for tread_offset in tread_vertex_offsets
        ]
        right_tread_vertices = [
            self.position + (Vector2(0, ROBOT_WIDTH / 2)
                             + tread_offset).rotate_rad(self.rotation)
            for tread_offset in tread_vertex_offsets
        ]

        # Draw treads rectangles
        pygame.draw.polygon(screen, TREADS_COLOR, left_tread_vertices)
        pygame.draw.polygon(screen, TREADS_COLOR, right_tread_vertices)

        # Length of each tread segment
        segment_length = TREAD_LENGTH / NUM_TREAD_SEGMENTS

        # Draw treads lines
        for i in range(NUM_TREAD_SEGMENTS):
            # Offset of left line from the robot center along treads length
            left_offset = (i + self.__left_tread_alpha) * segment_length
            left_offset -= TREAD_LENGTH / 2
            left_offset *= Vector2(1, 0).rotate_rad(self.rotation)
            # Absolute center position of left line
            left_position = self.position + left_offset

            # Offset of right line from the robot center along treads length
            right_offset = (i + self.__right_tread_alpha) * segment_length
            right_offset -= TREAD_LENGTH / 2
            right_offset *= Vector2(1, 0).rotate_rad(self.rotation)
            # Absolute position of right line along length of treads
            right_position = self.position + right_offset

            # Distance to inner and outer endpoints of tread lines
            inner = ROBOT_WIDTH / 2 - TREAD_WIDTH / 2
            outer = ROBOT_WIDTH / 2 + TREAD_WIDTH / 2

            # Draw line on left treads
            pygame.draw.line(
                screen, TREADS_LINES_COLOR,
                left_position + Vector2(0, -inner).rotate_rad(self.rotation),
                left_position + Vector2(0, -outer).rotate_rad(self.rotation),
                width=2
            )
            # Draw line on right treads
            pygame.draw.line(
                screen, TREADS_LINES_COLOR,
                right_position + Vector2(0, inner).rotate_rad(self.rotation),
                right_position + Vector2(0, outer).rotate_rad(self.rotation),
                width=2
            )

        # Offsets of robot body vertices (without rotation)
        robot_vertex_offsets = [
            Vector2(ROBOT_LENGTH / 2, ROBOT_WIDTH / 2),
            Vector2(-ROBOT_LENGTH / 2, ROBOT_WIDTH / 2),
            Vector2(-ROBOT_LENGTH / 2, -ROBOT_WIDTH / 2),
            Vector2(ROBOT_LENGTH / 2, -ROBOT_WIDTH / 2)
        ]

        # Draw robot body
        pygame.draw.polygon(screen, self.color,
                            [self.position + offset.rotate_rad(self.rotation)
                             for offset in robot_vertex_offsets])

        root3div2 = math.sqrt(3) / 2

        # Offsets of robot arrow vertices (without rotation)
        arrow_vertex_offsets = [
            Vector2(ROBOT_LENGTH / 2, 0),
            Vector2(ROBOT_LENGTH / 2 - ARROW_SIZE * root3div2, ARROW_SIZE / 2),
            Vector2(ROBOT_LENGTH / 2 - ARROW_SIZE * root3div2, -ARROW_SIZE / 2)
        ]

        # Draw arrow to denote front of robot
        pygame.draw.polygon(screen, ARROW_COLOR,
                            [self.position + offset.rotate_rad(self.rotation)
                             for offset in arrow_vertex_offsets])

        # Offsets of robot turret vertices (without rotation)
        turret_vertex_offsets = [
            Vector2(0, TURRET_WIDTH / 2),
            Vector2(0, -TURRET_WIDTH / 2),
            Vector2(TURRET_LENGTH, -TURRET_WIDTH / 2),
            Vector2(TURRET_LENGTH, TURRET_WIDTH / 2)
        ]

        # Draw turret
        pygame.draw.polygon(
            screen, TURRET_COLOR,
            [self.position + offset.rotate_rad(self.turret_rotation)
             for offset in turret_vertex_offsets]
        )

        # Draw robot head
        pygame.draw.circle(screen, self.head_color, self.position,
                           ROBOT_HEAD_RADIUS)

    def post_render(self, screen: pygame.Surface):
        # Draw health bar
        if self.health >= MAX_HEALTH:
            return

        # Get "radius" of Robot
        radius = self.hitbox[0].magnitude()

        # Top left position of bars
        top_left = self.position + Vector2(-HEALTH_BAR_LENGTH / 2, radius)

        # Draw deficit bar
        pygame.draw.rect(screen, HEALTH_DEFICIT_COLOR,
                         Rect(top_left, Vector2(HEALTH_BAR_LENGTH,
                                                HEALTH_BAR_WIDTH)))

        available_length = (self.health / MAX_HEALTH) * HEALTH_BAR_LENGTH

        # Draw available bar
        pygame.draw.rect(screen, HEALTH_COLOR,
                         Rect(top_left, Vector2(available_length,
                                                HEALTH_BAR_WIDTH)))


# Callback type for `on_update`
Callback = Callable[[Robot, float], None]

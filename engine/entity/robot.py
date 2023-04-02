import math
import pygame
from typing import Callable, Optional

import engine.entity as entity

Vector2 = pygame.Vector2

# Dimensional constants
ROBOT_LENGTH = 120                                  # Length of robot, in pixels
ROBOT_WIDTH = 100                                   # Width of robot, in pixels
ROBOT_HEAD_RADIUS = 40                              # Radius of robot's head, in pixels
TURRET_LENGTH = 70                                  # Length of turret barrel, in pixels
TURRET_WIDTH = 16                                   # Width of turret barrel, in pixels
TREAD_LENGTH = 136                                  # Length of treads on sides of robot, in pixels
TREAD_WIDTH = 30                                    # Width of treads on sides of robot, in pixels
ARROW_SIZE = 10                                     # Size of arrow to denote front of robot, in pixels

NUM_TREAD_SEGMENTS = 6                              # Number of tread lines used to show movement

# Color constants
ROBOT_COLOR = "#EE0000"                             # Color of robot's body (rectangle)
ROBOT_HEAD_COLOR = "#CC0000"                        # Color of robot's head (circle)
TURRET_COLOR = "#AAAAAA"                            # Color of robot's turret barrel
TREADS_COLOR = "#888888"                            # Color of robot's treads
TREADS_LINES_COLOR = "#555555"                      # Color of lines on robot's treads
ARROW_COLOR = "#AAAAAA"                             # Color of robot front arrow

# Callback type for `on_update`
Callback = Callable[["entity.Robot"], None]

class Robot(entity.Entity):
    """
    Robot entity that can move, turn, and shoot.
    """
    def __init__(self):
        super().__init__()

        self.on_update: Optional[Callback] = None   # Callback to be called on each `update`

        self.move_power = 0                         # Movement power in [-1, 1]
        self.turn_power = 0                         # Turning power in [-1, 1]
        self.turret_turn_power = 0                  # Turret turning power in [-1, 1]

        self.color = ROBOT_COLOR
        self.head_color = ROBOT_HEAD_COLOR

        self.__turret_rotation = 0                  # Turret rotation (in radians)

        self.__move_speed = 300                     # Maximum movement speed (in pixels/sec)
        self.__turn_speed = math.pi                 # Maximum turning speed (in radians/sec)
        self.__turret_turn_speed = 1.5 * math.pi    # Maximum turret turning speed (in radians/sec)

        self.__left_tread_alpha = 0                 # Value in [0, 1) to show left tread movement
        self.__right_tread_alpha = 0                # Value in [0, 1) to show right tread movement

        self.__shot_cooldown = 0.5                  # Time cooldown between each shot, in seconds
        self.__time_until_next_shot = 0             # Current shot cooldown progress (0 = ready)

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

    # We separate the `X_power` members into properties with specialized setters so that we can
    # clamp the values between [-1, 1].
    @property
    def move_power(self) -> float:
        """
        `move_power` is the current translational velocity of the robot,
        represented as a fraction of maximum movement speed.

        It is clamped between [-1, 1], where positive values of `move_power`
        correspond to moving forwards, while negative values correspond
        to moving backwards.
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
        correspond to turning clockwise, while negative values correspond
        to turning counter-clockwise.
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
        self.position += Vector2(self.__move_speed * self.move_power * dt, 0).rotate_rad(self.rotation)

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
        self.rotation += self.__turn_speed * self.turn_power * dt

        # Calculate tread segments/sec speed
        tread_speed = (self.__turn_speed * ROBOT_WIDTH / 2) / (TREAD_LENGTH / NUM_TREAD_SEGMENTS)
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
        self.__turret_rotation += self.__turret_turn_speed * self.turret_turn_power * dt
        self.__turret_rotation %= 2 * math.pi

    def shoot(self):
        """
        Makes the robot shoot a bullet in the direction of its turret.
        """
        assert self.arena is not None, "Robot does not have a corresponding Arena"

        if self.__time_until_next_shot > 0:
            return
        
        bullet_position = self.position + Vector2(TURRET_LENGTH, 0).rotate_rad(self.__turret_rotation)
        bullet = entity.Bullet(bullet_position, self.__turret_rotation, self)
        self.arena.add_entity(bullet)

        self.__time_until_next_shot = self.__shot_cooldown

    def update(self, dt: float):
        if self.on_update is not None:
            self.on_update(self)
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
            self.position + (Vector2(0, -ROBOT_WIDTH / 2) + tread_offset).rotate_rad(self.rotation)
            for tread_offset in tread_vertex_offsets
        ]
        right_tread_vertices = [
            self.position + (Vector2(0, ROBOT_WIDTH / 2) + tread_offset).rotate_rad(self.rotation)
            for tread_offset in tread_vertex_offsets
        ]

        # Draw treads rectangles
        pygame.draw.polygon(screen, TREADS_COLOR, left_tread_vertices)
        pygame.draw.polygon(screen, TREADS_COLOR, right_tread_vertices)

        # Length of each tread segment, in pixels
        tread_segment_length = TREAD_LENGTH / NUM_TREAD_SEGMENTS

        # Draw treads lines
        for i in range(NUM_TREAD_SEGMENTS):
            # Offset of left line from the robot center along treads length, in pixels
            left_line_offset = -TREAD_LENGTH / 2 + (i + self.__left_tread_alpha) * tread_segment_length
            # Absolute position of left line along length of treads
            left_line_position = self.position + Vector2(left_line_offset, 0).rotate_rad(self.rotation)

            # Offset of right line from the robot center along treads length, in pixels
            right_line_offset = -TREAD_LENGTH / 2 + (i + self.__right_tread_alpha) * tread_segment_length
            # Absolute position of right line along length of treads
            right_line_position = self.position + Vector2(right_line_offset, 0).rotate_rad(self.rotation)

            # Draw line on left treads
            pygame.draw.line(
                screen, TREADS_LINES_COLOR,
                left_line_position + Vector2(0, -ROBOT_WIDTH / 2 - TREAD_WIDTH / 2).rotate_rad(self.rotation),
                left_line_position + Vector2(0, -ROBOT_WIDTH / 2 + TREAD_WIDTH / 2).rotate_rad(self.rotation),
                width=2
            )
            # Draw line on right treads
            pygame.draw.line(
                screen, TREADS_LINES_COLOR,
                right_line_position + Vector2(0, ROBOT_WIDTH / 2 + TREAD_WIDTH / 2).rotate_rad(self.rotation),
                right_line_position + Vector2(0, ROBOT_WIDTH / 2 - TREAD_WIDTH / 2).rotate_rad(self.rotation),
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
        pygame.draw.polygon(
            screen, self.color,
            [self.position + offset.rotate_rad(self.rotation) for offset in robot_vertex_offsets]
        )

        # Offsets of robot arrow vertices (without rotation)
        arrow_vertex_offsets = [
            Vector2(ROBOT_LENGTH / 2, 0),
            Vector2(ROBOT_LENGTH / 2 - ARROW_SIZE * math.sqrt(3) / 2, ARROW_SIZE / 2),
            Vector2(ROBOT_LENGTH / 2 - ARROW_SIZE * math.sqrt(3) / 2, -ARROW_SIZE / 2)
        ]

        # Draw arrow to denote front of robot
        pygame.draw.polygon(
            screen, ARROW_COLOR,
            [self.position + offset.rotate_rad(self.rotation) for offset in arrow_vertex_offsets]
        )

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
            [self.position + offset.rotate_rad(self.__turret_rotation) for offset in turret_vertex_offsets]
        )

        # Draw robot head
        pygame.draw.circle(screen, self.head_color, self.position, ROBOT_HEAD_RADIUS)

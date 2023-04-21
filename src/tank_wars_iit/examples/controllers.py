from random import random

import pygame

from tank_wars_iit._engine.arena import Arena
from tank_wars_iit._engine.control import (Controller, ControllerAction,
                                           ControllerState)


class HumanController(Controller):
    """Controller that reads user input to move the robot."""
    name = "Human"
    body_color = "#222222"
    head_color = "#111111"

    def __init__(self, arena: Arena):
        self.arena = arena

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        keys = pygame.key.get_pressed()

        # Change motion power
        action.move_power = (-1 if keys[pygame.K_s] else 1 if keys[pygame.K_w]
                             else 0)
        action.turn_power = (-1 if keys[pygame.K_a] else 1 if keys[pygame.K_d]
                             else 0)

        window_point = pygame.Vector2(pygame.mouse.get_pos())
        arena_point = self.arena.window_to_arena(window_point)
        down, *_ = pygame.mouse.get_pressed()

        # Aim turret towards mouse
        action.aim_toward = (arena_point.x, arena_point.y)
        # Shoot
        if down:
            action.shoot = True

        return action


class SpinController(Controller):
    """Randomly spinning robot controller."""
    name = "Spin"
    body_color = "#EE0000"
    head_color = "#CC0000"

    def __init__(self):
        self.move_power = random() * 2 - 1
        self.turn_power = random() * 2 - 1
        self.turret_turn_power = random() * 2 - 1

    def act(self, _) -> ControllerAction:
        action = ControllerAction()

        action.shoot = True
        action.move_power = self.move_power
        action.turn_power = self.turn_power
        action.turret_turn_power = self.turret_turn_power

        return action


class AggressiveController(Controller):
    """Controller that seeks and kills the nearest robot."""
    name = "Aggressive"
    body_color = "#EE00EE"
    head_color = "#CC00CC"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.enemy_position
        if state.can_see_enemy:
            action.aim_toward = state.enemy_position
            action.shoot = True

        return action


class GreedyController(Controller):
    """Controller for seeking the coin."""
    name = "Greedy"
    body_color = "#00EE00"
    head_color = "#00CC00"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.coin_position

        return action


class AggreedyController(Controller):
    """Controller for seeking the coin while shooting at the nearest robot."""
    name = "Aggreedy"
    body_color = "#0000EE"
    head_color = "#0000CC"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.coin_position
        if state.can_see_enemy:
            action.aim_toward = state.enemy_position
            action.shoot = True

        return action

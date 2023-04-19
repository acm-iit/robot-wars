from random import random

from engine.control import Controller, ControllerAction, ControllerState


class SpinController(Controller):
    """Randomly spinning robot controller."""
    def __init__(self):
        super().__init__("Spin", "#EE0000", "#CC0000")
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
    def __init__(self):
        super().__init__("Aggressive", "#EE00EE", "#CC00CC")

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.enemy_position
        if state.can_see_enemy:
            action.aim_toward = state.enemy_position
            action.shoot = True

        return action


class GreedyController(Controller):
    """Controller for seeking the coin."""
    def __init__(self):
        super().__init__("Greedy", "#00EE00", "#00CC00")

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.coin_position

        return action


class AggreedyController(Controller):
    """Controller for seeking the coin while shooting at the nearest robot."""
    def __init__(self):
        super().__init__("Aggreedy", "#0000EE", "#0000CC")

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.coin_position
        if state.can_see_enemy:
            action.aim_toward = state.enemy_position
            action.shoot = True

        return action

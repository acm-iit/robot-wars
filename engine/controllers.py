from random import random

from engine.control import ControlInput, Controller, ControlOutput


class SpinController(Controller):
    """Randomly spinning robot controller."""
    def __init__(self):
        super().__init__("Spin", "#EE0000", "#CC0000")
        self.move_power = random() * 2 - 1
        self.turn_power = random() * 2 - 1
        self.turret_turn_power = random() * 2 - 1

    def act(self, _, output: ControlOutput):
        output.shoot = True
        output.move_power = self.move_power
        output.turn_power = self.turn_power
        output.turret_turn_power = self.turret_turn_power


class AggressiveController(Controller):
    """Controller that seeks and kills the nearest robot."""
    def __init__(self):
        super().__init__("Aggressive", "#EE00EE", "#CC00CC")

    def act(self, input: ControlInput, output: ControlOutput):
        output.move_toward = input.enemy_position
        if input.can_see_enemy:
            output.aim_toward = input.enemy_position
            output.shoot = True


class GreedyController(Controller):
    """Controller for seeking the coin."""
    def __init__(self):
        super().__init__("Greedy", "#00EE00", "#00CC00")

    def act(self, input: ControlInput, output: ControlOutput):
        output.move_toward = input.coin_position


class AggreedyController(Controller):
    """Controller for seeking the coin while shooting at the nearest robot."""
    def __init__(self):
        super().__init__("Aggreedy", "#0000EE", "#0000CC")

    def act(self, input: ControlInput, output: ControlOutput):
        output.move_toward = input.coin_position
        if input.can_see_enemy:
            output.aim_toward = input.enemy_position
            output.shoot = True

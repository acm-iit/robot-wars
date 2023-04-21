# `examples`

```python
import tank_wars_iit.examples
```

A module containing several examples of [`Controller`](./Controller.md)s that you can use as a baseline or as competition to assess your [`Controller`](./Controller.md) against.

Note that these examples are quite primitive and easy to implement; we hope you guys leverage the full potential of [`ControllerState`](./ControllerState.md) and [`ControllerAction`](./ControllerAction.md) to create intelligent tanks!

## `HumanController`

This [`Controller`](./Controller.md) reads user input from the keyboard and mouse to move a tank.

### Controls

- `W`: Move forward
- `S`: Move backward
- `A`: Turn counter-clockwise
- `D`: Turn clockwise
- Mouse aim: Set goal aim location for the turret
- Mouse left-click: Shoot a bullet

## `SpinController`

This [`Controller`](./Controller.md) simply moves, turns, and turns its turret randomly while constantly shooting.

To determine the powers at which it moves, turns, and turns its turret, it overrides `Controller.__init__` to determine the [`move_power`](./ControllerAction.md#move_power), [`turn_power`](./ControllerAction.md#turn_power), and [`turret_turn_power`](./ControllerAction.md#turret_turn_power) it will [`act`](./Controller.md#act) with at each time step.

This is a good example of overriding `Controller.__init__` for custom initialization logic and shared state.

### Code

```python
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
```

## `AggressiveController`

This [`Controller`](./Controller.md) chases down the nearest tank and shoots at it.

It simply sets [`action.move_toward`](./ControllerAction.md#move_toward) to [`state.enemy_position`](./ControllerState.md#enemy_position) to move towards the nearest tank.

Then, if it has line of sight ([`state.can_see_enemy`](./ControllerState.md#can_see_enemy)), it sets [`action.aim_toward`](./ControllerAction.md#aim_toward) to [`state.enemy_position`](./ControllerState.md#enemy_position) to aim towards the tank, and sets [`action.shoot`](./ControllerAction.md#shoot) to `True` to shoot.

### Code

```python
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
```

## `GreedyController`

This [`Controller`](./Controller.md) simply tries to collect as many coins as possible.

At each time step, it sets [`action.move_toward`](./ControllerAction.md#move_toward) to [`state.coin_position`](./ControllerState.md#coin_position) to move towards the coin.

### Code

```python
class GreedyController(Controller):
    """Controller for seeking the coin."""
    name = "Greedy"
    body_color = "#00EE00"
    head_color = "#00CC00"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        action.move_toward = state.coin_position

        return action
```

## `AggreedyController`

This [`Controller`](./Controller.md) is a combination of both `AggressiveController` and `GreedyController`; it moves towards the coin while shooting at any enemy it has line of sight with.

### Code

```python
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
```

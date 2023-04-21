# `ControllerState`

```python
from tank_wars_iit import ControllerState
```

Contains numerous values representing the state of a tank and its surroundings.

This object is fed into [`Controller.act`](./Controller.md#act) before every physics step to help the `Controller` determine how to behave.

## Attributes

### `time_delta`

```python
time_delta: float
```

Elapsed time that this time step will simulate, in seconds. This is helpful for precise physics calculations, like predicting tank or bullet paths!

### `is_battle_royale`

```python
is_battle_royale: bool
```

Signifies whether the tank is playing in a Battle Royale; i.e. the first round to determine seeding in the tournament.

A value of `False` indicates that the tank is facing a singular enemy in a one versus one environment.

This is useful if you want to program different strategies between Battle Royale and one versus one.

### `health`

```python
health: float
```

Health of the tank, as a fraction of its maximum health. A value of `1` implies full health, while a value of `0` implies no health.

### `coins`

```python
coins: int
```

Number of coins the tank has collected.

### `position`

```python
position: tuple[float, float]
```

Position of the tank, as a tuple `(x, y)` measured from the top-left point of the arena.

### `max_speed`

```python
max_speed: float
```

Maximum movement speed for the tank; i.e. when [`ControllerAction.move_power = 1`](./ControllerAction.md#move_power) or `-1`.

### `rotation`

```python
rotation: float
```

Rotation of the tank, in radians measured clockwise from the positive X-axis (right).

(It is measured clockwise since the positive Y-axis is down!)

### `max_turn_speed`

```python
max_turn_speed: float
```

Maximum turning speed for the tank; i.e. when [`ControllerAction.turn_power = 1`](./ControllerAction.md#turn_power) or `-1`.

### `turret_rotation`

```python
turret_rotation: float
```

Rotation of the tank's turret, in radians measured clockwise from the positive X-axis (right).

(It is measured clockwise since the positive Y-axis is down!)

### `max_turret_turn_speed`

```python
max_turret_turn_speed: float
```

Maximum turning speed for the tank's turret; i.e. when [`ControllerAction.turret_turn_power = 1`](./ControllerAction.md#turret_turn_power) or `-1`.

### `shot_cooldown`

```python
shot_cooldown: float
```

Time left until the tank can shoot a bullet. Every time a tank shoots a bullet, it cannot shoot again for `1` second.

If the value is `0`, then setting [`ControllerAction.shoot = True`](./ControllerAction.md#shoot) will successfully shoot a bullet.

### `shot_speed`

```python
shot_speed: float
```

Scalar speed of the tank's bullets when it shoots. Useful for predicting own bullet paths.

### `enemy_health`

```python
enemy_health: float
```

Health of the enemy tank, as a fraction of its maximum health. A value of `1` implies full health, while a value of `0` implies no health.

In the case of multiple enemy tanks (i.e. battle royale), this is the health of the nearest enemy tank.

### `enemy_coins`

```python
enemy_coins: int
```

Number of coins the enemy tank has collected.

In the case of multiple enemy tanks (i.e. battle royale), this is the number of coins of the nearest enemy tank.

### `enemy_position`

```python
enemy_position: tuple[float, float]
```

Position of the enemy tank, as a tuple `(x, y)` measured from the top-left point of the arena.

In the case of multiple enemy tanks (i.e. battle royale), this is the position of the nearest enemy tank.

### `enemy_velocity`

```python
enemy_velocity: tuple[float, float]
```

Velocity of the enemy tank from the previous time step, as a tuple `(vx, vy)` measured from the top-left point of the arena.

In the case of multiple enemy tanks (i.e. battle royale), this is the velocity of the nearest enemy tank.

Along with [`time_delta`](#time_delta), this is useful for predicting enemy paths!

### `enemy_rotation`

```python
enemy_rotation: float
```

Rotation of the enemy tank, in radians measured clockwise from the positive X-axis (right).

In the case of multiple enemy tanks (i.e. battle royale), this is the rotation of the nearest enemy tank.

(It is measured clockwise since the positive Y-axis is down!)

### `enemy_turret_rotation`

```python
enemy_turret_rotation: float
```

Rotation of the enemy tank's turret, in radians measured clockwise from the positive X-axis (right).

In the case of multiple enemy tanks (i.e. battle royale), this is the rotation of the nearest enemy tank's turret.

(It is measured clockwise since the positive Y-axis is down!)

### `enemy_shot_cooldown`

```python
enemy_shot_cooldown: float
```

Time left until the enemy tank can shoot a bullet. Every time a tank shoots a bullet, it cannot shoot again for `1` second.

If the value is `0`, then the enemy tank is able to shoot a bullet.

In the case of multiple enemy tanks (i.e. battle royale), this is the shot cooldown of the nearest enemy tank.

### `can_see_enemy`

```python
can_see_enemy: bool
```

Determines if the tank can see the enemy tank, as a boolean where `True` implies it can do so.

"See" is defined as having line-of-sight with the enemy, with no impeding obstacles.

In the case of multiple enemy tanks (i.e. battle royale), this applies to the nearest enemy tank.

### `bullets`

```python
bullets: list[tuple[float, float, float, float]]
```

List of positions and velocities of enemy bullets in proximity to the tank, as tuples `(x, y, vx, vy)`, where `x` and `y` are the positional coordinates measured from the top-left point of the arena, and `vx` and `vy` are the velocity components.

### `coin_position`

```python
coin_position: tuple[float, float]
```

Position of the coin, as a tuple `(x, y)` measured from the top-left point of the arena.

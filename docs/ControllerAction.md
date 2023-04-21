# `ControllerAction`

```python
from tank_wars_iit import ControllerAction
```

Contains numerous values representing the immediate action of a tank at a certain time step.

This object is returned from [`Controller.act`](./Controller.md#act) before every physics step to help the `Controller` determine how to behave.

## Attributes

### `move_power`

```python
move_power: float
```

Current velocity of the tank, represented as a fraction of maximum movement speed between `-1` and `1`, inclusive.

Positive values correspond to moving forwards, while negative values correspond to moving backwards.

### `turn_power`

```python
turn_power: float
```

Current angular velocity of the tank, represented as a fraction of maximum turning speed between `-1` and `1`, inclusive.

Positive values correspond to turning clockwise, while negative values correspond to turning counter-clockwise.

(Positive is clockwise because the positive Y-axis is down!)

### `turret_turn_power`

```python
turret_turn_power: float
```

Current angular velocity of the turret, represented as a fraction of maximum turret turning speed between `-1` and `1`, inclusive.

Positive values correspond to turning clockwise, while negative values correspond to turning counter-clockwise.

(Positive is clockwise because the positive Y-axis is down!)

### `move_toward`

```python
move_toward: tuple[float, float] | None
```

Position that the tank should move toward using pathfinding, as a tuple `(x, y)` measured from the top-left point of the arena.

This value overrides [`move_power`](#move_power), [`turn_power`](#turn_power), and [`turn_toward`](#turn_toward).

If unused, set to `None`.

### `turn_toward`

```python
turn_toward: float | tuple[float, float] | None
```

Angle or position that the tank should turn itself toward.

Angles should be in radians measured clockwise from the positive X-axis (right), while positions should be tuples of floats `(x, y)` measured from the top-left point of the arena.

This value overrides [`turn_power`](#turn_power).

If unused, set to `None`.

(Angles are measured clockwise since the positive Y-axis is down!)

### `aim_toward`

```python
aim_toward: float | tuple[float, float] | None
```

Angle or position that the tank should aim its turret toward.

Angles should be in radians measured clockwise from the positive X-axis (right), while positions should be tuples of floats `(x, y)` measured from the top-left point of the arena.

This value overrides [`turret_turn_power`](#turret_turn_power).

If unused, set to `None`.

(Angles are measured clockwise since the positive Y-axis is down!)

### `shoot`

```python
shoot: bool
```

Determines if the tank should shoot during this time step.

`False` represents no shooting, `True` represents shooting.
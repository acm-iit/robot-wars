# `util`

```python
import tank_wars_iit.util
```

Contains three utility functions that may be of use to you.

## `distance`

```python
distance(
    x1: float,
    y1: float,
    x2: float,
    y2: float
) -> float
```

Calculates the Euclidean distance between two points `(x1, y1)` and `(x2, y2)`.

## `angle_to`

```python
angle_to(
    x1: float,
    y1: float,
    x2: float,
    y2: float
) -> float
```

Calculates the angle, in radians, for an object located at `(x1, y1)` to be facing an object located at `(x2, y2)`.

## `angle_difference`

```python
angle_difference(
    angle1: float,
    angle2: float
) -> float
```

Returns the angle, in radians, that should be added to `angle1` (in radians) to direct it towards `angle2` (also in radians).

**Note**: This value is signed, so if you want the absolute angle difference between two angles, be sure to apply `abs`!

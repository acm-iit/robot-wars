# `scenario`

```python
import tank_wars_iit.scenario
```

This module contains several easy-to-use functions to model game environments.

## `one_vs_one`

```python
one_vs_one(
    controller1: type[Controller],
    controller2: type[Controller],
    show_fps=False,
    show_mouse_coordinates=False
)
```

Runs two [`Controller`](./Controller.md) classes in a one versus one environment. The map is a medium square map with two sets of concentric circular walls.

Optional parameter `show_fps` can be set to `True` to show FPS in the top left.

Optional parameter `show_mouse_coordinates` can be set to `True` to show the user mouse coordinates (in game space) in the top-left; this can be useful for figuring out certain coordinates in the map that you want your tank to be aware of.

## `battle_royale`

```python
battle_royale(
    controller_classes: list[type[Controller]],
    show_fps=False,
    show_mouse_coordinates=False,
    lock_camera=False
)
```

Runs a list of up to 64 [`Controller`](./Controller.md) classes in a battle royale environment. The map is a vast, square map with the walls slowly closing in towards the center, similar to a zone in a battle royale game. As the zone shrinks, the game camera zooms in to view the playable area.

Optional parameter `show_fps` can be set to `True` to show FPS in the top left.

Optional parameter `show_mouse_coordinates` can be set to `True` to show the user mouse coordinates (in game space) in the top-left; this can be useful for figuring out certain coordinates in the map that you want your tank to be aware of.

Optional parameter `lock_camera` can be set to `True` to keep the camera from zooming in on the playable area. This can be used in conjunction with `show_mouse_coordinates` to make it easier to find coordinates.

## `tournament`

```python
tournament(
    controller_classes: list[type[Controller]],
    show_fps=False,
    show_mouse_coordinates=False,
    lock_camera=False
)
```

Runs a list of up to 64 [`Controller`](./Controller.md) classes in a bracket tournament. To determine seeding, it runs the [`battle_royale`](#battle_royale) scenario with all of the [`Controller`](./Controller.md)s. It then constructs a bracket based on the seeding and runs each match until the final winner is determined. It also runs a third place matchup if there are at least four [`Controller`](./Controller.md)s.

Optional parameter `show_fps` can be set to `True` to show FPS in the top left.

Optional parameter `show_mouse_coordinates` can be set to `True` to show the user mouse coordinates (in game space) in the top-left; this can be useful for figuring out certain coordinates in the map that you want your tank to be aware of.

Optional parameter `lock_camera` can be set to `True` to keep the camera from zooming in on the playable area. This can be used in conjunction with `show_mouse_coordinates` to make it easier to find coordinates.

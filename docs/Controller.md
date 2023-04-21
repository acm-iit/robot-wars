# `Controller`

```python
from tank_wars_iit import Controller
```

Abstract tank controller class.

Do not modify this class; instead extend this class into a subclass with a unique classname to represent your tank.

To personalize your tank, set the [`name`](#name), [`body_color`](#body_color), and [`head_color`](#head_color) class attributes.

To program your tank, override the [`act`](#act) method.

You may also provide initialization logic by overriding the constructor; however, no new constructor parameters may be added. This is useful for adding custom state that can be used between different invocations of [`act`](#act).

## Attributes

**Note**: These are all *class* attributes, which means that they should be set in the scope of `Controller`, not within `Controller.__init__`.

### `name`

```python
Controller.name: str
```

Name used to distinguish this tank between others in the leaderboard.

Change this value to name your tank.

### `body_color`

```python
Controller.body_color: str
```

Hexadecimal RGB color of the tank's body (the rectangle chassis).

Change this value to personalize your tank.

### `head_color`

```python
Controller.head_color: str
```

Hexadecimal RGB color of the tank's head (the circle in the middle).

Change this value to personalize your tank.

## Methods

### `act`

```python
Controller.act(state: ControllerState) -> ControllerAction
```

This method is run by the engine before every physics step of the game simulation to determine how the tank will behave during that step.

`state` is a [`ControllerState`](./ControllerState.md), which contains values describing the current state of the tank.

The method returns an [`ControllerAction`](./ControllerAction.md), which contains values describing how the tank should behave in the upcoming time step.

You can think of it as a state machine!

Override this method with the desired behavior for your tank.


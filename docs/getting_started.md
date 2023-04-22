# Getting Started

Hello, and welcome to **Scarlet HackNiite Spring 2023: Tank Wars**!

If you haven't already, make sure to read the [background](./background.md) to familiarize yourself with the rules and features of the game.

## Prerequisites

The Tank Wars Framework requires you to have at least Python 3.10.

## Installation

You can install the framework via `pip`:

```
python -m pip install --upgrade tank_wars_iit
```

To make sure it works, try running the following code:

```python
import tank_wars_iit.examples as examples
import tank_wars_iit.scenario as scenario
scenario.one_vs_one(examples.HumanController, examples.AggressiveController)
```

If successful, you should see a one vs. one matchup appear on screen between a human-controlled tank (in black) and an NPC tank (in blue).

`scenario.one_vs_one` is a function that runs a one vs. one matchup between two tanks. There are two other scenarios: `battle_royale` and `tournament`, which you can read about [here](./scenario.md).

`examples.HumanController` represents the controller for a human-controlled tank.

`examples.AggressiveController` represents the controller for an NPC tank that chases enemy tanks down and shoots at them.

There are other example tanks provided to you to play with, which you can read about [here](./examples.md).

## Programming Your Tank

Now comes the fun part: making your own tank!

### Setting up a `Controller`

Your implementation of a tank comes in the form of a [`Controller`](./Controller.md). You will sub-class the `Controller` class to create your tank.

Here's an example:

```python
from tank_wars_iit import Controller, ControllerAction, ControllerState

class MyController(Controller):
    name = "MyTank"
    body_color = "#DDDDDD"
    head_color = "#AAAAAA"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        return action
```

`MyController` is a sub-class of `Controller` that you will implement; you can give it any classname besides `MyController` that you like.

You can personalize your tank via three class attributes: [`name`](./Controller.md#name), which is a string display name, [`body_color`](./Controller.md#body_color), which is the RGB color of the tank chassis, and [`head_color`](./Controller.md#head_color), which is the RGB color of the tank head.

You can program your tank's actions via overriding the [`act`](./Controller.md#act) method. This method accepts a [`ControllerState`](./ControllerState.md), which represents the state of the game that the tank can observe, and returns a [`ControllerAction`](./ControllerAction.md), which represents the action that the tank will take given that state.

The `act` method is run before each step of physics simulation, giving you granular control over the instantaneous decision making of your tank.

### Testing your `Controller`

You can easily test your controller by plugging it into a scenario from the `tank_wars_iit.scenario` module. Let's pit your new controller up against one of the examples!

```python
import tank_wars_iit.scenario as scenario
import tank_wars_iit.examples as examples

# One vs. one matchup against AggressiveController
scenario.one_vs_one(MyController, examples.AggressiveController)
```

When you run this code, you'll notice that your tank does nothing. This is because the `act` method doesn't do anything yet!

### Basic Actions

We want our tank to fight the Aggressive tank. Let's walk through how to do this:

First, let's make our tank move towards the enemy tank:

```python
class MyController(Controller):
    name = "MyTank"
    body_color = "#DDDDDD"
    head_color = "#AAAAAA"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        # Move towards the enemy
        action.move_toward = state.enemy_position

        return action
```

By setting [`action.move_toward`](./ControllerAction.md#move_toward) equal to [`state.enemy_position`](./ControllerState.md#enemy_position), we tell the tank to move towards the enemy position; the framework will handle the rest, including pathfinding. It's that easy!

Now, let's make it shoot the enemy:

```python
class MyController(Controller):
    name = "MyTank"
    body_color = "#DDDDDD"
    head_color = "#AAAAAA"

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        # Move towards the enemy
        action.move_toward = state.enemy_position

        # Shoot
        if state.can_see_enemy:
            action.shoot = True

        return action
```

We first check that we have line of sight via [`state.can_see_enemy`](./ControllerState.md#can_see_enemy), then we set [`action.shoot`](./ControllerAction.md#shoot) to `True` to shoot.

Note that the tank won't just spurt a flurry of bullets, since there's a 1 second cooldown between each shot! (Hint: you can read the current cooldown from the state via [`state.shot_cooldown`](./ControllerState.md#shot_cooldown)).

### See More

This is just a basic summary of all the functionalities you can use to program your tank. Please take a look at the following documentation for more!

- [`Controller`](./Controller.md)
- [`ControllerState`](./ControllerState.md)
- [`ControllerAction`](./ControllerAction.md)
- [`tank_wars_iit.examples`](./examples.md)
- [`tank_wars_iit.scenario`](./scenario.md)
- [`tank_wars_iit.util`](./util.md)

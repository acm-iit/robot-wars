import math


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculates the Euclidean distance between two points `(x1, y1)` and
    `(x2, y2)`.
    """
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def angle_to(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculates the angle, in radians, for an object located at `(x1, y1)` to be
    facing an object located at `(x2, y2)`.
    """
    dx, dy = x2 - x1, y2 - y1
    return math.atan2(dy, dx)


class ControllerState:
    """
    Object that resembles the current state of the tank. The values in this
    object can be used to determine how the tank should act in the upcoming
    time step, which is written into the ControllerAction.
    """
    def __init__(self):
        self.time_delta: float = 0
        """
        Elapsed time that this time step will simulate, in seconds. This is
        helpful for precise physics calculations, like predicting tank or
        bullet paths!
        """

        self.is_battle_royale: bool = False
        """
        Signifies whether the tank is playing in a Battle Royale; i.e. the
        first round to determine seeding in the tournament.

        A value of `False` indicates that the tank is facing a singular enemy
        in a one versus one environment.

        This is useful if you want to program different strategies between
        Battle Royale and one versus one.
        """

        self.health: float = 0
        """
        Health of the tank, as a fraction of its maximum health. A value of `1`
        implies full health, while a value of `0` implies no health.
        """

        self.coins: int = 0
        """
        Number of coins the tank has collected.
        """

        self.position: tuple[float, float] = (0, 0)
        """
        Position of the tank, as a tuple `(x, y)` measured from the top-left
        point of the arena.
        """

        self.max_speed: float = 0
        """
        Maximum movement speed for the tank; i.e. when `move_power = 1` or
        `-1`.
        """

        self.rotation: float = 0
        """
        Rotation of the tank, in radians measured clockwise from the positive
        X-axis (right).

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.max_turn_speed: float = 0
        """
        Maximum turning speed for the tank; i.e. when `turn_power = 1` or `-1`.
        """

        self.turret_rotation: float = 0
        """
        Rotation of the tank's turret, in radians measured clockwise from the
        positive X-axis (right).

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.max_turret_turn_speed: float = 0
        """
        Maximum turning speed for the tank's turret; i.e. when
        `turret_turn_power = 1` or `-1`.
        """

        self.shot_cooldown: float = 0
        """
        Time left until the tank can shoot a bullet. Every time a tank shoots
        a bullet, it cannot shoot again for `1` second.

        If the value is `0`, then setting `ControllerAction.shoot = True` will
        successfully shoot a bullet.
        """

        self.shot_speed: float = 0
        """
        Scalar speed of the tank's bullets when it shoots. Useful for
        predicting own bullet paths.
        """

        self.enemy_health: float = 0
        """
        Health of the enemy tank, as a fraction of its maximum health. A value
        of `1` implies full health, while a value of `0` implies no health.

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        health of the nearest enemy tank.
        """

        self.enemy_coins: int = 0
        """
        Number of coins the enemy tank has collected.

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        number of coins of the nearest enemy tank.
        """

        self.enemy_position: tuple[float, float] = (0, 0)
        """
        Position of the enemy tank, as a tuple `(x, y)` measured from the
        top-left point of the arena.

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        position of the nearest enemy tank.
        """

        self.enemy_velocity: tuple[float, float] = (0, 0)
        """
        Velocity of the enemy tank from the previous time step, as a tuple
        `(vx, vy)` measured from the top-left point of the arena.

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        velocity of the nearest enemy tank.

        Along with `time_delta`, this is useful for predicting enemy paths!
        """

        self.enemy_rotation: float = 0
        """
        Rotation of the enemy tank, in radians measured clockwise from the
        positive X-axis (right).

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        rotation of the nearest enemy tank.

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.enemy_turret_rotation: float = 0
        """
        Rotation of the enemy tank's turret, in radians measured clockwise from
        the positive X-axis (right).

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        rotation of the nearest enemy tank's turret.

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.enemy_shot_cooldown: float = 0
        """
        Time left until the enemy tank can shoot a bullet. Every time a tank
        shoots a bullet, it cannot shoot again for `1` second.

        If the value is `0`, then the enemy tank is able to shoot a bullet.

        In the case of multiple enemy tanks (i.e. battle royale), this is the
        shot cooldown of the nearest enemy tank.
        """

        self.can_see_enemy: bool = False
        """
        Determines if the tank can see the enemy tank, as a boolean where
        `True` implies it can do so.

        "See" is defined as having line-of-sight with the enemy, with no
        impeding obstacles.

        In the case of multiple enemy tanks (i.e. battle royale), this applies
        to the nearest enemy tank.
        """

        self.bullets: list[tuple[float, float, float, float]] = []
        """
        List of positions and velocities of enemy bullets in proximity to the
        tank, as tuples `(x, y, vx, vy)`, where `x` and `y` are the positional
        coordinates measured from the top-left point of the arena, and `vx` and
        `vy` are the velocity components.
        """

        self.coin_position: tuple[float, float] = (0, 0)
        """
        Position of the coin, as a tuple `(x, y)` measured from the top-left
        point of the arena.
        """


class ControllerAction:
    """
    Object the represents the actions the tank will take in the upcoming time
    step. Write into the values of this object to dictate the tank's behavior.
    """
    def __init__(self):
        self.move_power: float = 0
        """
        Current velocity of the tank, represented as a fraction of maximum
        movement speed between `-1` and `1`, inclusive.

        Positive values correspond to moving forwards, while negative values
        correspond to moving backwards.
        """

        self.turn_power: float = 0
        """
        Current angular velocity of the tank, represented as a fraction of
        maximum turning speed between `-1` and `1`, inclusive.

        Positive values correspond to turning clockwise, while negative values
        correspond to turning counter-clockwise.

        (Positive is clockwise because the positive Y-axis is down!)
        """

        self.turret_turn_power: float = 0
        """
        Current angular velocity of the turret, represented as a fraction of
        maximum turret turning speed between `-1` and `1`, inclusive.

        Positive values correspond to turning clockwise, while negative values
        correspond to turning counter-clockwise.

        (Positive is clockwise because the positive Y-axis is down!)
        """

        self.move_toward: tuple[float, float] | None = None
        """
        Position that the tank should move toward using pathfinding, as a tuple
        `(x, y)` measured from the top-left point of the arena.

        This value overrides `move_power`, `turn_power`, and `turn_toward`.

        If unused, set to `None`.
        """

        self.turn_toward: float | tuple[float, float] | None = None
        """
        Angle or position that the tank should turn itself toward.

        Angles should be in radians measured clockwise from the positive X-axis
        (right), while positions should be tuples of floats `(x, y)` measured
        from the top-left point of the arena.

        This value overrides `turn_power`.

        If unused, set to `None`.

        (Angles are measured clockwise since the positive Y-axis is down!)
        """

        self.aim_toward: float | tuple[float, float] | None = None
        """
        Angle or position that the tank should aim its turret toward.

        Angles should be in radians measured clockwise from the positive X-axis
        (right), while positions should be tuples of floats `(x, y)` measured
        from the top-left point of the arena.

        This value overrides `turret_turn_power`.

        If unused, set to `None`.

        (Angles are measured clockwise since the positive Y-axis is down!)
        """

        self.shoot: bool = False
        """
        Determines if the tank should shoot during this time step.

        `False` represents no shooting, `True` represents shooting.
        """


class Controller:
    """
    Abstract tank controller class.

    Do not modify this class; instead create a subclass of this class to
    represent your tank. Override the below methods in your subclass to
    implement the behavior of your tank.
    """
    name = "Tank"
    """
    Name used to distinguish this tank between others in the leaderboard.

    Change this value to name your tank.
    """

    body_color = "#EEEEEE"
    """
    Hexadecimal RGB color of the tank's body (the rectangle chassis).

    Change this value to personalize your tank.
    """

    head_color = "#CCCCCC"
    """
    Hexadecimal RGB color of the tank's head (the circle in the middle).

    Change this value to personalize your tank.
    """

    def __init__(self):
        """
        Initializes the controller.

        Override this method if you want to add any extra persistent state that
        you may need for your tank.
        """
        pass

    def act(self, state: ControllerState) -> ControllerAction:
        """
        Runs this Controller on a tank's state to produce an action that
        determines how the tank will behave in this time step.

        Override this with your own behavior!
        """
        return ControllerAction()

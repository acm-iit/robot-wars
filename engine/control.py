import math

from engine.util import angle_difference as angle_difference    # noqa


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


class ControlInput:
    """
    Object that resembles the current state of the robot. The values in this
    object can be used to determine how the robot should act in the upcoming
    time step, which is written into the ControlOutput.
    """
    def __init__(self):
        self.position: tuple[float, float] = (0, 0)
        """
        Position of the robot, as a tuple `(x, y)` measured from the top-left
        point of the arena.
        """

        self.rotation: float = 0
        """
        Rotation of the robot, in radians measured clockwise from the positive
        X-axis (right).

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.turret_rotation: float = 0
        """
        Rotation of the robot's turret, in radians measured clockwise from the
        positive X-axis (right).

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.enemy_position: tuple[float, float] = (0, 0)
        """
        Position of the enemy robot, as a tuple `(x, y)` measured from the
        top-left point of the arena.

        In the case of multiple enemy robots (i.e. battle royale), this is the
        position of the nearest enemy robot.
        """

        self.enemy_rotation: float = 0
        """
        Rotation of the enemy robot, in radians measured clockwise from the
        positive X-axis (right).

        In the case of multiple enemy robots (i.e. battle royale), this is the
        rotation of the nearest enemy robot.

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.enemy_turret_rotation: float = 0
        """
        Rotation of the enemy robot's turret, in radians measured clockwise
        from the positive X-axis (right).

        In the case of multiple enemy robots (i.e. battle royale), this is the
        rotation of the nearest enemy robot's turret.

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.can_see_enemy: bool = False
        """
        Determines if the robot can see the enemy robot, as a boolean where
        `True` implies it can do so.

        "See" is defined as having line-of-sight with the enemy, with no
        impeding obstacles.

        In the case of multiple enemy robots (i.e. battle royale), this applies
        to the nearest enemy robot.
        """

        self.bullets: list[tuple[float, float, float, float]] = []
        """
        List of positions and velocities of enemy bullets in proximity to the
        robot, as tuples `(x, y, vx, vy)`, where `x` and `y` are the positional
        coordinates measured from the top-left point of the arena, and `vx` and
        `vy` are the velocity components.
        """

        self.coin_position: tuple[float, float] = (0, 0)
        """
        Position of the coin, as a tuple `(x, y)` measured from the top-left
        point of the arena.
        """


class ControlOutput:
    """
    Object the represents the actions the robot will take in the upcoming time
    step. Write into the values of this object to dictate the robot's behavior.
    """
    def __init__(self, input: ControlInput):
        self.__input = input

        self.move_power = 0
        self.turn_power = 0
        self.turret_turn_power = 0

        self.move_toward: tuple[float, float] | None = None
        """
        Position that the robot should move toward using pathfinding, as a
        tuple `(x, y)` measured from the top-left point of the arena.

        This value overrides `move_power`, `turn_power`, and `turn_toward`.

        If unused, set to `None`.
        """

        self.turn_toward = None
        self.aim_toward = None

        self.shoot: bool = False
        """
        Determines if the robot should shoot during this time step.

        `False` represents no shooting, `True` represents shooting.
        """

    @property
    def move_power(self) -> float:
        """
        Current velocity of the robot, represented as a fraction of maximum
        movement speed between `-1` and `1`, inclusive.

        Positive values correspond to moving forwards, while negative values
        correspond to moving backwards.
        """
        self.__move_power = min(max(self.__move_power, -1), 1)
        return self.__move_power

    @move_power.setter
    def move_power(self, move_power: float):
        self.__move_power = min(max(move_power, -1), 1)

    @property
    def turn_power(self) -> float:
        """
        Current angular velocity of the robot, represented as a fraction of
        maximum turning speed between `-1` and `1`, inclusive.

        Positive values correspond to turning clockwise, while negative values
        correspond to turning counter-clockwise.

        (Positive is clockwise because the positive Y-axis is down!)
        """
        self.__turn_power = min(max(self.__turn_power, -1), 1)
        return self.__turn_power

    @turn_power.setter
    def turn_power(self, turn_power: float):
        self.__turn_power = min(max(turn_power, -1), 1)

    @property
    def turret_turn_power(self) -> float:
        """
        Current angular velocity of the turret, represented as a fraction of
        maximum turret turning speed between `-1` and `1`, inclusive.

        Positive values correspond to turning clockwise, while negative values
        correspond to turning counter-clockwise.

        (Positive is clockwise because the positive Y-axis is down!)
        """
        self.__turret_turn_power = min(max(self.__turret_turn_power, -1), 1)
        return self.__turret_turn_power

    @turret_turn_power.setter
    def turret_turn_power(self, turret_turn_power: float):
        self.__turret_turn_power = min(max(turret_turn_power, -1), 1)

    @property
    def turn_toward(self) -> float | None:
        """
        Angle or position that the robot should turn itself toward.

        Angles should be in radians measured clockwise from the positive X-axis
        (right), while positions should be tuples of floats `(x, y)` measured
        from the top-left point of the arena.

        This value overrides `turn_power`.

        If unused, set to `None`.

        (Angles are measured clockwise since the positive Y-axis is down!)
        """
        # Normalize value (in case the user somehow sets internal __turn_toward
        # to an incorrect value)
        if self.__turn_toward is not None:
            self.__turn_toward %= 2 * math.pi

        return self.__turn_toward

    @turn_toward.setter
    def turn_toward(self, target: float | tuple[float, float] | None):
        if target is None:
            self.__turn_toward = None
            return

        # Handle case where target is a position
        if type(target) is tuple:
            target = angle_to(*self.__input.position, *target)

        # Python type checker doesn't seem to understand that target should be
        # a float by here...
        assert type(target) is float, ("turn_toward should be float or tuple "
                                       "of floats")

        self.__turn_toward = target % (2 * math.pi)

    @property
    def aim_toward(self) -> float | None:
        """
        Angle or position that the robot should aim its turret toward.

        Angles should be in radians measured clockwise from the positive X-axis
        (right), while positions should be tuples of floats `(x, y)` measured
        from the top-left point of the arena.

        This value overrides `turret_turn_power`.

        If unused, set to `None`.

        (Angles are measured clockwise since the positive Y-axis is down!)
        """
        # Normalize value (in case the user somehow sets internal __aim_toward
        # to an incorrect value)
        if self.__aim_toward is not None:
            self.__aim_toward %= 2 * math.pi

        return self.__aim_toward

    @aim_toward.setter
    def aim_toward(self, target: float | tuple[float, float] | None):
        if target is None:
            self.__aim_toward = None
            return

        # Handle case where target is a position
        if type(target) is tuple:
            target = angle_to(*self.__input.position, *target)

        # Python type checker doesn't seem to understand that target should be
        # a float by here...
        assert type(target) is float, ("aim_toward should be float or tuple "
                                       "of floats")

        self.__aim_toward = target % (2 * math.pi)


class Controller:
    """
    Class which resembles your robot! Override the methods in this class to
    implement the behavior of your robot.
    """
    def __init__(self, name: str, body_color: str, head_color: str):
        """
        Initializes the controller with a Robot name, body color, and head
        color for display purposes.

        Override this method and call `super().__init__()` with your desired
        name and color values, and add any extra persistent state that you may
        need for your robot.
        """
        self.name = name
        self.body_color = body_color
        self.head_color = head_color

    def act(self, input: ControlInput, output: ControlOutput):
        """
        Runs this Controller on a Robot's input to modify an output that
        determines how the Robot will behave in this time step.

        Override this with your own behavior!
        """
        pass

import math


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

        # self.can_see_robot: bool = False
        # """
        # Determines if the robot can see the enemy robot, as a boolean where
        # `True` implies it can do so.

        # "See" is defined as having line-of-sight with the enemy, with no
        # impeding obstacles.

        # In the case of multiple enemy robots (i.e. battle royale), this
        # applies to the nearest enemy robot.
        # """

        self.bullets: list[tuple[float, float, float, float]] = []
        """
        List of positions and velocities of enemy bullets in proximity to the
        robot, as tuples `(x, y, vx, vy)`, where `x` and `y` are the positional
        coordinates measured from the top-left point of the arena, and `vx` and
        `vy` are the velocity components.
        """

        self.coin: tuple[float, float] = (0, 0)
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

        self.move_to: tuple[float, float] | None = None
        """
        Position that the robot should move towards using pathfinding, as a
        tuple `(x, y)` measured from the top-left point of the arena.

        This value overrides `move_power`, `turn_power`, and `turn_to`.

        If unused, set to `None`.
        """

        self.turn_to: float | None = None
        """
        Angle that the robot should turn itself towards, in radians measured
        clockwise from the positive X-axis (right).

        This value overrides `turn_power`.

        If unused, set to `None`.

        (It is measured clockwise since the positive Y-axis is down!)
        """

        self.aim_at: float | None = None
        """
        Angle that the robot should aim its turret in, in radians measured
        clockwise from the positive X-axis (right).

        This value overrides `turret_turn_power`.

        If unused, set to `None`.

        (It is measured clockwise since the positive Y-axis is down!)
        """

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

    def turn_to_position(self, target: tuple[float, float]):
        """
        Helper function for turning the robot towards a particular point in the
        arena. This sets `turn_to` to the calculated angle between the robot
        and `target`.

        `target` is a tuple of `(x, y)`.

        Note that the robot won't immediately turn to this position in one time
        step, this simply sets the goal rotation.
        """
        target_x, target_y = target
        current_x, current_y = self.__input.position
        difference_x, difference_y = target_x - current_x, target_y - current_y
        self.turn_to = math.atan2(difference_y, difference_x)

    def aim_at_position(self, target: tuple[float, float]):
        """
        Helper function for aiming the robot's turret towards a particular
        point in the arena. This sets `aim_at` to the calculated angle between
        the robot and `target`.

        `target` is a tuple of `(x, y)`.

        Note that the turret won't immediately aim at this position in one time
        step, this simply sets the goal turret rotation.
        """
        target_x, target_y = target
        current_x, current_y = self.__input.position
        difference_x, difference_y = target_x - current_x, target_y - current_y
        self.aim_at = math.atan2(difference_y, difference_x)


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

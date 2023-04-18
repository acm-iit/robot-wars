from random import choice

from engine import Arena, ControlInput, Controller, controllers, ControlOutput


# List of map filenames to pick from randomly if force_map is not set
maps = [
    # "engine/maps/basic.json",
    "engine/maps/circles.json",
    # "engine/maps/circles_large.json",
    # "engine/maps/lock.json",
    "engine/maps/maze.json",
    # "engine/maps/stress_test.json",
]

# If set, use this map instead of a random one above
force_map = None

# List of enemy robot controllers to pick from randomly if force_controller is
# not set
enemies = [
    controllers.SpinController,
    controllers.AggressiveController,
    controllers.GreedyController,
    controllers.AggreedyController
]

# If set, use this enemy controller instead of a random one above
force_enemy = None


class MyController(Controller):
    def __init__(self):
        super().__init__("MyRobot", "#EEEEEE", "#CCCCCC")

    def act(self, input: ControlInput, output: ControlOutput):
        output.move_to = input.enemy_position
        output.aim_at_position(input.enemy_position)
        output.shoot = True


if __name__ == "__main__":
    map = force_map if force_map is not None else choice(maps)
    arena = Arena.from_map_json(map)

    if arena is None:
        quit(1)

    # Add enemy robot
    enemy = (force_enemy if force_enemy is not None else choice(enemies))()
    arena.add_robot(enemy)

    # Add your robot
    arena.add_robot(MyController())

    # Spawn the robots
    arena.spawn_robots()

    # Run the simulation
    arena.run()

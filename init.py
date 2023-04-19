from random import choice

from engine import (Arena, Controller, controllers, ControllerAction,
                    ControllerState)

# List of available maps
maps = [
    "engine/maps/basic.json",
    "engine/maps/circles.json",
    "engine/maps/circles_large.json",
    "engine/maps/lock.json",
    "engine/maps/maze.json",
    "engine/maps/stress_test.json",
]

# If set, use this map instead of a random one above
map = maps[5]

# List of enemy robot controllers
enemies = [
    controllers.SpinController,
    controllers.AggressiveController,
    controllers.GreedyController,
    controllers.AggreedyController
]

# If set, use this enemy controller only instead of randomly chosen ones
enemy = None


# Implement your controller here!
class MyController(Controller):
    def __init__(self):
        super().__init__("MyRobot", "#EEEEEE", "#CCCCCC")

    def act(self, state: ControllerState) -> ControllerAction:
        return ControllerAction()


if __name__ == "__main__":
    map = map if map is not None else choice(maps)
    arena = Arena.from_map_json(map)

    if arena is None:
        quit(1)

    # Uncomment the below to show FPS
    # arena.show_fps = True

    # Add enemy robot(s)
    for i in range(15):
        chosen_enemy = enemy if enemy is not None else choice(enemies)
        arena.add_robot(chosen_enemy())

    # Add your robot
    arena.add_robot(MyController())

    # Uncomment the next line to add a human robot controlled by you, if you
    # want!
    # arena.add_robot(controllers.HumanController(arena))

    # Spawn the robots
    arena.spawn_robots()

    # Run the simulation
    arena.run()

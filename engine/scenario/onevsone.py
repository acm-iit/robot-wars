import sys

from engine.arena import Arena
from engine.control import Controller
from engine.controllers import HumanController

MAP_FILENAME = "engine/maps/circles.json"
DURATION = 60


def one_vs_one(controller1: type[Controller], controller2: type[Controller],
               show_fps: bool = False):
    """
    Runs two controller classes in a one versus one environment. The map is a
    medium square map with two sets of concentric circular walls.

    Optional parameter `show_fps` can be set to show FPS in the top left.
    """
    arena = Arena.from_map_json(MAP_FILENAME)
    if arena is None:
        sys.exit("Invalid map; exiting")

    arena.show_fps = show_fps

    controller_classes = [controller1, controller2]

    for controller_class in controller_classes:
        # Initialize controller
        controller = None
        if controller_class is HumanController:
            # HumanController has special Arena parameter in __init__
            controller = HumanController(arena)
        else:
            controller = controller_class()

        arena.add_robot(controller)

    arena.spawn_robots()

    results = arena.run(DURATION)
    print("RESULTS:")

    controller_results = list[type[Controller]]()
    for _, controller, place in results:
        print(f"{place}. {controller.name}")
        controller_results.append(type(controller))

    return controller_results[0]

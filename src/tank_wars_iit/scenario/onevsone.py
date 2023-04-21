import sys

from tank_wars_iit._engine.arena import Arena
from tank_wars_iit._engine.control import Controller
from tank_wars_iit.examples.controllers import HumanController

MAP_FILENAME = "circles.json"
DURATION = 60


def one_vs_one(controller1: type[Controller], controller2: type[Controller],
               show_fps=False, show_mouse_coordinates=False):
    """
    Runs two controller classes in a one versus one environment. The map is a
    medium square map with two sets of concentric circular walls.

    Optional parameter `show_fps` can be set to `True` to show FPS in the top
    left.

    Optional parameter `show_mouse_coordinates` can be set to `True` to show
    the user mouse coordinates (in game space) in the top-left; this can be
    useful for figuring out certain coordinates in the map that you want your
    tank to be aware of.
    """
    arena = Arena.from_map_json(MAP_FILENAME)
    if arena is None:
        sys.exit("Invalid map; exiting")

    arena.show_fps = show_fps
    arena.show_mouse_coordinates = show_mouse_coordinates

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
    if results is None:
        return None

    print("RESULTS:")

    controller_results = list[type[Controller]]()
    for _, controller, place in results:
        print(f"{place}. {controller.name}")
        controller_results.append(type(controller))

    return controller_results[0]

import sys

from tank_wars_iit._engine.arena import Arena
from tank_wars_iit._engine.control import Controller
from tank_wars_iit.examples.controllers import HumanController

MAP_FILENAME = "stress_test.json"
DURATION = 180


def battle_royale(controller_classes: list[type[Controller]],
                  show_fps=False, show_mouse_coordinates=False,
                  lock_camera=False):
    """
    Runs a list of controller classes in a battle royale environment. The map
    is a vast, square map with the walls slowly closing in towards the center,
    similar to a zone in a battle royale game.

    Optional parameter `show_fps` can be set to `True` to show FPS in the top
    left.

    Optional parameter `show_mouse_coordinates` can be set to `True` to show
    the user mouse coordinates (in game space) in the top-left; this can be
    useful for figuring out certain coordinates in the map that you want your
    tank to be aware of.

    Optional parameter `lock_camera` can be set to `True` to keep the camera
    from zooming in on the playable area. This can be used in conjunction with
    `show_mouse_coordinates` to make it easier to find coordinates.
    """
    arena = Arena.from_map_json(MAP_FILENAME)
    if arena is None:
        sys.exit("Invalid map; exiting")

    arena.show_fps = show_fps
    arena.show_mouse_coordinates = show_mouse_coordinates
    arena.shrink_zoom = not lock_camera
    arena.shrink_rate = 32
    arena.use_pathfinding = False

    for controller_class in controller_classes:
        # Initialize controller
        controller = None
        if controller_class is HumanController:
            # HumanController has special Arena parameter in __init__
            controller = HumanController(arena)
        else:
            controller = controller_class()

        arena.add_robot(controller)

    robots = arena.spawn_robots()
    for robot in robots:
        robot.is_battle_royale = True

    results = arena.run(DURATION)
    if results is None:
        return None

    print("RESULTS:")

    controller_results = list[type[Controller]]()
    for _, controller, place in results:
        print(f"{place}. {controller.name}")
        controller_results.append(type(controller))

    return controller_results

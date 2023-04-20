from engine.arena import Arena
from engine.control import Controller
from engine.controllers import HumanController

MAP_FILENAME = "engine/maps/stress_test.json"
DURATION = 180


def battle_royale(controller_classes: list[type[Controller]],
                  show_fps: bool = False):
    """
    Runs a list of controller classes in a battle royale environment. The map
    is a vast, square map with the walls slowly closing in towards the center,
    similar to a zone in a battle royale game.

    Optional parameter `show_fps` can be set to show FPS in the top left.
    """
    arena = Arena.from_map_json(MAP_FILENAME)
    if arena is None:
        print("Invalid map; exiting")
        exit(1)

    arena.show_fps = show_fps

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

    return controller_results

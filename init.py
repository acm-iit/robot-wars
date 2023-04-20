from engine import Controller, controllers, ControllerAction, ControllerState
from engine import battle_royale
# from engine import one_vs_one
# from engine import tournament


# Implement your controller here!
class MyController(Controller):
    def __init__(self):
        self.name = "MyRobot"
        self.body_color = "#EEEEEE"
        self.head_color = "#CCCCCC"

    def act(self, state: ControllerState) -> ControllerAction:
        return ControllerAction()


if __name__ == "__main__":
    # List of tank controllers to use in the simulation
    enemies = [
        controllers.HumanController,
        controllers.SpinController,
        controllers.AggressiveController,
        controllers.GreedyController,
        controllers.AggreedyController
    ]

    # Run a battle royale simulation (set show_fps=True to show FPS if needed)
    battle_royale(enemies, show_fps=False)

    # Run a 1 vs. 1 simulation between 2 robots
    # one_vs_one(controllers.HumanController, controllers.AggreedyController)

    # tournament(enemies, show_fps=False)

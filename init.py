from engine import (battle_royale, Controller, controllers, ControllerAction,
                    ControllerState)


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

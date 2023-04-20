from engine import Controller, controllers, ControllerAction, ControllerState
from engine import battle_royale
from engine import one_vs_one


# Implement your controller here!
# Change the class name to something unique
class MyController(Controller):
    # Change the following values to personalize your tank
    name = "MyTank"
    body_color = "#EEEEEE"
    head_color = "#CCCCCC"

    def __init__(self):
        # Add any initialization logic you need here!
        pass

    def act(self, state: ControllerState) -> ControllerAction:
        action = ControllerAction()

        # Program your tank's actions in this function!
        # Here's one to start you off...
        action.move_toward = state.coin_position

        return action


if __name__ == "__main__":
    # List of tank controllers to use in the simulation
    enemies = [
        controllers.HumanController,        # Human-controlled tank
        controllers.SpinController,         # Randomly spinning tank
        controllers.AggressiveController,   # Killer tank
        controllers.GreedyController,       # Coin-loving tank
        controllers.AggreedyController,     # Killer + coin-loving tank
        MyController                        # Your tank
    ]

    # Run a battle royale simulation (set show_fps=True to show FPS if needed)
    battle_royale(enemies, show_fps=False)

    # Run a 1 vs. 1 simulation between 2 tanks
    one_vs_one(MyController, controllers.HumanController)

from tank_wars_iit import Controller, ControllerAction, ControllerState
import tank_wars_iit.examples as examples
import tank_wars_iit.scenario as scenario


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
        examples.HumanController,       # Human-controlled tank
        examples.SpinController,        # Randomly spinning tank
        examples.AggressiveController,  # Killer tank
        examples.GreedyController,      # Coin-loving tank
        examples.AggreedyController,    # Killer + coin-loving tank
        MyController                    # Your tank
    ]

    # Run a battle royale simulation
    scenario.battle_royale(enemies)

    # Run a 1 vs. 1 simulation between 2 tanks
    scenario.one_vs_one(MyController, examples.HumanController)

    # Run a tournament
    scenario.tournament(enemies)

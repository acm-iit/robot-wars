# Robot Wars

Engine for the Robot Wars hack night.

## Requirements

* Python 3.10
* pygame 2.3.0 (SDL 2.24.2, Python 3.10.2)

## How do I run it?

Run `init.py` in Python. (This is a testing script and will be changed/moved in the future.)

## Structure

* `engine` - Package containing full Robot Wars engine.
    * `entity` - Package containing all `Entity` classes supported by the engine.
        * `bullet.py` - Contains the `Bullet` class (inherits `Entity`); represents a bullet that moves in the direction it faces, bounces off walls, and collides with `Robot`s.
        * `entity.py` - Contains the `Entity` abstract class, which represents a geometric object in an `Arena`.
        * `robot.py` - Contains the `Robot` class (inherits `Entity`); represents a robot that can move, turn, turn its turret, and shoot `Bullet`s.
        * `wall.py` - Contains the `Wall` class (inherits `Entity`); represents a static, unmovable barrier.
    * `maps` - Directory containing map JSON files which can be used to easily instantiate an `Arena` with `Wall`s and spawn locations.
        * `basic.json` - A small, wide map with five `Wall`s and two spawns.
        * `circles.json` - A medium, square map with two concentric circles of `Wall`s and four spawns.
        * `stress_test.json` - A large, square map with no `Wall`s and 64 spawns, meant for stress testing the engine.
    * `util` - Package containing engine utility modules.
        * `draw.py` - Contains helper functions for drawing gradients on screen.
        * `geometry.py` - Contains helper functions for collision detection between two convex polygons.
    * `arena.py` - Contains the `Arena` class, which represents a battle arena for one or more `Robot`s.
    * `map.py` - Contains type definitions and guards for the map JSON format.
    * `quadtree.py` - Contains the `Quadtree` class, which is a data structure used to optimize collision filtering.
* `tools` - Useful scripts to automate workflows.
    * `generate_circles.py` - Generates the `engine/maps/circles.json` map.
    * `generate_stress_test.py` - Generates the `engine/maps/stress_test.json` map.
* `init.py` - Loads an `Arena` from a map, spawns a user-controlled `Robot` and several NPC `Robot`s, and runs the simulation with visuals. Used for testing.

## To Do

* Map Creation
    * **[IMPLEMENTED]** *1v1 Map* - For now, we can use `engine/maps/circles.json`.
    * *Battle Royale Map* - Extra-large map with adequate `Wall`s spread across the map.
    * *Zoom-In* - Useful for observing the battle royale map!
* Optimization
    * **[IMPLEMENTED]** *Quadtree Collision Filtering* - Use a `Quadtree` data structure to filter which collisions to check for as opposed to checking every pair of `Entity`s.
    * *Parallelize `Entity.update`* - Invoke all calls of `Entity.update` in parallel since they operate independently.
    * *Parallelize `Entity.handle_collision`* - Invoke all calls of `Entity.handle_collision` in parallel; modify the method to return new `position` and `rotation` properties that will be applied in parallel.
* Game Rules
    * *`Robot` Destruction* - Incorporate health in `Robot` and damage in `Bullet`. For now, we use one-shot kills.
    * *Win Condition* - Destroy the other `Robot`.
    * *Stalemate Condition* - Both `Robot`s are still alive after *n* seconds of simulation.
    * *Secondary Win Condition* - In case of stalemate, use this condition as a tiebreaker. Some ideas:
        * *Portion of `Arena` Discovered* - Reward the `Robot` who ventured out the most.
        * *Coins* - Place `Coin` entities around the `Arena`; whichever `Robot` collects the most wins in case of stalemate.
* `Robot` Programmability
    * *`RobotControl` Class* - Class which each team extends to personalize and program the behavior of their `Robot`.
    * *Engine Encapsulation* - Prevent raw access to any `Entity`s or the `Arena`; the only accessible component is the `RobotControl` class.
    * *`Entity` Detection* - Expose API in `RobotControl` to figure out the direction and proximity of other `Entity`s.
    * *`Robot` Manipulation* - Expose API in `RobotControl` to move and turn the `Robot` and shoot `Bullet`s. For now, it's implemented as the `Robot.on_update` callback, which is unideal.
* `Robot` Personalization
    * **[IMPLEMENTED]** *Color* - Set `Robot` colors via properties `color` and `head_color`.
    * *Size* - Set `Robot` size; larger size increases health and decreases speed.
* `Robot` Examples
* Unit Tests
* Prepare for Distribution

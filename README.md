# Robot Wars

Engine for the Robot Wars hack night.

## Requirements

* Python 3.10
* pygame 2.3.0 (SDL 2.24.2, Python 3.10.2)

## How do I run it?

Run `init.py` in Python.

## Structure

* `init.py` - Simply creates an Arena, adds a user-controlled robot and an npc robot, and runs the simulation. This is largely meant for testing.
* `arena.py` - Contains the Arena class, which represents a battle arena for one or more robots.
* `entity.py` - Contains the Entity abstract class, which represents a geometric object in an Arena.
* `robot.py` - Contains the Robot class (inherits Entity), represents a robot that can move, turn, turn its turret, and shoot bullets.
* `bullet.py` - Contains the Bullet class (inherits Entity), represents a bullet that moves in the direction it faces, bounces off walls, and collides with robots.
* `wall.py` - Contains the Wall class (inherits Entity), represents a static, unmovable barrier.
* `geometry.py` - Contains helper functions for collision detection between two convex polygons.

## To Do

* Create a map for 1v1 robot fights
* Program rules for a game round
    * Robot destruction (will it be 1-shot, or HP?)
    * Win condition (destroy the other robot? maybe something else?)
    * Stalemate condition (robots do nothing for X ticks)
* Add scanning/sensor capabilities
    * Robot scans in a direction, returns distance between robot and detected object and object type
    * This is up in the air, we don't want it to be too hard to program the robot
* Robot personalization
    * Set robot color
    * Set robot size (tradeoffs)
    * Set robot speed (tradeoffs; e.g. higher speed --> less bullet damage)
* Create baseline robot(s) for demonstration purposes

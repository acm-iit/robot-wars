"""
Testing script which loads a map, creates a controllable robot, creates several
NPC robots, and simulates.
"""
from random import random

import pygame

from engine import Arena, Robot

Vector2 = pygame.Vector2


def human_controller_factory(arena: Arena):
    """Creates a human control scheme for a Robot given an Arena."""
    def human_controller(robot: Robot, dt: float):
        keys = pygame.key.get_pressed()

        # Change motion power
        robot.move_power = (-1 if keys[pygame.K_s] else 1 if keys[pygame.K_w]
                            else 0)
        robot.turn_power = (-1 if keys[pygame.K_a] else 1 if keys[pygame.K_d]
                            else 0)

        window_point = Vector2(pygame.mouse.get_pos())
        arena_point = arena.window_to_arena(window_point)
        down, *_ = pygame.mouse.get_pressed()

        if not arena.show_paths:
            # Aim turret towards mouse
            robot.aim_towards(arena_point, dt)
            # Shoot
            if down:
                robot.shoot()
        else:
            # Click to test pathfinding (with Arena.show_paths = True)
            if down:
                # Simply generate the path without using it, for viz purposes
                robot.pathfind(arena_point)

    return human_controller


def seek_point_pathfinding(robot: Robot, point: Vector2, dt: float) -> bool:
    """Helper function for moving a Robot towards a point via pathfinding."""
    # Figure out path towards point
    path = robot.pathfind(point)
    if path is None:
        return False

    robot.move_towards(path[0], dt)

    return True


def seek_robot_controller_factory(target: Robot):
    """Creates a control scheme to seek a certain robot with pathfinding."""
    def control(robot: Robot, dt: float):
        if seek_point_pathfinding(robot, target.position, dt):
            robot.aim_towards(target.position, dt)
            robot.shoot()

    return control


def seek_nearest_robot_controller(robot: Robot, dt: float):
    """Control scheme for seeking the nearest robot with pathfinding."""
    nearest = robot.nearest_robot
    if nearest is None:
        return
    if seek_point_pathfinding(robot, nearest.position, dt):
        robot.aim_towards(nearest.position, dt)
        robot.shoot()


def seek_coin_controller(robot: Robot, dt: float):
    """Control scheme for seeking the nearest coin with pathfinding."""
    coin = robot.coin
    if coin is None:
        return

    # Move towards coin
    seek_point_pathfinding(robot, coin, dt)


def seek_coin_shoot_controller(robot: Robot, dt: float):
    """
    Control scheme for seeking the coin with pathfinding and shooting enemies.
    """
    seek_coin_controller(robot, dt)

    nearest = robot.nearest_robot
    if nearest is None:
        return

    robot.aim_towards(nearest.position, dt)
    robot.shoot()


def spin_controller_factory():
    """Creates random spinning control scheme for a Robot."""
    move_power = random() * 2 - 1
    turn_power = random() * 2 - 1
    turret_turn_power = random() * 2 - 1

    def spin_control(robot: Robot, _):
        robot.shoot()
        robot.move_power = move_power
        robot.turn_power = turn_power
        robot.turret_turn_power = turret_turn_power

    return spin_control


if __name__ == "__main__":
    # Load the map
    arena = Arena.from_map_json("engine/maps/maze.json")
    if arena is None:
        quit()

    # Create the player robot
    player_robot = Robot("Player")
    player_robot.color = "#0000EE"
    player_robot.head_color = "#0000CC"
    player_robot.on_update = human_controller_factory(arena)

    robots = [player_robot]

    # You can configure how many of each type of NPC Robot you want in the
    # `range` parameters of the for-loops below, just make sure the total
    # number doesn't exceed the spawn count for the map.

    # These Robots seek the player Robot
    for i in range(0):
        npc_robot = Robot(f"NPC {len(robots)}")
        npc_robot.on_update = seek_robot_controller_factory(player_robot)
        robots.append(npc_robot)

    # These Robots seek the nearest Robot
    for i in range(0):
        npc_robot = Robot(f"NPC {len(robots)}")
        npc_robot.on_update = seek_nearest_robot_controller
        robots.append(npc_robot)

    # These Robots seek the nearest Coin
    for i in range(0):
        npc_robot = Robot(f"NPC {len(robots)}")
        npc_robot.on_update = seek_coin_controller
        robots.append(npc_robot)

    # These Robots seek the Coin and shoot enemy robots
    for i in range(1):
        npc_robot = Robot(f"NPC {len(robots)}")
        npc_robot.on_update = seek_coin_shoot_controller
        robots.append(npc_robot)

    # These Robots spin, move, and shoot randomly
    for i in range(0):
        npc_robot = Robot(f"NPC {len(robots)}")
        npc_robot.on_update = spin_controller_factory()
        robots.append(npc_robot)

    arena.spawn_robots_old(robots)

    # Debug setting configuration:

    # Shows hitboxes as red outlines around each entity.
    arena.show_hitboxes = False

    # Shows FPS in the top-left corner of the window.
    arena.show_fps = False

    # Shows the Quadtree; draws small blue circles at each node's region
    # center, draws blue edges between them, and draws blue bounding rectangles
    # around each entity.
    arena.show_quadtree = False

    # Shows the nearest-robot relations between Robots as green lines.
    arena.show_nearest_robot = False

    # Shows the pathfinding hitboxes for Walls in white.
    arena.show_pathfinding_hitbox = False

    # Shows the pathfinding graph in magenta.
    arena.show_path_graph = False

    # Shows all paths calculated by all entities in each frame in yellow.
    arena.show_paths = False

    # Shows the nearest pathfinding nodes for each Robot in cyan.
    arena.show_robot_nodes = False

    # Launch simulation
    arena.run()

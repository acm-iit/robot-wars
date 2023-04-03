import pygame
from random import random

from engine import Arena, Robot

def keyboard_control(robot: Robot):
    keys = pygame.key.get_pressed()
    robot.move_power = -1 if keys[pygame.K_s] else 1 if keys[pygame.K_w] else 0
    robot.turn_power = -1 if keys[pygame.K_a] else 1 if keys[pygame.K_d] else 0
    robot.turret_turn_power = -1 if keys[pygame.K_q] else 1 if keys[pygame.K_e] else 0
    if keys[pygame.K_SPACE]:
        robot.shoot()

def create_spin_control():
    move_power = random() * 2 - 1
    turn_power = random() * 2 - 1
    turret_turn_power = random() * 2 - 1
    def spin_control(robot: Robot):
        robot.shoot()
        robot.move_power = move_power
        robot.turn_power = turn_power
        robot.turret_turn_power = turret_turn_power

    return spin_control

arena = Arena.from_map_json("engine/maps/circles.json")
if arena is None:
    quit()

robots = []

player_robot = Robot()
player_robot.color = "#0000EE"
player_robot.head_color = "#0000CC"
player_robot.on_update = keyboard_control

robots.append(player_robot)

for i in range(3):
    npc_robot = Robot()
    npc_robot.on_update = create_spin_control()
    robots.append(npc_robot)

arena.spawn_entities(robots)

#arena.show_hitboxes = True
#arena.show_fps = True
#arena.show_quadtree = True
arena.run()

import pygame

from arena import Arena
from robot import Robot

def keyboard_control(robot: Robot):
    keys = pygame.key.get_pressed()
    robot.move_power = -1 if keys[pygame.K_s] else 1 if keys[pygame.K_w] else 0
    robot.turn_power = -1 if keys[pygame.K_a] else 1 if keys[pygame.K_d] else 0
    robot.turret_turn_power = -1 if keys[pygame.K_q] else 1 if keys[pygame.K_e] else 0
    if keys[pygame.K_SPACE]:
        robot.shoot()

def spin_control(robot: Robot):
    robot.shoot()
    robot.move_power = 1
    robot.turn_power = 1
    robot.turret_turn_power = -1

arena = Arena.from_map_json("circles.json")
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
    npc_robot.on_update = spin_control
    robots.append(npc_robot)

arena.spawn_entities(robots)

#arena.show_hitboxes = True
#arena.show_fps = True
#arena.show_quadtree = True
arena.run()

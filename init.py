import pygame

from arena import Arena
from robot import Robot

arena = Arena.from_map_json("circles.json")
if arena is None:
    quit()

player_robot = Robot()

def player_on_update():
    keys = pygame.key.get_pressed()
    player_robot.move_power = -1 if keys[pygame.K_s] else 1 if keys[pygame.K_w] else 0
    player_robot.turn_power = -1 if keys[pygame.K_a] else 1 if keys[pygame.K_d] else 0
    player_robot.turret_turn_power = -1 if keys[pygame.K_q] else 1 if keys[pygame.K_e] else 0
    if keys[pygame.K_SPACE]:
        player_robot.shoot()

player_robot.on_update = player_on_update

npc_robot = Robot()

def npc_on_update():
    npc_robot.shoot()
    npc_robot.move_power = 1
    npc_robot.turn_power = 1
    npc_robot.turret_turn_power = -1

npc_robot.on_update = npc_on_update

arena.spawn_entities([player_robot, npc_robot])

arena.show_hitboxes = True
arena.run()

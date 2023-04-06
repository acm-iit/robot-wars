# flake8: noqa
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from engine.arena import Arena as Arena
from engine.entity import Bullet as Bullet
from engine.entity import Entity as Entity
from engine.entity import Robot as Robot
from engine.entity import Wall as Wall
from engine.entity.robot import ROBOT_RADIUS as ROBOT_RADIUS

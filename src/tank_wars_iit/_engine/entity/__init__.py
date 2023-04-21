# flake8: noqa

# Import Entity base class first as it's a common dependency between all entities
from tank_wars_iit._engine.entity.entity import Entity as Entity

from tank_wars_iit._engine.entity.bullet import Bullet as Bullet
from tank_wars_iit._engine.entity.coin import Coin as Coin
from tank_wars_iit._engine.entity.robot import Robot as Robot
from tank_wars_iit._engine.entity.wall import Wall as Wall

from typing import Any, List, TypedDict, TypeGuard

number = int | float

class SizeJSON(TypedDict):
    width: number
    height: number

class PositionJSON(TypedDict):
    x: number
    y: number

class WallJSON(TypedDict):
    position: PositionJSON
    size: SizeJSON

class MapJSON(TypedDict):
    size: SizeJSON
    walls: List[WallJSON]
    spawns: List[PositionJSON]

def is_number(n: Any) -> TypeGuard[number]:
    return (type(n) is int) or (type(n) is float)

def is_size(size: Any) -> TypeGuard[SizeJSON]:
    return type(size) is dict \
        and "width" in size and is_number(size["width"]) \
        and "height" in size and is_number(size["height"])

def is_position(position: Any) -> TypeGuard[PositionJSON]:
    return type(position) is dict \
        and "x" in position and is_number(position["x"]) \
        and "y" in position and is_number(position["y"])

def is_wall(wall: Any) -> TypeGuard[WallJSON]:
    return type(wall) is dict \
        and "size" in wall and is_size(wall["size"]) \
        and "position" in wall and is_position(wall["position"])

def is_map(map: Any) -> TypeGuard[MapJSON]:
    """
    Determines if a value is a Map JSON formatted dictionary.
    """
    return type(map) is dict \
        and "size" in map and is_size(map["size"]) \
        and "walls" in map and type(map["walls"]) is list and all(is_wall(wall) for wall in map["walls"]) \
        and "spawns" in map and type(map["spawns"]) is list and all(is_position(spawn) for spawn in map["spawns"])

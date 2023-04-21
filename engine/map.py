from typing import Any, TypedDict, TypeGuard

Number = int | float


class SizeJson(TypedDict):
    width: Number
    height: Number


class PositionJson(TypedDict):
    x: Number
    y: Number


class WallJson(TypedDict):
    position: PositionJson
    size: SizeJson
    rotation: Number


class MapJson(TypedDict):
    size: SizeJson
    walls: list[WallJson]
    spawns: list[PositionJson]


def is_number(n: Any) -> TypeGuard[Number]:
    return (type(n) is int) or (type(n) is float)


def is_size(size: Any) -> TypeGuard[SizeJson]:
    return (type(size) is dict
            and "width" in size and is_number(size["width"])
            and "height" in size and is_number(size["height"]))


def is_position(position: Any) -> TypeGuard[PositionJson]:
    return (type(position) is dict
            and "x" in position and is_number(position["x"])
            and "y" in position and is_number(position["y"]))


def is_wall(wall: Any) -> TypeGuard[WallJson]:
    return (type(wall) is dict
            and "size" in wall and is_size(wall["size"])
            and "position" in wall and is_position(wall["position"])
            and "rotation" in wall and is_number(wall["rotation"]))


def is_map(map: Any) -> TypeGuard[MapJson]:
    """Determines if a value is a Map JSON formatted dictionary."""
    return (type(map) is dict
            and "size" in map and is_size(map["size"])
            and "walls" in map and type(map["walls"]) is list
            and all(is_wall(wall) for wall in map["walls"])
            and "spawns" in map and type(map["spawns"]) is list
            and all(is_position(spawn) for spawn in map["spawns"]))

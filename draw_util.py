import math
import pygame
from typing import List, Sequence, Tuple, Union

Surface = pygame.Surface
Vector2 = pygame.Vector2
Color = pygame.Color
ColorValue = Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]]

def draw_gradient(color1: ColorValue, color2: ColorValue, size: Vector2) -> Surface:
    """
    Draws a horizontal gradient surface of size `size`, with `color1` on the left and `color2` on the right.
    """
    surface = Surface(Vector2(2, 2), flags=pygame.SRCALPHA)
    pygame.draw.line(surface, color1, Vector2(0, 0), Vector2(0, 1))
    pygame.draw.line(surface, color2, Vector2(1, 0), Vector2(1, 1))
    surface = pygame.transform.smoothscale(surface, size)
    return surface

def draw_gradient_line(surface: Surface, color1: ColorValue, color2: ColorValue, point1: Vector2, point2: Vector2, width: int):
    """
    Draws a gradient line of width `width`.
    """
    gradient_surface = draw_gradient(color1, color2, Vector2((point2 - point1).magnitude(), width))
    angle = -math.degrees(math.atan2(point2.y - point1.y, point2.x - point1.x))
    gradient_surface = pygame.transform.rotate(gradient_surface, angle)
    surface_size = Vector2(gradient_surface.get_size())
    surface.blit(gradient_surface, (point1 + point2) / 2 - surface_size / 2)

def draw_gradient_path(surface: Surface, color1: ColorValue, color2: ColorValue, points: List[Vector2], width: int):
    """
    Draws gradient lines along a path of points.
    """
    total_distance = sum((points[i + 1] - points[i]).magnitude() for i in range(len(points) - 1))
    if total_distance == 0:
        return
    distance_travelled = 0

    color1 = Color(color1)
    color2 = Color(color2)

    for i in range(len(points) - 1):
        pointA, pointB = points[i], points[i + 1]
        distance = (pointB - pointA).magnitude()
        colorA = color1.lerp(color2, distance_travelled / total_distance)
        colorB = color1.lerp(color2, (distance_travelled + distance) / total_distance)
        
        draw_gradient_line(surface, colorA, colorB, pointA, pointB, width)

        distance_travelled += distance

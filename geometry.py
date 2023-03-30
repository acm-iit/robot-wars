import math
import pygame
from typing import List, Optional

Vector2 = pygame.Vector2

def project_polygon_onto_axis(polygon: List[Vector2], axis: Vector2):
    """
    Projects a polygon onto a given axis.
    """
    dots = [vertex.dot(axis) for vertex in polygon]
    return min(dots), max(dots)

def check_polygon_overlap(polygon1: List[Vector2], polygon2: List[Vector2], axis: Vector2):
    """
    Checks if two polygons overlap on a given axis.
    """
    min1, max1 = project_polygon_onto_axis(polygon1, axis)
    min2, max2 = project_polygon_onto_axis(polygon2, axis)
    return max1 >= min2 and max2 >= min1

def get_polygon_axes(polygon: List[Vector2]) -> List[Vector2]:
    """
    Gets the axes to check for overlap for a polygon.
    """
    axes = []
    for i in range(len(polygon)):
        vertex1 = polygon[i]
        vertex2 = polygon[(i + 1) % len(polygon)]
        edge = vertex2 - vertex1
        axis = Vector2(-edge.y, edge.x)
        axes.append(axis.normalize())
    return axes

def check_polygon_collision(polygon1: List[Vector2], polygon2: List[Vector2]):
    """
    Checks if two polygons intersect.
    """
    axes = get_polygon_axes(polygon1) + get_polygon_axes(polygon2)
    for axis in axes:
        if not check_polygon_overlap(polygon1, polygon2, axis):
            return False
    return True

def interval_mtv(min1: float, max1: float, min2: float, max2: float) -> Optional[float]:
    """
    Gets the one-dimensional minimum translation for two intervals.
    """
    right = max2 - min1
    left = max1 - min2
    if left < 0 or right < 0:
        return None
    elif right < left:
        return right
    else:
        return -left

def get_minimum_translation_vector(polygon1: List[Vector2], polygon2: List[Vector2]):
    """
    Gets the minimum translation vector to separate two polygons.
    """
    mtv = Vector2()
    overlap = math.inf
    axes = get_polygon_axes(polygon1) + get_polygon_axes(polygon2)
    for axis in axes:
        min1, max1 = project_polygon_onto_axis(polygon1, axis)
        min2, max2 = project_polygon_onto_axis(polygon2, axis)
        axis_mtv = interval_mtv(min1, max1, min2, max2)
        if axis_mtv is not None and abs(axis_mtv) < overlap:
            overlap = abs(axis_mtv)
            mtv = axis * axis_mtv
    return mtv

import math
from typing import Optional

import pygame

Vector2 = pygame.Vector2


def project_polygon_onto_axis(polygon: list[Vector2], axis: Vector2):
    """Projects a polygon onto a given axis."""
    dots = [vertex.dot(axis) for vertex in polygon]
    return min(dots), max(dots)


def check_polygon_overlap(polygon1: list[Vector2], polygon2: list[Vector2],
                          axis: Vector2):
    """Checks if two polygons overlap on a given axis."""
    min1, max1 = project_polygon_onto_axis(polygon1, axis)
    min2, max2 = project_polygon_onto_axis(polygon2, axis)
    return max1 >= min2 and max2 >= min1


def get_polygon_axes(polygon: list[Vector2]) -> list[Vector2]:
    """Gets the axes to check for overlap for a polygon."""
    axes = []
    for i in range(len(polygon)):
        vertex1 = polygon[i]
        vertex2 = polygon[(i + 1) % len(polygon)]
        edge = vertex2 - vertex1
        axis = Vector2(-edge.y, edge.x)
        axes.append(axis.normalize())
    return axes


def check_polygon_collision(polygon1: list[Vector2], polygon2: list[Vector2]):
    """Checks if two polygons intersect."""
    axes = get_polygon_axes(polygon1) + get_polygon_axes(polygon2)
    for axis in axes:
        if not check_polygon_overlap(polygon1, polygon2, axis):
            return False
    return True


def interval_mtv(min1: float, max1: float, min2: float, max2: float
                 ) -> Optional[float]:
    """Gets the one-dimensional minimum translation for two intervals."""
    right = max2 - min1
    left = max1 - min2
    if left < 0 or right < 0:
        return None
    elif right < left:
        return right
    else:
        return -left


def get_minimum_translation_vector(polygon1: list[Vector2],
                                   polygon2: list[Vector2]):
    """Gets the minimum translation vector to separate two polygons."""
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


def is_point_in_polygon(point: Vector2, polygon: list[Vector2]):
    """Determines if a point is in a convex polygon."""
    sign = 0

    for i in range(len(polygon)):
        vertex1 = polygon[i]
        vertex2 = polygon[(i + 1) % len(polygon)]

        side_direction = vertex2 - vertex1
        normal = Vector2(-side_direction.y, side_direction.x)
        diff = point - vertex1

        dot = diff.dot(normal)
        dot_sign = 0 if dot == 0 else -1 if dot < 0 else 1

        if sign == 0:
            sign = dot_sign
        elif dot_sign != 0 and dot_sign != sign:
            return False

    return True


def angle_difference(angle1: float, angle2: float) -> float:
    """
    Returns the angle difference that should be added to angle1 to direct it
    towards angle2.
    """
    diff = (angle2 - angle1) % (2 * math.pi)
    if diff < math.pi:
        return diff
    else:
        # The shorter direction is counter-clockwise
        return -(2 * math.pi - diff)


def line_segment_intersection(a1: Vector2, a2: Vector2,
                              b1: Vector2, b2: Vector2):
    """
    Compute the (t, u) intersection parameters' numerators as well as their
    denominator for two line segments.
    """
    denom = (a1.x - a2.x) * (b1.y - b2.y) - (a1.y - a2.y) * (b1.x - b2.x)
    if denom == 0:
        return None
    t_num = (a1.x - b1.x) * (b1.y - b2.y) - (a1.y - b1.y) * (b1.x - b2.x)
    u_num = (a1.x - b1.x) * (a1.y - a2.y) - (a1.y - b1.y) * (a1.x - a2.x)
    return t_num, u_num, denom


def check_segment_intersection(a1: Vector2, a2: Vector2,
                               b1: Vector2, b2: Vector2):
    """Checks if two line segments intersect."""
    result = line_segment_intersection(a1, a2, b1, b2)
    if result is None:
        return False
    t_num, u_num, denom = result
    lower = denom * 1e-4
    upper = denom - lower
    if denom < 0 and (t_num > lower or t_num < upper
                      or u_num > lower or u_num < upper):
        return False
    if denom > 0 and (t_num < lower or t_num > upper
                      or u_num < lower or u_num > upper):
        return False
    return True


def raycast(origin: Vector2, endpoint: Vector2,
            segments: list[tuple[Vector2, Vector2]]):
    """Determines if a ray intersects one or more segments."""
    if origin == endpoint:
        return None

    for point1, point2 in segments:
        if point1 == origin or point2 == origin:
            # Skip over segments where either endpoint is the origin
            continue

        if check_segment_intersection(origin, endpoint, point1, point2):
            return True

    return False


def can_see(point1: Vector2, point2: Vector2,
            segments: list[tuple[Vector2, Vector2]]):
    """Determines if point1 and point2 can see each other."""
    return not raycast(point1, point2, segments)

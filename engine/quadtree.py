from __future__ import annotations
import math
from typing import Callable, Generic, Optional, TypeVar

import pygame

Rect = pygame.Rect
Vector2 = pygame.Vector2

# Object type
Object = TypeVar("Object")

# Function to retrieve a Rect from an object
ObjectToRect = Callable[[Object], Rect]
# Function to retrieve a position from an object
ObjectToPos = Callable[[Object], Vector2]

# Intersection between two objects
Intersection = tuple[Object, Object]

# Predicate for nearest neighbor
Predicate = Callable[[Object], bool]


def get_child_rect(rect: Rect, i: int) -> Rect:
    """
    Given the rect of a node and the index of the child node quadrant, returns
    the rect of the quadrant.

    `i` must be one of `0`, `1`, `2`, or `3`.
    """
    x = rect.left
    y = rect.top
    w = rect.width / 2
    h = rect.height / 2

    if i == 0:
        # Northwest
        return Rect(x, y, w, h)
    elif i == 1:
        # Northeast
        return Rect(x + w, y, w, h)
    elif i == 2:
        # Southwest
        return Rect(x, y + h, w, h)
    elif i == 3:
        # Southeast
        return Rect(x + w, y + h, w, h)
    else:
        assert False, "i must be 0, 1, 2, or 3"


def get_quadrant_from_rect(node_rect: Rect, rect: Rect) -> Optional[int]:
    """
    Given the rect of a node and another rect, returns the index of the child
    node quadrant that the rect is fully contained in. If the rect cannot be
    fully contained in any quadrant rect, then it returns `None`, indicating
    that the rect belongs in this node.
    """
    if rect.right < node_rect.centerx:
        if rect.bottom < node_rect.centery:
            # Northwest
            return 0
        elif rect.top >= node_rect.centery:
            # Southwest
            return 2
    elif rect.left >= node_rect.centerx:
        if rect.bottom < node_rect.centery:
            # Northeast
            return 1
        elif rect.top >= node_rect.centery:
            # Southeast
            return 3

    # Not entirely contained in a quadrant
    return None


def get_quadrant_from_point(node_rect: Rect, point: Vector2) -> int:
    """
    Given the rect of a node and a point, returns the index of the child node
    quadrant that the point is within.
    """
    if point.x < node_rect.centerx:
        if point.y < node_rect.centery:
            # Northwest
            return 0
        else:  # point.y >= node_rect.centery
            # Southwest
            return 2
    else:  # point.x >= node_rect.centerx
        if point.y < node_rect.centery:
            # Northeast
            return 1
        else:  # point.y >= node_rect.centery
            # Southeast
            return 3


def closer(object1: Optional[Object], object2: Optional[Object],
           point: Vector2, get_pos: ObjectToPos[Object]) -> Optional[Object]:
    """
    Given two objects and a point, returns the object closer to the point.
    """
    if object2 is None:
        return object1
    if object1 is None:
        return object2

    point_to_object = (get_pos(object1) - point).magnitude()
    point_to_closest = (get_pos(object2) - point).magnitude()

    if point_to_object < point_to_closest:
        return object1
    else:
        return object2


def distance_to_rect(point: Vector2, rect: Rect) -> float:
    """Finds the shortest distance between a point and a Rect."""
    # Coordinates of Rect border point closest to the provided point
    border_x, border_y = 0, 0

    if point.x < rect.left:
        border_x = rect.left
    elif point.x < rect.right:
        border_x = point.x
    else:  # point.x >= rect.right
        border_x = rect.right

    if point.y < rect.top:
        border_y = rect.top
    elif point.y < rect.bottom:
        border_y = point.y
    else:  # point.y >= rect.bottom
        border_y = rect.bottom

    dx = point.x - border_x
    dy = point.y - border_y
    return (dx * dx + dy * dy) ** 0.5


class Node(Generic[Object]):
    """Node of a Quadtree."""
    def __init__(self):
        self.objects = list[Object]()           # List of objects in this node
        self.children = list[Node[Object]]()    # List of 0 or 4 children nodes
        self.threshold = 8                      # Max size of self.objects

    @property
    def is_leaf(self):
        """A Node is a leaf node if it has no children nodes."""
        return len(self.children) == 0

    @property
    def is_branch(self):
        """A Node is a branch node if it has 4 children nodes."""
        return len(self.children) == 4

    def remove_object(self, object: Object):
        """
        Removes an object from this node. Specialized as a method to
        incorporate a swap-and-pop optimization.
        """
        objects = self.objects

        # The below will throw if the object is not present, so an assert
        # would be extraneous.
        index = objects.index(object)
        objects[index], objects[-1] = objects[-1], objects[index]
        objects.pop()

    def split(self, rect: Rect, get_rect: ObjectToRect[Object]):
        """
        Splits this leaf node into a branch node. Creates 4 child leaf nodes
        and splits this node's objects among them and itself depending on
        quadrant.
        """
        assert self.is_leaf, "Only leaf nodes can split"

        self.children = [Node() for i in range(4)]

        new_self_objects = []
        for object in self.objects:
            i = get_quadrant_from_rect(rect, get_rect(object))
            if i is not None:
                self.children[i].objects.append(object)
            else:
                new_self_objects.append(object)

        self.objects = new_self_objects

    def try_merge(self) -> bool:
        """
        Attempts to merge this branch node into a leaf node. Fails if the total
        number of objects in this node and its children is larger than the
        threshold.

        Returns `True` if succeeded, `False` otherwise.
        """
        assert self.is_branch, "Only branch nodes can merge"

        are_children_leaves = all(child.is_leaf for child in self.children)
        assert are_children_leaves, "Children of this node much be leaf nodes"

        num_children_objects = sum(len(child.objects)
                                   for child in self.children)
        num_objects = len(self.objects) + num_children_objects

        if num_objects > self.threshold:
            return False

        self.objects += (object
                         for child in self.children
                         for object in child.objects)
        self.children = []

        return True


class Quadtree(Generic[Object]):
    """
    Quadtree class which assists with 2D spacial organization. It's like a
    binary tree for two dimensions!
    """
    def __init__(self, rect: Rect, get_rect: ObjectToRect[Object],
                 get_pos: ObjectToPos[Object]):
        self.__root_node = Node[Object]()
        self.__root_rect = rect
        self.__max_depth = 8

        self.__get_rect = get_rect
        self.__get_pos = get_pos

    @staticmethod
    def from_objects(objects: list[Object], get_rect: ObjectToRect[Object],
                     get_pos: ObjectToPos[Object]) -> Quadtree[Object]:
        """Constructs a Quadtree with a list of objects."""
        # Calculate Quadtree bounds
        min_x, min_y = math.inf, math.inf
        max_x, max_y = -math.inf, -math.inf

        for object in objects:
            rect = get_rect(object)
            min_x = min(min_x, rect.left)
            min_y = min(min_y, rect.top)
            max_x = max(max_x, rect.right)
            max_y = max(max_y, rect.bottom)

        quadtree_top_left = Vector2(min_x, min_y)
        quadtree_size = Vector2(max_x - min_x, max_y - min_y)

        # Construct Quadtree
        quadtree = Quadtree(Rect(quadtree_top_left, quadtree_size), get_rect,
                            get_pos)
        for object in objects:
            quadtree.add(object)

        return quadtree

    def __add_leaf(self, node: Node[Object], rect: Rect, object: Object,
                   depth: int):
        """Adds object to a leaf node."""
        if depth >= self.__max_depth or len(node.objects) < node.threshold:
            # Insert object into this leaf node if it has space or is at max
            # depth
            node.objects.append(object)
        else:
            # Otherwise, split the node and try again
            node.split(rect, self.__get_rect)
            self.__add(node, rect, object, depth)

    def __add_branch(self, node: Node[Object], rect: Rect, object: Object,
                     depth: int):
        """Adds object to a branch node."""
        i = get_quadrant_from_rect(rect, self.__get_rect(object))
        if i is not None:
            # Add the object in child node if object is entirely contained in a
            # quadrant
            child_node = node.children[i]
            child_rect = get_child_rect(rect, i)
            self.__add(child_node, child_rect, object, depth + 1)
        else:
            # Add to current node otherwise
            node.objects.append(object)

    def __add(self, node: Node[Object], rect: Rect, object: Object,
              depth: int):
        """Recursive helper function for Quadtree.add."""
        # TODO: Fix the rectangle calculation so that we can un-comment the
        # assert below. The Rect seems to have some rounding that causes it to
        # be a pixel or two short.
        # assert rect.contains(self.__get_rect(object)), ("Object must be "
        #                                                 "within rect")

        if node.is_leaf:
            self.__add_leaf(node, rect, object, depth)
        elif node.is_branch:
            self.__add_branch(node, rect, object, depth)
        else:
            assert False, "Node is neither a leaf nor a branch"

    def add(self, object: Object):
        """Adds an object to this Quadtree."""
        self.__add(self.__root_node, self.__root_rect, object, 0)

    def __remove_leaf(self, node: Node[Object], rect: Rect, object: Object
                      ) -> bool:
        """Removes an object from a leaf node."""
        # Remove object from leaf node
        node.remove_object(object)
        # Inform parent node to try to merge by returning True
        return True

    def __remove_branch(self, node: Node[Object], rect: Rect, object: Object
                        ) -> bool:
        """Removes an object from a branch node."""
        i = get_quadrant_from_rect(rect, self.__get_rect(object))
        if i is not None:
            # Remove object from child node if it's entirely contained in it
            child_node = node.children[i]
            child_rect = get_child_rect(rect, i)
            if self.__remove(child_node, child_rect, object):
                # Try to merge if the child is a leaf node
                return node.try_merge()
        else:
            # Otherwise, remove the object from the current node
            node.remove_object(object)
        return False

    def __remove(self, node: Node[Object], rect: Rect, object: Object) -> bool:
        """
        Recursive helper function for Quadtree.remove.

        Returns `True` if `object` was removed from a leaf node, `False`
        otherwise.
        """
        # TODO: Fix the rectangle calculation so that we can un-comment the
        # assert below. The Rect seems to have some rounding that causes it to
        # be a pixel or two short.
        # assert rect.contains(self.__get_rect(object)), ("Object must be "
        #                                                 "within rect")

        if node.is_leaf:
            return self.__remove_leaf(node, rect, object)
        elif node.is_branch:
            return self.__remove_branch(node, rect, object)
        else:
            assert False, "Node is neither a leaf nor a branch"

    def remove(self, object: Object):
        """Removes an object from this Quadtree."""
        self.__remove(self.__root_node, self.__root_rect, object)

    def __query(self, node: Node[Object], rect: Rect, query_rect: Rect,
                objects: list[Object]):
        """Helper recursive function for Quadtree.query."""
        if not query_rect.colliderect(rect):
            print(query_rect, rect)
        assert query_rect.colliderect(rect)

        # Add objects from this node that collide with the query_rect
        objects += (object
                    for object in node.objects
                    if query_rect.colliderect(self.__get_rect(object)))

        if node.is_leaf:
            return

        # Recurse on children that collide with the query_rect
        for i, child in enumerate(node.children):
            child_rect = get_child_rect(rect, i)
            if query_rect.colliderect(child_rect):
                self.__query(child, child_rect, query_rect, objects)

    def query(self, query_rect: Rect) -> list[Object]:
        """Queries for all object rectangles intersecting a query rectangle."""
        objects = []
        self.__query(self.__root_node, self.__root_rect, query_rect, objects)
        return objects

    def __find_intersections_in_descendants(self, node: Node[Object],
                                            object: Object,
                                            intersections:
                                            list[Intersection[Object]]):
        """
        Finds all intersections between an object and all objects in the
        provided node and its descendants.
        """
        object_rect = self.__get_rect(object)

        # Add the intersections between the object and this node's objects
        intersections += ((object, other)
                          for other in node.objects
                          if object_rect.colliderect(self.__get_rect(other)))

        if node.is_leaf:
            return

        # Recurse
        for child in node.children:
            self.__find_intersections_in_descendants(child, object,
                                                     intersections)

    def __find_all_intersections(self, node: Node[Object],
                                 intersections: list[Intersection[Object]]):
        """Recursive helper function for Quadtree.find_all_intersections."""
        intersections += (
            (node.objects[i], node.objects[j])
            for i in range(len(node.objects) - 1)
            for j in range(i + 1, len(node.objects))
            if (self.__get_rect(node.objects[i])
                .colliderect(self.__get_rect(node.objects[j])))
        )

        if node.is_leaf:
            return

        for child in node.children:
            for object in node.objects:
                self.__find_intersections_in_descendants(child, object,
                                                         intersections)

        for child in node.children:
            self.__find_all_intersections(child, intersections)

    def find_all_intersections(self) -> list[Intersection[Object]]:
        """Finds all pairs of rectangle intersections between two objects."""
        intersections = []
        self.__find_all_intersections(self.__root_node, intersections)
        return intersections

    def __nearest_neighbor(self, node: Node[Object], rect: Rect,
                           point: Vector2, predicate: Predicate[Object]
                           ) -> Optional[Object]:
        """Recursive helper function for Quadtree.nearest_neighbor."""
        closest: Optional[Object] = None

        if node.is_branch:
            # Get children rects
            children = [(i, get_child_rect(rect, i)) for i in range(4)]

            # Sort by distance to point
            children = sorted(children,
                              key=lambda t: distance_to_rect(point, t[1]))

            # Check objects in children
            for i, child_rect in children:
                if closest is not None:
                    # Prune child rects that are farther away than closest
                    point_to_rect = distance_to_rect(point, child_rect)
                    point_to_closest = (self.__get_pos(closest)
                                        - point).magnitude()
                    if point_to_rect >= point_to_closest:
                        # We break here since remaining child rects are farther
                        break
                child_node = node.children[i]
                sub_closest = self.__nearest_neighbor(child_node,
                                                      child_rect, point,
                                                      predicate)
                closest = closer(closest, sub_closest, point, self.__get_pos)

        # Check objects in node
        for object in node.objects:
            if not predicate(object):
                continue
            closest = closer(closest, object, point, self.__get_pos)

        return closest

    def nearest_neighbor(self, point: Vector2, predicate: Predicate[Object]
                         ) -> Optional[Object]:
        """Finds the nearest object to a point that satisfies a predicate."""
        return self.__nearest_neighbor(self.__root_node, self.__root_rect,
                                       point, predicate)

    def __render(self, screen: pygame.Surface, node: Node[Object], rect: Rect):
        """Recursive helper function for Quadtree.render."""
        pygame.draw.circle(screen, "#0000FF", Vector2(rect.center), 8)

        for object in node.objects:
            pygame.draw.line(screen, "#0000FF", Vector2(rect.center),
                             self.__get_pos(object))

            object_rect = self.__get_rect(object)
            pygame.draw.lines(
                screen, "#0000FF", True,
                [
                    Vector2(object_rect.topleft),
                    Vector2(object_rect.topright),
                    Vector2(object_rect.bottomright),
                    Vector2(object_rect.bottomleft),
                ]
            )

        for i, child in enumerate(node.children):
            child_rect = get_child_rect(rect, i)
            self.__render(screen, child, child_rect)

            pygame.draw.line(screen, "#0000FF", Vector2(rect.center),
                             Vector2(child_rect.center))

    def render(self, screen: pygame.Surface):
        """Render the quadtree onto a surface."""
        self.__render(screen, self.__root_node, self.__root_rect)

from __future__ import annotations
from typing import Final, Optional

import pygame

from engine.entity import Entity

Rect = pygame.Rect
Vector2 = pygame.Vector2

Intersection = tuple[Entity, Entity]


def get_child_rect(rect: Rect, i: int) -> Rect:
    """
    Given the rect of a node and the index of the child node quadrant, returns
    the rect of the quadrant.

    `i` must be one of `0`, `1`, `2`, or `3`.
    """
    child_size = Vector2(rect.size) / 2
    top_left = Vector2(rect.topleft)

    if i == 0:
        # Northwest
        return Rect(top_left, child_size)
    elif i == 1:
        # Northeast
        return Rect(top_left + Vector2(child_size.x, 0), child_size)
    elif i == 2:
        # Southwest
        return Rect(top_left + Vector2(0, child_size.y), child_size)
    elif i == 3:
        # Southeast
        return Rect(top_left + child_size, child_size)
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


def closer(entity1: Optional[Entity], entity2: Optional[Entity], point: Vector2
           ) -> Optional[Entity]:
    """
    Given two entities and a point, returns the entity closer to the point.
    """
    if entity2 is None:
        return entity1
    if entity1 is None:
        return entity2

    point_to_entity = (entity1.position - point).magnitude()
    point_to_closest = (entity2.position - point).magnitude()

    if point_to_entity < point_to_closest:
        return entity1
    else:
        return entity2


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


class Node:
    """Node of a Quadtree."""
    def __init__(self):
        self.entities: list[Entity] = []    # List of entities under this node
        self.children: list[Node] = []      # List of 0 or 4 children nodes
        self.threshold: Final[int] = 8      # Max size of self.entities

    @property
    def is_leaf(self):
        """A Node is a leaf node if it has no children nodes."""
        return len(self.children) == 0

    @property
    def is_branch(self):
        """A Node is a branch node if it has 4 children nodes."""
        return len(self.children) == 4

    def remove_entity(self, entity: Entity):
        """
        Removes an entity from this node. Specialized as a method to
        incorporate a swap-and-pop optimization.
        """
        entities = self.entities

        # The below will throw if the entity is not present, so an assert
        # would be extraneous.
        index = entities.index(entity)
        entities[index], entities[-1] = entities[-1], entities[index]
        entities.pop()

    def split(self, rect: Rect):
        """
        Splits this leaf node into a branch node. Creates 4 child leaf nodes
        and splits this node's entities among them and itself depending on
        quadrant.
        """
        assert self.is_leaf, "Only leaf nodes can split"

        self.children = [Node() for i in range(4)]

        new_self_entities = []
        for entity in self.entities:
            i = get_quadrant_from_rect(rect, entity.rect)
            if i is not None:
                self.children[i].entities.append(entity)
            else:
                new_self_entities.append(entity)

        self.entities = new_self_entities

    def try_merge(self) -> bool:
        """
        Attempts to merge this branch node into a leaf node. Fails if the total
        number of entities in this node and its children is larger than the
        threshold.

        Returns `True` if succeeded, `False` otherwise.
        """
        assert self.is_branch, "Only branch nodes can merge"

        are_children_leaves = all(child.is_leaf for child in self.children)
        assert are_children_leaves, "Children of this node much be leaf nodes"

        num_children_entities = sum(len(child.entities)
                                    for child in self.children)
        num_entities = len(self.entities) + num_children_entities

        if num_entities > self.threshold:
            return False

        self.entities += (entity
                          for child in self.children
                          for entity in child.entities)
        self.children = []

        return True


class Quadtree:
    """
    Quadtree class which assists with 2D spacial organization. It's like a
    binary tree for two dimensions!
    """
    def __init__(self, rect: Rect):
        self.__root_node: Node = Node()
        self.__root_rect = rect
        self.__max_depth = 8

    def __add_leaf(self, node: Node, rect: Rect, entity: Entity, depth: int):
        """Adds entity to a leaf node."""
        if depth >= self.__max_depth or len(node.entities) < node.threshold:
            # Insert entity into this leaf node if it has space or is at max
            # depth
            node.entities.append(entity)
        else:
            # Otherwise, split the node and try again
            node.split(rect)
            self.__add(node, rect, entity, depth)

    def __add_branch(self, node: Node, rect: Rect, entity: Entity, depth: int):
        """Adds entity to a branch node."""
        i = get_quadrant_from_rect(rect, entity.rect)
        if i is not None:
            # Add the entity in child node if entity is entirely contained in a
            # quadrant
            child_node = node.children[i]
            child_rect = get_child_rect(rect, i)
            self.__add(child_node, child_rect, entity, depth + 1)
        else:
            # Add to current node otherwise
            node.entities.append(entity)

    def __add(self, node: Node, rect: Rect, entity: Entity, depth: int):
        """Recursive helper function for Quadtree.add."""
        # TODO: Fix the rectangle calculation so that we can un-comment the
        # assert below. The Rect seems to have some rounding that causes it to
        # be a pixel or two short.
        # assert rect.contains(entity.rect), "Entity must be within rect"

        if node.is_leaf:
            self.__add_leaf(node, rect, entity, depth)
        elif node.is_branch:
            self.__add_branch(node, rect, entity, depth)
        else:
            assert False, "Node is neither a leaf nor a branch"

    def add(self, entity: Entity):
        """Adds an entity to this Quadtree."""
        self.__add(self.__root_node, self.__root_rect, entity, 0)

    def __remove_leaf(self, node: Node, rect: Rect, entity: Entity) -> bool:
        """Removes an entity from a leaf node."""
        # Remove entity from leaf node
        node.remove_entity(entity)
        # Inform parent node to try to merge by returning True
        return True

    def __remove_branch(self, node: Node, rect: Rect, entity: Entity) -> bool:
        """Removes an entity from a branch node."""
        i = get_quadrant_from_rect(rect, entity.rect)
        if i is not None:
            # Remove entity from child node if it's entirely contained in it
            child_node = node.children[i]
            child_rect = get_child_rect(rect, i)
            if self.__remove(child_node, child_rect, entity):
                # Try to merge if the child is a leaf node
                return node.try_merge()
        else:
            # Otherwise, remove the entity from the current node
            node.remove_entity(entity)
        return False

    def __remove(self, node: Node, rect: Rect, entity: Entity) -> bool:
        """
        Recursive helper function for Quadtree.remove.

        Returns `True` if `entity` was removed from a leaf node, `False`
        otherwise.
        """
        # TODO: Fix the rectangle calculation so that we can un-comment the
        # assert below. The Rect seems to have some rounding that causes it to
        # be a pixel or two short.
        # assert rect.contains(entity.rect), "Entity must be within rect"

        if node.is_leaf:
            return self.__remove_leaf(node, rect, entity)
        elif node.is_branch:
            return self.__remove_branch(node, rect, entity)
        else:
            assert False, "Node is neither a leaf nor a branch"

    def remove(self, entity: Entity):
        """Removes an entity from this Quadtree."""
        self.__remove(self.__root_node, self.__root_rect, entity)

    def __query(self, node: Node, rect: Rect, query_rect: Rect,
                entities: list[Entity]):
        """Helper recursive function for Quadtree.query."""
        assert query_rect.colliderect(rect)

        # Add entities from this node that collide with the query_rect
        entities += (entity
                     for entity in node.entities
                     if query_rect.colliderect(entity.rect))

        if node.is_leaf:
            return

        # Recurse on children that collide with the query_rect
        for i, child in enumerate(node.children):
            child_rect = get_child_rect(rect, i)
            if query_rect.colliderect(child_rect):
                self.__query(child, child_rect, query_rect, entities)

    def query(self, query_rect: Rect) -> list[Entity]:
        """Queries for all entity rectangles intersecting a query rectangle."""
        entities = []
        self.__query(self.__root_node, self.__root_rect, query_rect, entities)
        return entities

    def __find_intersections_in_descendants(self, node: Node, entity: Entity,
                                            intersections: list[Intersection]):
        """
        Finds all intersections between an entity and all entities in the
        provided node and its descendants.
        """
        entity_rect = entity.rect

        # Add the intersections between the entity and this node's entities
        intersections += ((entity, other)
                          for other in node.entities
                          if entity_rect.colliderect(other.rect))

        if node.is_leaf:
            return

        # Recurse
        for child in node.children:
            self.__find_intersections_in_descendants(child, entity,
                                                     intersections)

    def __find_all_intersections(self, node: Node,
                                 intersections: list[Intersection]):
        """Recursive helper function for Quadtree.find_all_intersections."""
        intersections += (
            (node.entities[i], node.entities[j])
            for i in range(len(node.entities) - 1)
            for j in range(i + 1, len(node.entities))
            if node.entities[i].rect.colliderect(node.entities[j].rect)
        )

        if node.is_leaf:
            return

        for child in node.children:
            for entity in node.entities:
                self.__find_intersections_in_descendants(child, entity,
                                                         intersections)

        for child in node.children:
            self.__find_all_intersections(child, intersections)

    def find_all_intersections(self) -> list[Intersection]:
        """Finds all pairs of rectangle intersections between two entities."""
        intersections = []
        self.__find_all_intersections(self.__root_node, intersections)
        return intersections

    def __render(self, screen: pygame.Surface, node: Node, rect: Rect):
        """Recursive helper function for Quadtree.render."""
        pygame.draw.circle(screen, "#0000FF", Vector2(rect.center), 8)

        for entity in node.entities:
            pygame.draw.line(screen, "#0000FF", Vector2(rect.center),
                             Vector2(entity.position))

            entity_rect = entity.rect
            pygame.draw.lines(
                screen, "#0000FF", True,
                [
                    Vector2(entity_rect.topleft),
                    Vector2(entity_rect.topright),
                    Vector2(entity_rect.bottomright),
                    Vector2(entity_rect.bottomleft),
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

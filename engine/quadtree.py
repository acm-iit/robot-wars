import pygame
from typing import Final, Optional

from engine.entity import Entity

Rect = pygame.Rect
Vector2 = pygame.Vector2

def get_child_rect(rect: Rect, i: int) -> Rect:
    """
    Given the rect of a node and the index of the child node quadrant,
    returns the rect of the quadrant.

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

def get_quadrant(node_rect: Rect, entity_rect: Rect) -> Optional[int]:
    """
    Given the rect of a node and the rect of an entity, returns the index
    of the child node quadrant that the entity is fully contained in. If the
    entity cannot be fully contained in any quadrant rect, then it returns
    `None`, indicating that the entity belongs in this node.
    """
    if entity_rect.right < node_rect.centerx:
        if entity_rect.bottom < node_rect.centery:
            # Northwest
            return 0
        elif entity_rect.top >= node_rect.centery:
            # Southwest
            return 2
    elif entity_rect.left >= node_rect.centerx:
        if entity_rect.bottom < node_rect.centery:
            # Northeast
            return 1
        elif entity_rect.top >= node_rect.centery:
            # Southeast
            return 3

    # Not entirely contained in a quadrant
    return None

class Node:
    """
    Node of a Quadtree.
    """
    def __init__(self):
        self.entities: list[Entity] = []        # list of entities under this node
        self.children: list["Node"] = []        # list of 0 or 4 children nodes
        self.threshold: Final[int] = 8          # Maximum amount of entities this node can contain (unless it's at max depth)

    @property
    def is_leaf(self):
        """
        A Node is a leaf node if it has no children nodes.
        """
        return len(self.children) == 0

    @property
    def is_branch(self):
        """
        A Node is a branch node if it has 4 children nodes.
        """
        return len(self.children) == 4

    def remove_entity(self, entity: Entity):
        """
        Removes an entity from this node. Specialized as a method to incorporate a swap-and-pop optimization.
        """
        # The below will throw if the entity is not present, so an assert would be extraneous.
        index = self.entities.index(entity)
        self.entities[index], self.entities[-1] = self.entities[-1], self.entities[index]
        self.entities.pop()

    def split(self, rect: Rect):
        """
        Splits this leaf node into a branch node.
        Creates 4 child leaf nodes and splits this node's entities among them and itself depending on quadrant.
        """
        assert self.is_leaf, "Only leaf nodes can split"

        self.children = [Node() for i in range(4)]

        new_self_entities = []
        for entity in self.entities:
            i = get_quadrant(rect, entity.rect)
            if i is not None:
                self.children[i].entities.append(entity)
            else:
                new_self_entities.append(entity)

        self.entities = new_self_entities

    def try_merge(self) -> bool:
        """
        Attempts to merge this branch node into a leaf node.
        Fails if the total number of entities in this node and its children is larger than the threshold.
        
        Returns `True` if succeeded, `False` otherwise.
        """
        assert self.is_branch, "Only branch nodes can merge"
        assert all(child.is_leaf for child in self.children), "Children of this node much be leaf nodes"

        num_entities = len(self.entities) + sum(len(child.entities) for child in self.children)

        if num_entities > self.threshold:
            return False

        self.entities += (entity for child in self.children for entity in child.entities)
        self.children = []

        return True

class Quadtree:
    """
    Quadtree class which assists with 2D spacial organization.
    It's like a binary tree for two dimensions!
    """
    def __init__(self, rect: Rect):
        self.__root_node: Node = Node()
        self.__root_rect = rect
        self.__max_depth = 8

    def __add(self, node: Node, rect: Rect, entity: Entity, depth: int):
        """
        Recursive helper function for Quadtree.add.
        """
        entity_rect = entity.rect
        # TODO: Fix the rectangle calculation so that we can un-comment the assert below.
        # The Rect seems to have some rounding that causes it to be a pixel or two short.
        # assert rect.contains(entity_rect), f"Entity must be within rect; {rect}; {entity_rect}"

        if node.is_leaf:
            if depth >= self.__max_depth or len(node.entities) < node.threshold:
                # Insert entity into this leaf node if it has space or is at max depth
                node.entities.append(entity)
            else:
                # Otherwise, split the node and try again
                node.split(rect)
                self.__add(node, rect, entity, depth)
        elif node.is_branch:
            i = get_quadrant(rect, entity_rect)
            if i is not None:
                # Add the entity in child node if entity is entirely contained in a quadrant
                self.__add(node.children[i], get_child_rect(rect, i), entity, depth + 1)
            else:
                # Add to current node otherwise
                node.entities.append(entity)
        else:
            assert False, "Node is neither a leaf nor a branch"

    def add(self, entity: Entity):
        """
        Adds an entity to this Quadtree.
        """
        self.__add(self.__root_node, self.__root_rect, entity, 0)

    def __remove(self, node: Node, rect: Rect, entity: Entity) -> bool:
        """
        Recursive helper function for Quadtree.remove.

        Returns `True` if `entity` was removed from a leaf node, `False` otherwise.
        """
        entity_rect = entity.rect
        assert rect.contains(entity_rect), "Entity must be within rect"

        if node.is_leaf:
            # Remove entity from leaf node
            node.remove_entity(entity)
            # Inform parent node to try to merge by returning True
            return True
        elif node.is_branch:
            i = get_quadrant(rect, entity_rect)
            if i is not None:
                # Remove entity from child node if it's entirely contained in it
                if self.__remove(node.children[i], get_child_rect(rect, i), entity):
                    # Try to merge if the child is a leaf node
                    return node.try_merge()
            else:
                # Otherwise, remove the entity from the current node
                node.remove_entity(entity)
            return False
        else:
            assert False, "Node is neither a leaf nor a branch"

    def remove(self, entity: Entity):
        """
        Removes an entity from this Quadtree.
        """
        self.__remove(self.__root_node, self.__root_rect, entity)

    def __query(self, node: Node, rect: Rect, query_rect: Rect, entities: list[Entity]):
        """
        Helper recursive function for Quadtree.query.
        """
        assert query_rect.colliderect(rect)

        # Add entities from this node that collide with the query_rect
        entities += (entity for entity in node.entities if query_rect.colliderect(entity.rect))

        if node.is_leaf:
            return

        # Recurse on children that collide with the query_rect
        for i, child in enumerate(node.children):
            child_rect = get_child_rect(rect, i)
            if query_rect.colliderect(child_rect):
                self.__query(child, child_rect, query_rect, entities)

    def query(self, query_rect: Rect) -> list[Entity]:
        """
        Queries for all entity rectangles intersecting a query rectangle.
        """
        entities = []
        self.__query(self.__root_node, self.__root_rect, query_rect, entities)
        return entities

    def __find_intersections_in_descendants(self, node: Node, entity: Entity, intersections: list[tuple[Entity, Entity]]):
        """
        Finds all intersections between an entity and all entities in the provided node and its descendants.
        """
        entity_rect = entity.rect

        # Add the intersections between the entity and this node's entities
        intersections += ((entity, other) for other in node.entities if entity_rect.colliderect(other.rect))

        if node.is_leaf:
            return

        # Recurse 
        for child in node.children:
            self.__find_intersections_in_descendants(child, entity, intersections)

    def __find_all_intersections(self, node: Node, intersections: list[tuple[Entity, Entity]]):
        """
        Recursive helper function for Quadtree.find_all_intersections.
        """
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
                self.__find_intersections_in_descendants(child, entity, intersections)

        for child in node.children:
            self.__find_all_intersections(child, intersections)

    def find_all_intersections(self) -> list[tuple[Entity, Entity]]:
        """
        Finds all pairs of rectangle intersections between two entities.
        """
        intersections = []
        self.__find_all_intersections(self.__root_node, intersections)
        return intersections

    def __render(self, screen: pygame.Surface, node: Node, rect: Rect):
        """
        Recursive helper function for Quadtree.render.
        """
        pygame.draw.circle(screen, "#0000FF", Vector2(rect.center), 8)

        for entity in node.entities:
            pygame.draw.line(screen, "#0000FF", Vector2(rect.center), Vector2(entity.position))

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

            pygame.draw.line(screen, "#0000FF", Vector2(rect.center), Vector2(child_rect.center))

    def render(self, screen: pygame.Surface):
        """
        Render the quadtree onto a surface.
        """
        self.__render(screen, self.__root_node, self.__root_rect)

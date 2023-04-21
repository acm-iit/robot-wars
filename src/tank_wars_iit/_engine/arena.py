from __future__ import annotations
from importlib.resources import files
import json
import math
from random import choice, random, sample
import traceback
from typing import cast, Optional

import pygame

from tank_wars_iit._engine.control import Controller
from tank_wars_iit._engine.entity import Bullet, Coin, Entity, Robot, Wall
from tank_wars_iit._engine.entity.bullet import BULLET_SPEED
from tank_wars_iit._engine.entity.coin import COIN_RADIUS
from tank_wars_iit._engine.entity.robot import ROBOT_HITBOX_WIDTH
from tank_wars_iit._engine.map import is_map
from tank_wars_iit._engine.pathfinding import PathfindingGraph
from tank_wars_iit._engine.quadtree import Quadtree
from tank_wars_iit._engine.robotlist import (RobotList,
                                             WIDTH as ROBOT_LIST_WIDTH,
                                             COLOR as ROBOT_LIST_COLOR)
from tank_wars_iit._engine.util import can_see_walls

Rect = pygame.Rect
Vector2 = pygame.Vector2

WALL_THICKNESS = 100
FRAME_RATE = 60
MAX_VIEWPORT_WIDTH = 896
MAX_VIEWPORT_HEIGHT = 896
GRASS_COLOR = "#006600"

BULLET_COLLIDE_RADIUS = 16          # Radius for collisions w/ other bullets
BULLET_COLLIDE_EFFECT_RADIUS = 24   # Radius for collision boom effect
BULLET_COLLIDE_EFFECT_COLOR = "#FC9803"
BULLET_COLLIDE_EFFECT_TIME = 0.3


class Arena:
    """
    Class representing a round of Robot Wars.

    Contains and simulates Entities and provides rendering support.
    """
    def __init__(self, size: Vector2):
        self.__entities: list[Entity] = []
        self.__original_size = size     # Unmodified size of the Arena
        self.__size = size
        self.origin = Vector2()         # Top-left corner of Arena space
        self.__surface = pygame.Surface(size)
        self.__quadtree: Optional[Quadtree[Entity]] = None
        self.__wall_quadtree: Optional[Quadtree[Wall]] = None
        self.__path_graph: Optional[PathfindingGraph] = None
        self.__paths = list[list[Vector2]]()
        self.__available_nodes: list[Vector2] = []
        self.__coin: Coin = Coin(Vector2())  # Dummy dead coin
        self.__robots = list[tuple[Robot, Controller]]()
        self.__bullet_collisions = list[tuple[Vector2, float]]()

        self.spawns: list[Vector2] = []
        self.total_sim_time = 0         # Total simulation time (not elapsed)
        self.shrink_rate = 0            # Rate at which Arena shrinks (0 = no)
        self.shrink_zoom = True         # Determines if the camera shrinks

        # Whether to use pathfinding over direct paths
        self.use_pathfinding = True

        # Debug settings
        self.show_hitboxes = False
        self.show_mouse_coordinates = False
        self.show_fps = False
        self.show_quadtree = False
        self.show_nearest_robot = False
        self.show_pathfinding_hitbox = False
        self.show_path_graph = False
        self.show_paths = False
        self.show_robot_nodes = False

        # Add surrounding walls
        self.boundary_walls = list[Wall]()
        self.set_boundary_walls()

    @property
    def entities(self) -> list[Entity]:
        """Read-only property that provides list of arena entities."""
        return self.__entities.copy()

    @property
    def surface(self) -> pygame.Surface:
        """
        Read-only property that provides reference to drawn arena surface.
        """
        return self.__surface

    @property
    def coin(self) -> Vector2:
        """Read-only property that provides the position of the Coin."""
        return self.__coin.position

    @property
    def size(self) -> Vector2:
        """Read-only property that provides the size of the Arena."""
        return self.__size.copy()

    @property
    def viewport_size(self) -> Vector2:
        """
        Read-only property that provides the size of the viewport surface.
        """
        viewport_rect = Rect(0, 0, MAX_VIEWPORT_WIDTH, MAX_VIEWPORT_HEIGHT)
        arena_rect = Rect(Vector2(), self.__original_size)
        return Vector2(arena_rect.fit(viewport_rect).size)

    @property
    def window_size(self) -> Vector2:
        """
        Read only property that provides the size of the window surface.
        """
        return self.viewport_size + Vector2(ROBOT_LIST_WIDTH, 0)

    @staticmethod
    def from_map_json(filename: str) -> Optional[Arena]:
        """Constructs an Arena from a map config JSON file."""
        path = files("tank_wars_iit._engine.maps").joinpath(filename)
        with path.open("r") as file:
            arena_data = json.load(file)
            assert is_map(arena_data), "Map JSON is malformed"

            arena_size = Vector2(arena_data["size"]["width"],
                                 arena_data["size"]["height"])
            arena = Arena(arena_size)

            for wall_data in arena_data["walls"]:
                wall_position = Vector2(wall_data["position"]["x"],
                                        wall_data["position"]["y"])
                wall_size = Vector2(wall_data["size"]["width"],
                                    wall_data["size"]["height"])
                wall = Wall(wall_position, wall_size,
                            math.radians(wall_data["rotation"]))
                arena.add_entity(wall)

            arena.spawns = [Vector2(spawn_data["x"], spawn_data["y"])
                            for spawn_data in arena_data["spawns"]]

            # Calculate pathfinding graph
            arena.prepare_path_graph()

            return arena

    def set_boundary_walls(self):
        """Adds Walls that surround the Arena."""
        for wall in self.boundary_walls:
            wall.destroy()

        origin = self.origin
        size = self.__size
        thick = WALL_THICKNESS

        north_wall = Wall(origin + Vector2(size.x / 2, -thick / 2 - 1),
                          Vector2(size.x + 2 * thick, thick))
        south_wall = Wall(origin + Vector2(size.x / 2, size.y + thick / 2 + 1),
                          Vector2(size.x + 2 * thick, thick))
        west_wall = Wall(origin + Vector2(-thick / 2 - 1, size.y / 2),
                         Vector2(thick, size.y + 2 * thick))
        east_wall = Wall(origin + Vector2(size.x + thick / 2 + 1, size.y / 2),
                         Vector2(thick, size.y + 2 * thick))

        self.add_entity(north_wall)
        self.add_entity(south_wall)
        self.add_entity(west_wall)
        self.add_entity(east_wall)

        self.boundary_walls = [north_wall, south_wall, west_wall, east_wall]

    def add_entity(self, entity: Entity):
        """
        Adds an entity to this Arena. Entity must not already be in the Arena.
        """
        assert entity not in self.__entities, "Entity already in Arena"

        entity.arena = self
        self.__entities.append(entity)

    def remove_entity(self, entity: Entity):
        """Removes an entity from this Arena. Entity must be in the Arena."""
        assert entity in self.__entities, "Entity not in Arena"

        self.__entities.remove(entity)
        entity.arena = None

    def add_robot(self, controller: Controller):
        robot = Robot(controller.name)
        robot.color = controller.body_color
        robot.head_color = controller.head_color
        self.__robots.append((robot, controller))
        self.add_entity(robot)

    def spawn_robots_old(self, robots: list[Robot]):
        """
        Spawns a list of robots into unique spawn locations. The number of
        robots must be lower than the number of arena spawns.
        """
        assert len(robots) <= len(self.spawns), "# of entities > # of spawns"

        positions: list[Vector2] = sample(self.spawns, k=len(robots))

        for robot in robots:
            self.add_entity(robot)
            robot.position = positions.pop()

    def spawn_robots(self) -> list[Robot]:
        """
        Spawns the Arena's robots into unique spawn locations. The number of
        robots must be lower than the number of arena spawns.
        """
        robots = self.__robots
        assert len(robots) <= len(self.spawns), "# of entities > # of spawns"

        positions: list[Vector2] = sample(self.spawns, k=len(robots))

        for robot, _ in robots:
            robot.position = positions.pop()

        return [robot for robot, _ in robots]

    def get_entities_of_type(self, typeVal: type) -> list[Entity]:
        """Returns a filtered list of entities of a certain class."""
        return [entity
                for entity in self.__entities
                if type(entity) is typeVal]

    def nearest_robot(self, robot: Robot) -> Optional[Robot]:
        """
        Returns the position and rotation of the Robot closest to another
        Robot.
        """
        # Robot.on_update may call this, and the quadtree won't exist on the
        # first update, so just return None
        if self.__quadtree is None:
            return None

        neighbor = self.__quadtree.nearest_neighbor(
            robot.position,
            lambda e: type(e) is Robot and e is not robot
        )
        assert neighbor is None or type(neighbor) is Robot, "Shouldn't happen"

        return neighbor if neighbor is not None else None

    def nearby_bullets(self, robot: Robot) -> list[tuple[Vector2, Vector2]]:
        """
        Returns the positions and velocities of enemy Bullets within a radius
        of a Robot.
        """
        if self.__quadtree is None:
            return []

        query_rect = Rect(robot.position - Vector2(256), Vector2(512))

        entities = self.__quadtree.query(query_rect)
        result = list[tuple[Vector2, Vector2]]()

        for entity in entities:
            if type(entity) is not Bullet or entity.origin == robot:
                continue
            if (entity.position - robot.position).magnitude() > 256:
                continue
            velocity = Vector2(BULLET_SPEED, 0).rotate_rad(entity.rotation)
            result.append((entity.position, velocity))

        return result

    def can_see(self, robot: Robot, point: Vector2) -> bool:
        """Determines if a Robot has line of sight with a point."""
        if self.__wall_quadtree is None:
            return False
        return can_see_walls(robot.position, point, self.__wall_quadtree,
                             use_pathfinding_hitbox=False)

    def prepare_path_graph(self):
        """
        Prepares the PathfindingGraph for this Arena, based on the Walls it
        currently haves.
        """
        self.__path_graph = PathfindingGraph(self)
        self.__available_nodes = self.__path_graph.get_available_nodes()

    def pathfind(self, robot: Robot, point: Vector2
                 ) -> Optional[list[Vector2]]:
        """
        Finds a path between the robot and a provided point, if there is one.
        """
        # Early exit if not using pathfinding
        if not self.use_pathfinding:
            return [point]

        assert self.__path_graph is not None, "Path graph should exist"
        path = self.__path_graph.pathfind(robot.position, robot.rotation,
                                          point)

        if path is None:
            return None

        if self.show_paths:
            self.__paths.append(path)

        # Prune nodes that are close to the Robot
        i = 0
        while i < len(path):
            if (path[i] - robot.position).magnitude() > 1:
                break
            i += 1
        else:
            return None

        return path[i:]

    def window_to_arena(self, point: Vector2) -> Vector2:
        """
        Converts a point on the window surface to a point on the arena surface.
        """
        # Subtract width of robot list panel
        point -= Vector2(ROBOT_LIST_WIDTH, 0)

        # Handle case w/o shrink or zoom
        if self.shrink_rate <= 0 or not self.shrink_zoom:
            ratio = self.__original_size.x / self.viewport_size.x
            return point * ratio

        ratio = self.__size.x / self.viewport_size.x
        offset = point * ratio

        diff = self.__original_size - self.__size
        return diff / 2 + offset

    def __update_shrinking(self):
        """Handles the shrinking of the Arena over time."""
        if self.shrink_rate <= 0:
            return

        og_size = self.__original_size
        shrink = self.total_sim_time * self.shrink_rate
        shrink = min(shrink, min(og_size.x, og_size.y) / 2 - 256)

        self.origin = Vector2(shrink)
        self.__size = self.__original_size - Vector2(2 * shrink)
        self.set_boundary_walls()

    def __update_coin(self):
        """Ensure there's a Coin on screen for Robots to attain."""
        if self.__coin.arena is not None:
            # Make sure the coin is in the shrunk area
            shrunk = Rect(self.origin, self.__size)
            if shrunk.contains(self.__coin.rect):
                return
            else:
                self.__coin.destroy()

        coin = Coin(Vector2())

        if len(self.__available_nodes) == 0:
            # If the Arena has no interior Walls, then spawn in a random
            # location.
            offset = ROBOT_HITBOX_WIDTH / 2 + COIN_RADIUS
            interior_size = self.__size - Vector2(offset * 2, offset * 2)
            x = offset + random() * interior_size.x
            y = offset + random() * interior_size.y
            coin.position = self.origin + Vector2(x, y)
        else:
            coin.position = choice(self.__available_nodes)

        self.add_entity(coin)
        self.__coin = coin

    def __update_robots(self, dt: float):
        for robot, controller in self.__robots:
            if robot.arena is None:
                continue
            try:
                state = robot.compute_state(dt)
                action = controller.act(state)
                robot.perform_action(action, dt)
            except Exception:
                print(f"[ERROR ({robot.name})]: Error occurred during robot "
                      "execution; see below traceback")
                print(traceback.format_exc())

    def __update_entities(self, dt: float):
        for entity in self.__entities:
            entity.update(dt)

    def __filter_entities(self):
        """
        Filter out any entities that were destroyed during updating.

        An entity can be destroyed in various ways:

        * It destroyed itself (i.e. bullet reaches max distance)
        * It was destroyed by another entity (i.e. robot destroyed by bullet)

        An entity is destroyed if its `arena` field is set to `None`.
        """
        self.__entities[:] = [entity
                              for entity in self.__entities
                              if entity.arena is self]

    def __solve_collisions(self):
        """Solves collisions between entities."""
        assert self.__quadtree is not None, "Quadtree should exist"
        for entity1, entity2 in self.__quadtree.find_all_intersections():
            entity1.handle_collision(entity2)

    def __update_bullets(self, dt: float):
        """Handles bullet collision negation."""
        assert self.__quadtree is not None, "Quadtree should exist"

        self.__bullet_collisions[:] = [(p, t - dt)
                                       for p, t in self.__bullet_collisions]
        self.__bullet_collisions[:] = [(p, t)
                                       for p, t in self.__bullet_collisions
                                       if t > 0]

        bullets = self.get_entities_of_type(Bullet)

        for bullet in bullets:
            assert type(bullet) is Bullet, "Shouldn't happen"
            if bullet.arena is None:
                continue

            query_rect = Rect(
                bullet.position - Vector2(BULLET_COLLIDE_RADIUS),
                Vector2(BULLET_COLLIDE_RADIUS * 2)
            )
            entities = self.__quadtree.query(query_rect)

            collided = 1
            position_sum = bullet.position

            for entity in entities:
                if type(entity) is not Bullet:
                    continue

                if entity.origin == bullet.origin:
                    continue

                dist = (entity.position - bullet.position).magnitude()
                if dist > BULLET_COLLIDE_RADIUS:
                    continue

                entity.destroy()

                collided += 1
                position_sum += entity.position

            if collided > 1:
                collision_point = position_sum / collided
                self.__bullet_collisions.append((collision_point,
                                                 BULLET_COLLIDE_EFFECT_TIME))
                bullet.destroy()

    def __clear_offscreen_entities(self):
        """Removes all entities not within the playable area."""
        rect = Rect(self.origin, self.__size)
        for entity in self.__entities:
            if entity.is_static:
                continue
            if not rect.colliderect(entity.rect):
                entity.destroy()

    def __construct_quadtree(self):
        """Constructs a Quadtree with the entities in the arena."""
        self.__quadtree = Quadtree.from_objects(self.__entities,
                                                lambda e: e.rect,
                                                lambda e: e.position)

        walls = cast(list[Wall], self.get_entities_of_type(Wall))
        self.__wall_quadtree = Quadtree.from_objects(walls, lambda w: w.rect,
                                                     lambda w: w.position)

    def __render_scene(self):
        """Renders the Arena onto self.__surface."""
        # Clear screen with grass color
        self.__surface.fill(GRASS_COLOR)

        # Draw updated entities onto the surface
        for entity in self.__entities:
            entity.render(self.__surface)
        for entity in self.__entities:
            entity.post_render(self.__surface)

        # Draw bullet collisions
        for point, time in self.__bullet_collisions:
            alpha = (time / BULLET_COLLIDE_EFFECT_TIME) ** 2
            size = BULLET_COLLIDE_EFFECT_RADIUS * 2 * (1 + (1 - alpha) * 0.5)
            color = pygame.Color(BULLET_COLLIDE_EFFECT_COLOR)
            color.a = int(alpha * 255)

            boom = pygame.Surface(Vector2(size), flags=pygame.SRCALPHA)

            pygame.draw.circle(boom, color, Vector2(size / 2), size / 2)

            self.__surface.blit(boom, point - Vector2(size / 2))

        # Draw hitboxes
        if self.show_hitboxes:
            for entity in self.__entities:
                pygame.draw.lines(self.__surface, "#FF0000", True,
                                  entity.absolute_hitbox)

        # Draw quadtree
        if self.show_quadtree:
            assert self.__quadtree, "Quadtree should exist"
            self.__quadtree.render(self.__surface)

        # Draw closest robot lines
        if self.show_nearest_robot:
            for robot in self.get_entities_of_type(Robot):
                assert type(robot) is Robot, "Shouldn't happen"

                nearest = self.nearest_robot(robot)
                if nearest is None:
                    continue

                point1 = robot.position
                point2 = nearest.position

                middle = (point1 + point2) / 2
                direction = (point2 - point1).normalize()
                normal = direction.rotate_rad(math.pi / 2)

                tip_base = middle - direction * 8 * math.sqrt(3)
                tip_left = tip_base - normal * 8
                tip_right = tip_base + normal * 8

                pygame.draw.line(self.__surface, "#00FF00", point1, point2)
                pygame.draw.polygon(self.__surface, "#00FF00",
                                    [middle, tip_left, tip_right])

        # Draw Wall pathfinding hitboxes
        if self.show_pathfinding_hitbox:
            for wall in self.get_entities_of_type(Wall):
                assert type(wall) is Wall, "Shouldn't happen"
                pygame.draw.lines(self.__surface, "#FFFFFF", True,
                                  wall.pathfinding_hitbox)

        # Draw pathfinding graph
        if self.show_path_graph:
            assert self.__path_graph is not None
            self.__path_graph.render(self.__surface)

        # Draw paths
        if self.show_paths:
            for path in self.__paths:
                if len(path) < 2:
                    continue
                pygame.draw.lines(self.__surface, "#FFFF00", False, path)
            # Clear paths to avoid memory leak
            self.__paths = []

        # Draw Robot nodes
        if self.show_robot_nodes:
            assert self.__path_graph is not None
            for robot in self.get_entities_of_type(Robot):
                nodes = self.__path_graph.get_visible_nodes(robot.position,
                                                            robot.rotation)
                for node in nodes:
                    pygame.draw.circle(self.__surface, "#00FFFF",
                                       node.position, 8)

    def __rank_robots(self) -> list[tuple[Robot, Controller, int]]:
        """Ranks the robots in the Arena."""
        def robot_stats(robot: Robot):
            """
            Computes an ordered triple of stats to rank Robots with. Ranks
            firstly by their its of death (infinite if it is alive), then by
            number of coins, then by their remaining health (matters only if
            it's alive).
            """
            return (robot.death_time, robot.coins, robot.health)

        sorted_robots = sorted(self.__robots, key=lambda t: robot_stats(t[0]),
                               reverse=True)

        # Calculate placements, with ties considered
        ranked_robots = list[tuple[Robot, Controller, int]]()

        place = 1
        for i, (robot, controller) in enumerate(sorted_robots):
            if i > 0:
                previous = sorted_robots[i - 1][0]
                if robot_stats(previous) != robot_stats(robot):
                    place += 1

            ranked_robots.append((robot, controller, place))

        return ranked_robots

    def __should_still_run(self, time_limit: float) -> bool:
        """Determines if the Arena simulation should keep running."""
        # Check for time limit
        if self.total_sim_time >= time_limit:
            return False

        # Check if there are at least 2 living robots
        ranked = self.__rank_robots()
        robot_count = 0
        while robot_count < len(ranked) and ranked[robot_count][0].health > 0:
            robot_count += 1

        return robot_count >= 2

    def update(self, dt: float):
        """Updates the state of the arena after time delta `dt`, in seconds."""
        self.total_sim_time += dt
        self.__update_shrinking()
        self.__update_coin()
        self.__update_robots(dt)
        self.__update_entities(dt)
        self.__filter_entities()
        self.__construct_quadtree()
        self.__solve_collisions()
        self.__update_bullets(dt)
        self.__clear_offscreen_entities()
        self.__filter_entities()
        self.__render_scene()

    def run(self, time_limit: float = math.inf):
        """
        Runs simulation of the Arena, returning the leaderboard once finished.

        An optional time limit argument may be provided.
        """
        has_path_graph = self.__path_graph is not None
        assert has_path_graph, ("Must call Arena.prepare_path_graph after "
                                "generating walls and before spawning other "
                                "entities!")

        # Initialize pygame, if not yet initialized
        if not pygame.get_init():
            pygame.init()

        robot_list = RobotList()
        window_size = self.window_size
        viewport_size = self.viewport_size
        window = pygame.display.set_mode(window_size)
        clock = pygame.time.Clock()
        dt = 0

        # Font to render debug text
        font = pygame.font.SysFont(pygame.font.get_default_font(), 24)

        total_frames = 0
        total_frame_time = 0        # Actual elapsed time
        self.total_sim_time = 0     # Simulated time

        while self.__should_still_run(time_limit):
            # Check for pygame.QUIT event
            should_quit = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Returning None indicates ending the whole simulation
                    print("Aborting")
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("Skipping")
                        should_quit = True
                        break
            if should_quit:
                break

            # Clear window
            window.fill(ROBOT_LIST_COLOR)

            # Increment frames and frame time for calculating FPS at the end
            total_frames += 1
            total_frame_time += dt

            # If simulation runs slower, keep time step at .25x desired rate to
            # prevent large time steps
            time_step = min(dt, 4 / FRAME_RATE)

            # Simulate a time step
            self.update(time_step)

            surface = self.__surface
            # Crop surface if shrinking
            if self.shrink_rate > 0 and self.shrink_zoom:
                diff = self.__original_size - self.__size
                surface = surface.subsurface(Rect(diff / 2, self.__size))

            # Scale arena surface contents to create viewport surface
            ratio = surface.get_width() / viewport_size.x
            viewport = None
            if ratio > 2:
                # Use faster, normal scale if the ratio is too large
                viewport = pygame.transform.scale(surface, viewport_size)
            else:
                # Use slower, smooth scale if the ratio isn't too large
                viewport = pygame.transform.smoothscale(surface, viewport_size)

            # Draw framerate onto the viewport
            if self.show_fps and dt > 0:
                viewport.blit(
                    font.render(f"FPS: {int(1 / dt)}", True, "#FF0000",
                                "#000000"),
                    Vector2(),
                )

            # Draw coordinate hover
            if self.show_mouse_coordinates and pygame.mouse.get_focused():
                coords = self.window_to_arena(Vector2(pygame.mouse.get_pos()))
                x, y = int(coords.x), int(coords.y)
                text = font.render(f"({x}, {y})", True, "#FF0000", "#000000")
                text_x = viewport.get_width() - text.get_width()
                viewport.blit(text, (text_x, 0))

            # Draw viewport onto screen
            window.blit(viewport, Vector2(ROBOT_LIST_WIDTH, 0))

            # Draw Robot list
            ranked = [(r, p) for r, _, p in self.__rank_robots()]
            robot_list.render(window, ranked, time_limit, self.total_sim_time)

            # Display results on window
            pygame.display.flip()

            # Limit FPS
            dt = clock.tick(FRAME_RATE) / 1000

        results = self.__rank_robots()

        winner_font = pygame.font.SysFont(pygame.font.get_default_font(), 64)
        continue_font = pygame.font.SysFont(pygame.font.get_default_font(), 48)

        # Game over screen
        while True:
            # Check for pygame.QUIT event
            should_quit = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Returning None indicates ending the whole simulation
                    print("Aborting")
                    pygame.quit()
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_quit = True
                        break
            if should_quit:
                break

            # Clear window
            window.fill(ROBOT_LIST_COLOR)

            # Draw winning robot
            if len(results) > 0:
                winner, *_ = results[0]
                winner.turn_power = 1
                winner.turret_turn_power = -1
                winner.update(dt)
                winner.render_at_position(window, Vector2(window_size.x / 2,
                                                          window_size.y / 3))

                winner_text = winner_font.render(f"{winner.name} wins!", True,
                                                 "#FFFFFF")
                winner_x = window_size.x / 2 - winner_text.get_width() / 2
                winner_y = window_size.y / 3 + 256
                window.blit(winner_text, (winner_x, winner_y))

            continue_text = continue_font.render("Press Escape to continue...",
                                                 True, "#FFFFFF")
            continue_x = window_size.x / 2 - continue_text.get_width() / 2
            continue_y = window_size.y / 3 + 320
            window.blit(continue_text, (continue_x, continue_y))

            pygame.display.flip()

            dt = clock.tick(FRAME_RATE) / 1000

        pygame.quit()

        if self.show_fps:
            print(f"Overall FPS: {total_frames / total_frame_time}")

        return results

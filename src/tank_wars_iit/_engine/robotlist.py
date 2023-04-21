import math

import pygame

from tank_wars_iit._engine.entity.coin import Coin, COIN_RADIUS
from tank_wars_iit._engine.entity.robot import (HEALTH_COLOR,
                                                HEALTH_DEFICIT_COLOR,
                                                MAX_HEALTH, Robot,
                                                ROBOT_RADIUS)

Rect = pygame.Rect
Surface = pygame.Surface
Vector2 = pygame.Vector2

WIDTH = 256
COLOR = "#444444"

PADDING = 8

TITLE_HEIGHT = 52

NAME_HEIGHT = 24
STATS_HEIGHT = 16
ENTRY_HEIGHT = STATS_HEIGHT + PADDING + NAME_HEIGHT

HEALTH_BAR_HEIGHT = 4

coin: Coin | None = None


def format_time(time: float) -> str:
    # Show seconds w/ decimals if less than one minute
    if time < 60:
        return str(int(time * 10) / 10)

    # Show formatted mm:ss w/o decimal if at least a minute
    time_int = int(time)
    minutes = time_int // 60
    seconds = time_int % 60

    # Prepend the seconds with a 0 if it's single-digit
    if seconds < 10:
        seconds = f"0{seconds}"

    return f"{minutes}:{seconds}"


def render_robot_list(surface: Surface, robots: list[tuple[Robot, int]],
                      time_limit: float, sim_time: float, coin: Coin,
                      name_font: pygame.font.Font,
                      stats_font: pygame.font.Font,
                      title_font: pygame.font.Font):
    """
    Renders list of Robots on the left side of the window, along with other
    information.
    """
    # Render the coin icon
    coin.update(1 / 60)
    coin_icon = Surface(Vector2(COIN_RADIUS * 2), flags=pygame.SRCALPHA)
    coin.render(coin_icon)
    coin_icon = pygame.transform.smoothscale_by(coin_icon,
                                                STATS_HEIGHT / COIN_RADIUS / 2)

    #    v-------------------- [   ROBOT LIST LAYOUT    ] --------------------v
    # 4P [                                                                    ]
    # TH [                                TITLE                               ]
    # P  [                                                                    ]
    # NH [                                TIME                                ]
    # P  [                                                                    ]
    # NH [                             ROBOTS LEFT                            ]
    # 4P [                                                                    ]
    #    v-------------------- [   ROBOT ENTRY LAYOUT   ] --------------------v
    # NH [ 2P |                   NAME                  | P |   RENDER   | 2P ]
    # P  [                                                  |   RENDER   | 2P ]
    # SH [ 2P |      HEALTH      | P | COIN | P | COUNT | P |   RENDER   | 2P ]
    # P  [                                                                    ]
    #    ^-------------------- [ END ROBOT ENTRY LAYOUT ] --------------------^
    #    ^-------------------- [ END ROBOT LIST LAYOUT  ] --------------------^
    # Legend:
    #   - P  = PADDING
    #   - TH = TITLE_HEIGHT
    #   - NH = NAME_HEIGHT
    #   - SH = STATS_HEIGHT

    # Top margin (4P)
    y = PADDING * 4

    # Title (TH)
    title = title_font.render("Tank Wars!", True, "#FFFFFF")
    title_position = Vector2(WIDTH / 2 - title.get_width() / 2, y)
    surface.blit(title, title_position)
    y += title.get_height()

    # Show remaining time (if timed)
    if math.isfinite(time_limit):
        # Title-to-time padding (P)
        y += PADDING

        # Time (NH)
        time_left = format_time(time_limit - sim_time)
        time = name_font.render(f"Simulated Time Left: {time_left}", True,
                                "#FFFFFF")
        time_position = Vector2(WIDTH / 2 - time.get_width() / 2, y)
        surface.blit(time, time_position)
        y += time.get_height()

    # Title/time-to-robots-left padding (P)
    y += PADDING

    # Robots left (NH)
    num_robots = 0
    while num_robots < len(robots) and robots[num_robots][0].health > 0:
        num_robots += 1
    robots_left = name_font.render(f"Tanks Left: {num_robots}", True,
                                   "#FFFFFF")
    robots_left_position = Vector2(WIDTH / 2 - robots_left.get_width() / 2, y)
    surface.blit(robots_left, robots_left_position)
    y += robots_left.get_height()

    # Robots-left-to-leaderboard padding (4P)
    y += PADDING * 4

    # Robot entries
    for robot, place in robots:
        # Quit early if it won't be visible
        if y >= surface.get_height():
            break

        # Name (NH)

        # Name label max width (WIDTH - 2P - P - EH - 2P)
        name_max_width = WIDTH - 5 * PADDING - ENTRY_HEIGHT
        name = name_font.render(f"{place}. {robot.name}", True, "#FFFFFF")

        # Scale down the name if it exceeds max width
        if name.get_width() > name_max_width:
            ratio = name_max_width / name.get_width()
            name = pygame.transform.smoothscale_by(name, ratio)

        # Center name label within NH space
        name_position = Vector2(PADDING * 2,
                                y + NAME_HEIGHT / 2 - name.get_height() / 2)
        surface.blit(name, name_position)

        # Robot render (EH)
        robot_position = Vector2(3 * PADDING + name_max_width, y)
        if robot.health > 0:
            # Render the robot if it's alive only
            robot_surface = Surface(Vector2(ROBOT_RADIUS * 2),
                                    flags=pygame.SRCALPHA)
            robot.render_at_position(robot_surface, Vector2(ROBOT_RADIUS))
            ratio = ENTRY_HEIGHT / (2 * ROBOT_RADIUS)
            if len(robots) <= 2:
                robot_surface = pygame.transform.smoothscale_by(robot_surface,
                                                                ratio)
            else:
                # Use normal scale_by to save on performance
                robot_surface = pygame.transform.scale_by(robot_surface,
                                                          ratio)
            surface.blit(robot_surface, robot_position)
        else:
            # If dead, show a big red X
            x_size = ENTRY_HEIGHT - PADDING
            center = robot_position + Vector2(ENTRY_HEIGHT) / 2
            top_left = center - Vector2(x_size) / 2
            top_right = center + Vector2(x_size, -x_size) / 2
            bottom_left = center + Vector2(-x_size, x_size) / 2
            bottom_right = center + Vector2(x_size) / 2
            pygame.draw.line(surface, HEALTH_DEFICIT_COLOR, top_left,
                             bottom_right, 8)
            pygame.draw.line(surface, HEALTH_DEFICIT_COLOR, top_right,
                             bottom_left, 8)
        y += NAME_HEIGHT

        # Name-to-stats padding (P)
        y += PADDING

        # Stats (SH)

        # Health bar width (WIDTH - 2P - P - SH - P - SH - P - EH - 2P)
        red_width = WIDTH - 7 * PADDING - 2 * STATS_HEIGHT - ENTRY_HEIGHT
        green_width = red_width * (robot.health / MAX_HEALTH)

        # Center health bar within vertical SH space
        health_position = Vector2(PADDING * 2,
                                  y + STATS_HEIGHT / 2 - HEALTH_BAR_HEIGHT / 2)
        pygame.draw.rect(surface, HEALTH_DEFICIT_COLOR,
                         Rect(health_position,
                              Vector2(red_width, HEALTH_BAR_HEIGHT)))
        pygame.draw.rect(surface, HEALTH_COLOR,
                         Rect(health_position,
                              Vector2(green_width, HEALTH_BAR_HEIGHT)))

        # Display death time if dead
        if robot.health <= 0:
            time_left = format_time(time_limit - robot.death_time)
            death = stats_font.render(f"Died at {time_left}", True,
                                      "#FFFFFF")
            death_position = Vector2(PADDING * 2 + red_width / 2
                                     - death.get_width() / 2,
                                     y + STATS_HEIGHT / 2
                                     - death.get_height() / 2)

            # Render text background
            bg_rect = Rect(death_position - Vector2(PADDING),
                           Vector2(death.get_size()) + Vector2(PADDING * 2))
            pygame.draw.rect(surface, COLOR, bg_rect)

            surface.blit(death, death_position)

        # Coin icon
        coin_position = Vector2(3 * PADDING + red_width, y)
        surface.blit(coin_icon, coin_position)

        # Coin count
        count = stats_font.render(str(robot.coins), True, "#FFFFFF")
        # Center coin count within vertical SH space
        count_position = Vector2(4 * PADDING + red_width + STATS_HEIGHT,
                                 y + STATS_HEIGHT / 2 - count.get_height() / 2)
        surface.blit(count, count_position)

        y += STATS_HEIGHT

        # Entry-to-entry padding (P)
        y += PADDING


class RobotList:
    def __init__(self):
        self.name_font = pygame.font.SysFont(pygame.font.get_default_font(),
                                             NAME_HEIGHT)
        self.stats_font = pygame.font.SysFont(pygame.font.get_default_font(),
                                              STATS_HEIGHT + 8)
        self.title_font = pygame.font.SysFont(pygame.font.get_default_font(),
                                              TITLE_HEIGHT)

        self.coin = Coin(Vector2(COIN_RADIUS))

    def render(self, surface: Surface, robots: list[tuple[Robot, int]],
               time_limit: float, sim_time: float):
        render_robot_list(surface, robots, time_limit, sim_time, self.coin,
                          self.name_font, self.stats_font, self.title_font)

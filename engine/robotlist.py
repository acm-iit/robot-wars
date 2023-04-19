import pygame

from engine.entity.coin import Coin, COIN_RADIUS
from engine.entity.robot import (HEALTH_COLOR, HEALTH_DEFICIT_COLOR,
                                 MAX_HEALTH, Robot, ROBOT_RADIUS)

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

name_font: pygame.font.Font | None = None
stats_font: pygame.font.Font | None = None
title_font: pygame.font.Font | None = None
coin: Coin | None = None


def robot_stats(robot: Robot):
    """Computes an ordered triple of stats to rank Robots with."""
    return (robot.death_time, robot.coins, robot.health)


def render_robot_list(surface: Surface, robots: list[Robot]):
    """
    Renders list of Robots on the left side of the window, along with other
    information.
    """
    global coin, name_font, stats_font, title_font

    # Initialize Coin used for rendering an icon (yes this is hacky)
    if coin is None:
        coin = Coin(Vector2(COIN_RADIUS))

    # Initialize fonts
    if name_font is None:
        name_font = pygame.font.SysFont(pygame.font.get_default_font(),
                                        NAME_HEIGHT)
    if stats_font is None:
        stats_font = pygame.font.SysFont(pygame.font.get_default_font(),
                                         STATS_HEIGHT + 8)
    if title_font is None:
        title_font = pygame.font.SysFont(pygame.font.get_default_font(),
                                         TITLE_HEIGHT)

    # Render the coin icon
    coin.update(1 / 60)
    coin_icon = Surface(Vector2(COIN_RADIUS * 2), flags=pygame.SRCALPHA)
    coin.render(coin_icon)
    coin_icon = pygame.transform.smoothscale_by(coin_icon,
                                                STATS_HEIGHT / COIN_RADIUS / 2)

    y = PADDING * 4

    title = title_font.render("Tank Wars!", True, "#FFFFFF")
    title_position = Vector2(WIDTH / 2 - title.get_width() / 2, y)
    surface.blit(title, title_position)

    y += title.get_height() + PADDING * 4

    # Sort robots by health and coins
    robots = sorted(robots, key=robot_stats, reverse=True)

    place = 1
    for i, robot in enumerate(robots):
        if i > 0 and robot_stats(robots[i - 1]) != robot_stats(robots[i]):
            place += 1

        name_max_width = WIDTH - 5 * PADDING - ENTRY_HEIGHT
        name = name_font.render(f"{place}. {robot.name}", True, "#FFFFFF")
        if name.get_width() > name_max_width:
            ratio = name_max_width / name.get_width()
            name = pygame.transform.smoothscale_by(name, ratio)

        name_position = Vector2(PADDING * 2,
                                y + NAME_HEIGHT / 2 - name.get_height() / 2)
        surface.blit(name, name_position)

        robot_position = Vector2(3 * PADDING + name_max_width, y)

        if robot.health > 0:
            robot_surface = Surface(Vector2(ROBOT_RADIUS * 2),
                                    flags=pygame.SRCALPHA)
            robot.render_at_position(robot_surface, Vector2(ROBOT_RADIUS))
            ratio = ENTRY_HEIGHT / (2 * ROBOT_RADIUS)
            robot_surface = pygame.transform.smoothscale_by(robot_surface,
                                                            ratio)
            surface.blit(robot_surface, robot_position)
        else:
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

        y += NAME_HEIGHT + PADDING

        red_width = WIDTH - 6 * PADDING - 2 * STATS_HEIGHT - ENTRY_HEIGHT
        green_width = red_width * (robot.health / MAX_HEALTH)

        health_position = Vector2(PADDING * 2,
                                  y + STATS_HEIGHT / 2 - HEALTH_BAR_HEIGHT / 2)
        pygame.draw.rect(surface, HEALTH_DEFICIT_COLOR,
                         Rect(health_position,
                              Vector2(red_width, HEALTH_BAR_HEIGHT)))
        pygame.draw.rect(surface, HEALTH_COLOR,
                         Rect(health_position,
                              Vector2(green_width, HEALTH_BAR_HEIGHT)))

        coin_position = Vector2(3 * PADDING + red_width, y)
        surface.blit(coin_icon, coin_position)

        count = stats_font.render(str(robot.coins), True, "#FFFFFF")
        count_position = Vector2(4 * PADDING + red_width + STATS_HEIGHT,
                                 y + STATS_HEIGHT / 2 - count.get_height() / 2)
        surface.blit(count, count_position)

        y += STATS_HEIGHT + PADDING

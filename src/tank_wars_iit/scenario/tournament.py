import math
import sys
from typing import cast, Literal

import pygame

from tank_wars_iit._engine.control import Controller
from tank_wars_iit._engine.entity.robot import Robot, ROBOT_RADIUS
from tank_wars_iit.scenario import battle_royale, one_vs_one

Rect = pygame.Rect
Vector2 = pygame.Vector2

Seeding = list[type[Controller] | None]

MAX_BRACKET_WINDOW_SIZE = (1800, 1000)
TEXT_HEIGHT = 64
SMALL_TEXT_HEIGHT = 32
TEXT_WIDTH = 512
MARGIN = TEXT_HEIGHT
ROUND_GAP = 128

BRACKET_BG_COLOR = "#555555"
SEED_BG_COLOR = "#777777"
NAME_BG_COLOR = "#BBBBBB"
WIN_SEED_BG_COLOR = "#999900"
WIN_NAME_BG_COLOR = "#DDDD00"
LINE_COLOR = "#777777"
WIN_LINE_COLOR = "#BBBBBB"
TEXT_COLOR = "#FFFFFF"
NEXT_MATCH_BG_COLOR = "#FFFFFF"
NEXT_MATCH_TEXT_COLOR = "#000000"


class Matchup:
    def __init__(self, next_index: int,
                 controller1: type[Controller] | None = None,
                 controller2: type[Controller] | None = None,
                 seed1: int = 0, seed2: int = 0,
                 winner: Literal[1, 2] | None = None):
        self.next_index = next_index
        self.controller1 = controller1
        self.controller2 = controller2
        self.seed1 = seed1
        self.seed2 = seed2
        self.winner = winner

    def __repr__(self) -> str:
        # Easily print out Matchup initialization code for easy state saving
        name1 = ("None" if self.controller1 is None
                 else self.controller1.__name__)
        name2 = ("None" if self.controller2 is None
                 else self.controller2.__name__)
        return (f"Matchup({self.next_index}, {name1}, {name2}, {self.seed1}, "
                f"{self.seed2}, {self.winner})")


def blank_bracket(num_rounds: int):
    return [[Matchup(i // 2) for i in range(2 ** round_num)]
            for round_num in range(num_rounds - 1, -1, -1)]


def determine_order(num_rounds: int):
    order = [0]

    for i in range(num_rounds):
        new_order = []
        for j, seed in enumerate(order):
            opponent = 2 ** (i + 1) - 1 - seed
            if j % 2 == 0:
                new_order += [seed, opponent]
            else:
                new_order += [opponent, seed]
        order = new_order

    return order


def construct_bracket(seeding: list[type[Controller]]):
    num_rounds = math.ceil(math.log2(len(seeding)))
    # A matchup against None represents a bye round
    num_byes = 2 ** num_rounds - len(seeding)
    padded_seeding = cast(Seeding, seeding + [None] * num_byes)

    bracket = blank_bracket(num_rounds)
    order = determine_order(num_rounds)
    for i, seed in enumerate(order):
        if i % 2 == 0:
            bracket[0][i // 2].controller1 = padded_seeding[seed]
            bracket[0][i // 2].seed1 = seed + 1
        else:
            bracket[0][i // 2].controller2 = padded_seeding[seed]
            bracket[0][i // 2].seed2 = seed + 1

    # Auto-win the BYE matchups
    for i, matchup in enumerate(bracket[0]):
        if matchup.controller1 is None:
            matchup.winner = 2
            if len(bracket) < 2:
                continue
            next_matchup = bracket[1][matchup.next_index]
            if i % 2 == 0:
                next_matchup.controller1 = matchup.controller2
                next_matchup.seed1 = matchup.seed2
            else:
                next_matchup.controller2 = matchup.controller2
                next_matchup.seed2 = matchup.seed2
        elif matchup.controller2 is None:
            matchup.winner = 1
            if len(bracket) < 2:
                continue
            next_matchup = bracket[1][matchup.next_index]
            if i % 2 == 0:
                next_matchup.controller1 = matchup.controller1
                next_matchup.seed1 = matchup.seed1
            else:
                next_matchup.controller2 = matchup.controller1
                next_matchup.seed2 = matchup.seed1

    return bracket


def graceful_exit(bracket: list[list[Matchup]] | None = None):
    if bracket is not None:
        print("In case you want to pick up where you left off, here's the "
              "state of the bracket:")
        print(bracket)
    sys.exit(0)


def render_robot_preview(controller: type[Controller]):
    robot = Robot("Dummy")
    robot.color = controller.body_color
    robot.head_color = controller.head_color

    surface = pygame.Surface(Vector2(ROBOT_RADIUS * 2), flags=pygame.SRCALPHA)
    robot.render_at_position(surface, Vector2(ROBOT_RADIUS))

    del robot

    return surface


def render_matchup(surface: pygame.Surface, matchup: Matchup,
                   x: float, y: float, is_next_matchup: bool,
                   is_first_round: bool):
    # Fonts used
    font_name = pygame.font.get_default_font()
    font = pygame.font.SysFont(font_name, TEXT_HEIGHT)
    small_font = pygame.font.SysFont(font_name, SMALL_TEXT_HEIGHT)

    controller1, controller2 = matchup.controller1, matchup.controller2

    # Figure out background colors based on winner
    seed1_bg_color = SEED_BG_COLOR
    seed2_bg_color = SEED_BG_COLOR
    name1_bg_color = NAME_BG_COLOR
    name2_bg_color = NAME_BG_COLOR
    if matchup.winner == 1:
        seed1_bg_color = WIN_SEED_BG_COLOR
        name1_bg_color = WIN_NAME_BG_COLOR
    elif matchup.winner == 2:
        seed2_bg_color = WIN_SEED_BG_COLOR
        name2_bg_color = WIN_NAME_BG_COLOR

    # If this is the next matchup, highlight it
    if is_next_matchup:
        box_pos = Vector2(x - 8, y - SMALL_TEXT_HEIGHT)
        box_size = Vector2(TEXT_WIDTH + 16,
                           2 * TEXT_HEIGHT + SMALL_TEXT_HEIGHT + 8)
        pygame.draw.rect(surface, NEXT_MATCH_BG_COLOR, Rect(box_pos, box_size))
        label = small_font.render("NEXT MATCH", True, NEXT_MATCH_TEXT_COLOR)
        label_y = y - SMALL_TEXT_HEIGHT / 2 - label.get_height() / 2
        surface.blit(label, (x, label_y))

    # Draw backgrounds
    pygame.draw.rect(surface, name1_bg_color,
                     Rect(x, y, TEXT_WIDTH, TEXT_HEIGHT))
    pygame.draw.rect(surface, name2_bg_color,
                     Rect(x, y + TEXT_HEIGHT, TEXT_WIDTH, TEXT_HEIGHT))
    pygame.draw.rect(surface, seed1_bg_color,
                     Rect(x, y, TEXT_HEIGHT, TEXT_HEIGHT))
    pygame.draw.rect(surface, seed2_bg_color,
                     Rect(x, y + TEXT_HEIGHT, TEXT_HEIGHT, TEXT_HEIGHT))

    # Formatted seeds
    seed1 = str(matchup.seed1) if matchup.seed1 > 0 else "?"
    seed2 = str(matchup.seed2) if matchup.seed2 > 0 else "?"

    # Names w/ BYE or TBD for None values, depending on round
    # Show "BYE" in first round; "TBD" otherwise
    blank = "BYE" if is_first_round else "TBD"
    name1 = controller1.name if controller1 is not None else blank
    name2 = controller2.name if controller2 is not None else blank

    # Seed text labels
    seed1_text = font.render(seed1, True, TEXT_COLOR)
    seed2_text = font.render(seed2, True, TEXT_COLOR)

    # Name text labels
    name1_text = font.render(name1, True, TEXT_COLOR)
    name2_text = font.render(name2, True, TEXT_COLOR)

    # Scale seed labels to fit
    if seed1_text.get_width() > TEXT_HEIGHT:
        ratio = TEXT_HEIGHT / seed1_text.get_width()
        seed1_text = pygame.transform.smoothscale_by(seed1_text, ratio)
    if seed2_text.get_width() > TEXT_HEIGHT:
        ratio = TEXT_HEIGHT / seed2_text.get_width()
        seed2_text = pygame.transform.smoothscale_by(seed2_text, ratio)

    # Scale name labels to fit
    if name1_text.get_width() > TEXT_WIDTH - 2 * TEXT_HEIGHT - 4:
        ratio = (TEXT_WIDTH - 2 * TEXT_HEIGHT - 4) / name1_text.get_width()
        name1_text = pygame.transform.smoothscale_by(name1_text, ratio)
    if name2_text.get_width() > TEXT_WIDTH - 2 * TEXT_HEIGHT - 4:
        ratio = (TEXT_WIDTH - 2 * TEXT_HEIGHT - 4) / name2_text.get_width()
        name2_text = pygame.transform.smoothscale_by(name2_text, ratio)

    # Figure out seed label coordinates
    seed1_x = x + TEXT_HEIGHT / 2 - seed1_text.get_width() / 2
    seed1_y = y + TEXT_HEIGHT / 2 - seed1_text.get_height() / 2
    seed2_x = x + TEXT_HEIGHT / 2 - seed2_text.get_width() / 2
    seed2_y = y + 3 * TEXT_HEIGHT / 2 - seed2_text.get_height() / 2

    # Figure out name label coordinates
    name1_x = x + TEXT_HEIGHT + 4
    name1_y = y + TEXT_HEIGHT / 2 - name1_text.get_height() / 2
    name2_x = x + TEXT_HEIGHT + 4
    name2_y = y + 3 * TEXT_HEIGHT / 2 - name2_text.get_height() / 2

    # Draw seed labels onto surface
    surface.blit(seed1_text, Vector2(seed1_x, seed1_y))
    surface.blit(seed2_text, Vector2(seed2_x, seed2_y))

    # Draw name labels onto surface
    surface.blit(name1_text, Vector2(name1_x, name1_y))
    surface.blit(name2_text, Vector2(name2_x, name2_y))

    # Draw robot previews
    if controller1 is not None:
        preview = render_robot_preview(controller1)
        scaled = pygame.transform.smoothscale(preview, Vector2(TEXT_HEIGHT))
        surface.blit(scaled, (x + TEXT_WIDTH - TEXT_HEIGHT, y))
    if controller2 is not None:
        preview = render_robot_preview(controller2)
        scaled = pygame.transform.smoothscale(preview, Vector2(TEXT_HEIGHT))
        surface.blit(scaled, (x + TEXT_WIDTH - TEXT_HEIGHT, y + TEXT_HEIGHT))

    # Move y-cursor below this matchup
    return TEXT_HEIGHT * 2


def render_bracket(bracket: list[list[Matchup]],
                   next_matchup: Matchup | None = None,
                   current_round: int = 0,
                   third_place_matchup: Matchup | None = None):
    if not pygame.get_init():
        pygame.init()

    # Font for third place and continue text
    font = pygame.font.SysFont(pygame.font.get_default_font(), TEXT_HEIGHT)

    num_rounds = len(bracket) - current_round

    # Figure out side of bracket surface (may be scaled down to fit window)
    width = (2 * MARGIN + (TEXT_WIDTH + ROUND_GAP) * (2 * num_rounds - 1)
             - ROUND_GAP)
    height_in_rounds = (len(bracket[current_round + 1])
                        if current_round < len(bracket) - 1
                        else len(bracket[current_round]))
    height = (2 * MARGIN + (3 * TEXT_HEIGHT) * height_in_rounds
              + TEXT_HEIGHT * 5)
    box_size = Vector2(width, height)

    surface = pygame.Surface(box_size)

    # Gray background
    surface.fill(BRACKET_BG_COLOR)

    for i in range(num_rounds):
        round = bracket[current_round + i]
        x = MARGIN + (TEXT_WIDTH + ROUND_GAP) * i

        spacing = TEXT_HEIGHT * 3 / 2 * (2 ** i - 1)
        if i != 0 and i == num_rounds - 1:
            spacing = TEXT_HEIGHT * 3 / 2 * (2 ** (i - 1) - 1)
        y = MARGIN + spacing

        left_side = True

        for j, matchup in enumerate(round):
            # Flip to the other side once we're halfway through this round's
            # matchups
            if j == 2 ** (num_rounds - i - 2):
                y = MARGIN + spacing
                x = width - MARGIN - (TEXT_WIDTH + ROUND_GAP) * i - TEXT_WIDTH
                left_side = False

            # Draw connecting line
            if i != num_rounds - 1:
                out_x = x + TEXT_WIDTH if left_side else x
                out_y = y + TEXT_HEIGHT

                mid_x = (x + TEXT_WIDTH + ROUND_GAP / 2 if left_side
                         else x - ROUND_GAP / 2)

                in_x = (x + TEXT_WIDTH + ROUND_GAP if left_side
                        else x - ROUND_GAP)
                in_y = 0

                next_spacing = TEXT_HEIGHT * 3 / 2 * (2 ** (i + 1) - 1)
                if i == num_rounds - 2:
                    next_spacing = TEXT_HEIGHT * 3 / 2 * (2 ** i - 1)

                if j % 2 == 0:
                    in_y = y + (next_spacing - spacing) + TEXT_HEIGHT / 2
                else:
                    in_y = y - (next_spacing - spacing) + 3 * TEXT_HEIGHT / 2

                line_color = (LINE_COLOR if matchup.winner is None
                              else WIN_LINE_COLOR)
                pygame.draw.lines(surface, line_color, False,
                                  [(out_x, out_y), (mid_x, out_y),
                                   (mid_x, in_y), (in_x, in_y)], 8)

            # Move y-cursor below this matchup
            y += render_matchup(surface, matchup, x, y,
                                matchup == next_matchup,
                                i == 0 and current_round == 0)

            if i != num_rounds - 1:
                # Move y-cursor to next matchup
                y += spacing * 2 + TEXT_HEIGHT
            else:
                # Render finals matchup label
                final_text = font.render("Grand Finals", True, TEXT_COLOR)
                final_x = x + TEXT_WIDTH / 2 - final_text.get_width() / 2
                final_y = y + TEXT_HEIGHT / 2 - final_text.get_height() / 2
                surface.blit(final_text, (final_x, final_y))

                if third_place_matchup is None:
                    continue

                # Move y-cursor to third place matchup
                y += 2 * TEXT_HEIGHT
                y += render_matchup(surface, third_place_matchup, x, y,
                                    third_place_matchup == next_matchup, False)

                # Render third place matchup label
                third_text = font.render("Bronze Match", True, TEXT_COLOR)
                third_x = x + TEXT_WIDTH / 2 - third_text.get_width() / 2
                third_y = y + TEXT_HEIGHT / 2 - third_text.get_height() / 2
                surface.blit(third_text, (third_x, third_y))

    # Render continue text
    cont_text = font.render("Press Escape to continue...", True, TEXT_COLOR)
    cont_text_x = width / 2 - cont_text.get_width() / 2
    cont_text_y = (height - MARGIN - TEXT_HEIGHT / 2
                   - cont_text.get_height() / 2)
    surface.blit(cont_text, (cont_text_x, cont_text_y))

    # Figure out window size that fits in max dimensions
    window_rect = Rect((0, 0), MAX_BRACKET_WINDOW_SIZE)
    surface_rect = Rect((0, 0), surface.get_size())
    window_size = surface_rect.fit(window_rect).size

    # Scale surface up to window size and draw onto window
    window = pygame.display.set_mode(window_size)
    pygame.transform.smoothscale(surface, window_size, window)
    pygame.display.flip()

    clock = pygame.time.Clock()

    # Spin until window closed or space pressed
    while True:
        should_quit = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Aborting")
                pygame.quit()
                graceful_exit(bracket)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                should_quit = True
                break

        if should_quit:
            break

        clock.tick(60)

    pygame.quit()


def tournament(controller_classes: list[type[Controller]],
               show_fps=False, show_mouse_coordinates=False,
               lock_camera=False):
    """
    Runs a list of controller classes in a tournament. To determine seeding,
    it runs a battle royale scenario with all of the controllers. It then
    constructs a bracket based on the seeding and runs each match until the
    final winner is determined. It also runs a third place matchup if there are
    at least four controllers.

    Optional parameter `show_fps` can be set to `True` to show FPS in the top
    left.

    Optional parameter `show_mouse_coordinates` can be set to `True` to show
    the user mouse coordinates (in game space) in the top-left; this can be
    useful for figuring out certain coordinates in the map that you want your
    tank to be aware of.

    Optional parameter `lock_camera` can be set to `True` to keep the camera
    from zooming in on the playable area. This can be used in conjunction with
    `show_mouse_coordinates` to make it easier to find coordinates.
    """
    assert len(controller_classes) > 1, "Multiple controllers required"

    seeding = battle_royale(controller_classes, show_fps,
                            show_mouse_coordinates, lock_camera)

    if seeding is None:
        graceful_exit()

        # For some reason, pylance doesn't detect that graceful_exit stops
        # the program, so I return here to prevent typecheck errors.
        return

    bracket = construct_bracket(seeding)

    third_place_matchup = None
    if len(seeding) >= 4:
        third_place_matchup = Matchup(0)

    for i, round in enumerate(bracket):
        for j, matchup in enumerate(round):
            controller1, controller2 = matchup.controller1, matchup.controller2
            winner = None
            winner_seed = 0

            if controller1 is None or controller2 is None:
                continue

            display_round = min(i, max(len(bracket) - 4, 0))
            render_bracket(bracket, matchup, display_round,
                           third_place_matchup)

            winner = one_vs_one(controller1, controller2,
                                show_fps, show_mouse_coordinates)
            if winner is None:
                graceful_exit(bracket)
                return

            winner_seed = (matchup.seed1 if winner == controller1
                           else matchup.seed2)
            matchup.winner = 1 if winner == controller1 else 2

            if i < len(bracket) - 1:
                next_matchup = bracket[i + 1][matchup.next_index]
                if j % 2 == 0:
                    next_matchup.controller1 = winner
                    next_matchup.seed1 = winner_seed
                else:
                    next_matchup.controller2 = winner
                    next_matchup.seed2 = winner_seed

                # Feed into third_place_matchup
                if i == len(bracket) - 2 and third_place_matchup is not None:
                    loser = (controller1 if winner == controller2
                             else controller2)
                    loser_seed = (matchup.seed1 if loser == controller1
                                  else matchup.seed2)
                    if j % 2 == 0:
                        third_place_matchup.controller1 = loser
                        third_place_matchup.seed1 = loser_seed
                    else:
                        third_place_matchup.controller2 = loser
                        third_place_matchup.seed2 = loser_seed

    if third_place_matchup is not None:
        assert (third_place_matchup.controller1 is not None
                and third_place_matchup.controller2 is not None)

        display_round = max(len(bracket) - 4, 0)
        render_bracket(bracket, third_place_matchup, display_round,
                       third_place_matchup)

        controller1 = third_place_matchup.controller1
        controller2 = third_place_matchup.controller2

        winner = one_vs_one(controller1, controller2, show_fps,
                            show_mouse_coordinates)
        if winner is None:
            graceful_exit()
            return

        third_place_matchup.winner = 1 if winner == controller1 else 2

    render_bracket(bracket, third_place_matchup=third_place_matchup)

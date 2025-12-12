import jeu.globals as G
from jeu.main_david_old import *

def timer():
    """Update world time based on real delta time."""
    delta_real_seconds = G.clock.get_time() / 1000.0
    G.world_hours += delta_real_seconds * G.GAME_HOURS_PER_SECOND

    while G.world_hours >= 24:
        G.world_hours -= 24
        G.world_days += 1

    G.world_minutes = int((G.world_hours % 1) * 60)
    G.display_hours = int(G.world_hours)


def draw_timer():
    draw_time_bar()
    draw_day_bar()

    # toggle button
    btn_color = (200, 50, 50) if G.timer_active else (50, 200, 50)
    pygame.draw.rect(G.screen, btn_color, G.timer_button)

    label = "STOP" if G.timer_active else "PLAY"
    surf = G.font.render(label, True, (255, 255, 255))
    G.screen.blit(surf, (G.timer_button.x + 10, G.timer_button.y + 10))


# ----------------------------------------------------------------------
# TIME BAR
# ----------------------------------------------------------------------

def draw_time_bar():
    """Draw the 24-hour timeline bar."""
    # background
    pygame.draw.rect(G.screen, (100, 100, 100), G.TIME_BAR_RECT, border_radius=5)

    # fill
    fraction = G.world_hours / 24.0
    fill_w = int(G.TIME_BAR_RECT.width * fraction)
    pygame.draw.rect(
        G.screen, (50, 200, 50),
        (G.TIME_BAR_RECT.x, G.TIME_BAR_RECT.y, fill_w, G.TIME_BAR_RECT.height),
        border_radius=5
    )

    # handle
    handle_x = G.TIME_BAR_RECT.x + fill_w
    pygame.draw.rect(G.screen, (255, 0, 0),
                     (handle_x - 3, G.TIME_BAR_RECT.y - 2, 6, G.TIME_BAR_RECT.height + 4))

    # time label
    time_text = f"{int(G.world_hours):02d}:{int(G.world_minutes):02d}"
    surf = G.font.render(time_text, True, (255, 255, 255))
    rect = surf.get_rect(center=G.TIME_BAR_RECT.center)
    G.screen.blit(surf, rect)


def update_time_from_bar(mouse_pos):
    """Scrub the time along the bar."""
    x = mouse_pos[0]
    # clamp
    x = max(G.TIME_BAR_RECT.x, min(x, G.TIME_BAR_RECT.x + G.TIME_BAR_RECT.width))

    fraction = (x - G.TIME_BAR_RECT.x) / G.TIME_BAR_RECT.width
    G.world_hours = fraction * 24.0
    G.world_minutes = int((G.world_hours % 1) * 60)


# ----------------------------------------------------------------------
# DAY BAR
# ----------------------------------------------------------------------

def draw_day_bar():
    """Draw the day counter bar."""
    # background
    pygame.draw.rect(G.screen, (100, 100, 100), G.DAY_BAR_RECT, border_radius=5)

    # fill
    fraction = G.world_days / G.MAX_DAYS
    fill_w = int(G.DAY_BAR_RECT.width * fraction)
    pygame.draw.rect(
        G.screen, (50, 200, 50),
        (G.DAY_BAR_RECT.x, G.DAY_BAR_RECT.y, fill_w, G.DAY_BAR_RECT.height),
        border_radius=5
    )

    # handle
    handle_x = G.DAY_BAR_RECT.x + fill_w
    pygame.draw.rect(G.screen, (255, 0, 0),
                     (handle_x - 3, G.DAY_BAR_RECT.y - 2, 6, G.DAY_BAR_RECT.height + 4))

    # text
    day_text = f"Day {G.world_days}"
    surf = G.font.render(day_text, True, (255, 255, 255))
    rect = surf.get_rect(center=G.DAY_BAR_RECT.center)
    G.screen.blit(surf, rect)


def update_day_from_bar(mouse_pos):
    x = mouse_pos[0]

    # clamp
    x = max(G.DAY_BAR_RECT.x, min(x, G.DAY_BAR_RECT.x + G.DAY_BAR_RECT.width))

    fraction = (x - G.DAY_BAR_RECT.x) / G.DAY_BAR_RECT.width
    G.world_days = int(fraction * G.MAX_DAYS)


def handle_day_bar_click(mouse_pos):
    if G.DAY_BAR_RECT.collidepoint(mouse_pos):
        G.day_bar_dragging = True
        update_day_from_bar(mouse_pos)
        return True
    return False
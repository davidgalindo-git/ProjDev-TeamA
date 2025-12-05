from jeu.main_david_old import *

MAX_DAYS = 1000
world_minutes = 0
world_hours = 0
world_days = 0
display_hours = 0
# 1 real second = 1 game hour
GAME_HOURS_PER_SECOND = 1
# buttons
timer_button = pygame.Rect(20, 20, 120, 40)
# Time bar
TIME_BAR_RECT = pygame.Rect(150, 60, 400, 20)  # x, y, width, height
# Day bar
DAY_BAR_RECT = pygame.Rect(150, 20, 400, 20)  # x, y, width, height

def timer(world_hours, world_days):
    # --- Update world time ---
    delta_real_seconds = clock.get_time() / 1000  # convert ms to seconds

    # Add hours according to your rule
    world_hours += delta_real_seconds * GAME_HOURS_PER_SECOND

    # Handle overflow
    while world_hours >= 24:
        world_hours -= 24
        world_days += 1

    world_minutes = int((world_hours % 1) * 60)
    display_hours = int(world_hours)

    return world_hours, world_days, display_hours, world_minutes

def draw_timer(days):
    global display_hours, world_minutes, timer_active
    draw_time_bar()
    draw_day_bar()

    # --- TIMER CONTROL BUTTON (toggle) ---
    btn_color = (200, 50, 50) if timer_active else (50, 200, 50)
    pygame.draw.rect(screen, btn_color, timer_button)
    button_text = "STOP" if timer_active else "PLAY"
    text_surf = font.render(button_text, True, (255, 255, 255))
    screen.blit(text_surf, (timer_button.x + 10, timer_button.y + 10))

def draw_time_bar():
    """Draw the timeline bar showing current world time with hours:minutes centered."""
    global world_hours, world_minutes

    # Background of the bar
    pygame.draw.rect(screen, (100, 100, 100), TIME_BAR_RECT, border_radius=5)

    # Fill portion of the bar (progress of the day)
    day_progress = world_hours / 24.0
    fill_width = int(TIME_BAR_RECT.width * day_progress)
    pygame.draw.rect(screen, (50, 200, 50), (TIME_BAR_RECT.x, TIME_BAR_RECT.y, fill_width, TIME_BAR_RECT.height), border_radius=5)

    # Handle (small red rectangle)
    handle_x = TIME_BAR_RECT.x + fill_width
    pygame.draw.rect(screen, (255, 0, 0), (handle_x - 3, TIME_BAR_RECT.y - 2, 6, TIME_BAR_RECT.height + 4))

    # Draw the time in the middle of the bar
    time_text = f"{int(world_hours):02d}:{int(world_minutes):02d}"
    text_surface = font.render(time_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=TIME_BAR_RECT.center)
    screen.blit(text_surface, text_rect)

def update_time_from_bar(mouse_pos):
    global world_hours, world_minutes

    mouse_x = mouse_pos[0]  # extract X coordinate

    # Clamp x inside the bar
    x = max(TIME_BAR_RECT.x, min(mouse_x, TIME_BAR_RECT.x + TIME_BAR_RECT.width))

    # Fraction of the bar
    fraction = (x - TIME_BAR_RECT.x) / TIME_BAR_RECT.width

    # Set world_hours as float (fractional)
    world_hours = fraction * 24.0
    world_minutes = int((world_hours % 1) * 60)

def draw_day_bar():
    global world_days

    # Draw background bar
    pygame.draw.rect(screen, (100, 100, 100), DAY_BAR_RECT, border_radius=5)

    # Compute fill width from world_days
    fraction = world_days / MAX_DAYS
    fill_width = int(DAY_BAR_RECT.width * fraction)

    # Fill bar
    pygame.draw.rect(screen, (50, 200, 50), (DAY_BAR_RECT.x, DAY_BAR_RECT.y, fill_width, DAY_BAR_RECT.height), border_radius=5)

    # Draw handle
    handle_x = DAY_BAR_RECT.x + fill_width
    pygame.draw.rect(screen, (255, 0, 0), (handle_x - 3, DAY_BAR_RECT.y - 2, 6, DAY_BAR_RECT.height + 4))

    # Affichage du nombre de jours
    day_text = f"Day {world_days}"
    text_surface = font.render(day_text, True, (255,255,255))
    text_rect = text_surface.get_rect(center=DAY_BAR_RECT.center)
    screen.blit(text_surface, text_rect)


def update_day_from_bar(mouse_pos):
    global world_days

    mouse_x = mouse_pos[0]  # extract X coordinate

    # Clamp X inside the bar
    x = max(DAY_BAR_RECT.x, min(mouse_x, DAY_BAR_RECT.x + DAY_BAR_RECT.width))

    # Fraction along the bar (0 to 1)
    fraction = (x - DAY_BAR_RECT.x) / DAY_BAR_RECT.width

    # Set world_days according to fraction of max
    world_days = int(fraction * MAX_DAYS)

def handle_day_bar_click(mouse_pos):
    global day_bar_dragging
    if DAY_BAR_RECT.collidepoint(mouse_pos):
        day_bar_dragging = True
        update_day_from_bar(mouse_pos)
        return True
    return False

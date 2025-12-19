import pygame
import config as cfg


def update_timer(dt):
    """Update world time based on delta time (dt en secondes)."""
    if not cfg.timer_active:
        return

    cfg.world_hours += dt * cfg.GAME_HOURS_PER_SECOND

    while cfg.world_hours >= 24:
        cfg.world_hours -= 24
        cfg.world_days += 1

    cfg.world_minutes = int((cfg.world_hours % 1) * 60)


def draw_timer_ui(screen, font):
    # 1. Day Bar
    pygame.draw.rect(screen, (100, 100, 100), cfg.DAY_BAR_RECT, border_radius=5)
    day_frac = cfg.world_days / cfg.MAX_DAYS
    pygame.draw.rect(screen, (50, 200, 50),
                     (cfg.DAY_BAR_RECT.x, cfg.DAY_BAR_RECT.y, int(cfg.DAY_BAR_RECT.width * day_frac),
                      cfg.DAY_BAR_RECT.height), border_radius=5)

    # 2. Time Bar
    pygame.draw.rect(screen, (100, 100, 100), cfg.TIME_BAR_RECT, border_radius=5)
    time_frac = cfg.world_hours / 24.0
    pygame.draw.rect(screen, (50, 200, 50),
                     (cfg.TIME_BAR_RECT.x, cfg.TIME_BAR_RECT.y, int(cfg.TIME_BAR_RECT.width * time_frac),
                      cfg.TIME_BAR_RECT.height), border_radius=5)

    # 3. Handles (Curseurs rouges)
    pygame.draw.rect(screen, (255, 0, 0),
                     (cfg.DAY_BAR_RECT.x + int(cfg.DAY_BAR_RECT.width * day_frac) - 3, cfg.DAY_BAR_RECT.y - 2, 6,
                      cfg.DAY_BAR_RECT.height + 4))
    pygame.draw.rect(screen, (255, 0, 0),
                     (cfg.TIME_BAR_RECT.x + int(cfg.TIME_BAR_RECT.width * time_frac) - 3, cfg.TIME_BAR_RECT.y - 2, 6,
                      cfg.TIME_BAR_RECT.height + 4))

    # 4. Bouton PLAY/STOP
    btn_color = (200, 50, 50) if cfg.timer_active else (50, 200, 50)
    pygame.draw.rect(screen, btn_color, cfg.timer_button, border_radius=5)
    label = "STOP" if cfg.timer_active else "PLAY"
    txt = font.render(label, True, (255, 255, 255))
    screen.blit(txt, (cfg.timer_button.x + 35, cfg.timer_button.y + 10))

    # Labels temps
    time_str = f"Day {cfg.world_days} | {int(cfg.world_hours):02d}:{cfg.world_minutes:02d}"
    lbl = font.render(time_str, True, (255, 255, 255))
    screen.blit(lbl, (cfg.TIME_BAR_RECT.x + cfg.TIME_BAR_RECT.width + 10, cfg.TIME_BAR_RECT.y))


def handle_timer_logic(mouse_pos, is_click=False):
    """Gère les interactions avec les barres et le bouton."""
    # 1. Bouton Play/Pause (uniquement au clic)
    if is_click and cfg.timer_button.collidepoint(mouse_pos):
        cfg.timer_active = not cfg.timer_active
        return True

    # 2. Gestion de la barre des JOURS
    if cfg.DAY_BAR_RECT.collidepoint(mouse_pos):
        if is_click:
            cfg.day_bar_dragging = True
        if cfg.day_bar_dragging:
            x = max(cfg.DAY_BAR_RECT.x, min(mouse_pos[0], cfg.DAY_BAR_RECT.x + cfg.DAY_BAR_RECT.width))
            cfg.world_days = int(((x - cfg.DAY_BAR_RECT.x) / cfg.DAY_BAR_RECT.width) * cfg.MAX_DAYS)
            return True

    # 3. Gestion de la barre des HEURES
    if cfg.TIME_BAR_RECT.collidepoint(mouse_pos):
        if is_click:
            cfg.time_bar_dragging = True
        if cfg.time_bar_dragging:
            x = max(cfg.TIME_BAR_RECT.x, min(mouse_pos[0], cfg.TIME_BAR_RECT.x + cfg.TIME_BAR_RECT.width))
            cfg.world_hours = ((x - cfg.TIME_BAR_RECT.x) / cfg.TIME_BAR_RECT.width) * 24.0
            return True

    # Si on est en train de drag mais que la souris est sortie du Rect, on continue de mettre à jour
    if cfg.day_bar_dragging:
        x = max(cfg.DAY_BAR_RECT.x, min(mouse_pos[0], cfg.DAY_BAR_RECT.x + cfg.DAY_BAR_RECT.width))
        cfg.world_days = int(((x - cfg.DAY_BAR_RECT.x) / cfg.DAY_BAR_RECT.width) * cfg.MAX_DAYS)
        return True

    if cfg.time_bar_dragging:
        x = max(cfg.TIME_BAR_RECT.x, min(mouse_pos[0], cfg.TIME_BAR_RECT.x + cfg.TIME_BAR_RECT.width))
        cfg.world_hours = ((x - cfg.TIME_BAR_RECT.x) / cfg.TIME_BAR_RECT.width) * 24.0
        return True

    return False
import pygame
import numpy as np
import jeu.globals as G
from jeu.world.world import generate_random_world

def get_dimensions():
    scr_w, scr_h = G.screen.get_size()

    G.screen_width = float(scr_w)
    G.screen_height = float(scr_h)

    G.grid_bottom_y = scr_h - G.TOOLBAR_HEIGHT

def update_start_buttons():
    center_x = G.screen_width / 2

    btn1_rect = pygame.Rect(center_x - G.button_w / 2,
                            G.screen_height / 2 - G.button_h - 10,
                            G.button_w, G.button_h)

    btn2_rect = pygame.Rect(center_x - G.button_w / 2,
                            G.screen_height / 2 + 10,
                            G.button_w, G.button_h)

    G.START_BUTTONS = [
        {"rect": btn1_rect, "action": "NEW"},
        {"rect": btn2_rect, "action": "RANDOM"},
    ]


def toggle_fullscreen():
    if G.current_screen_flags & pygame.FULLSCREEN:
        G.current_screen_flags &= ~pygame.FULLSCREEN
        G.screen = pygame.display.set_mode((G.DEFAULT_WINDOW_WIDTH, G.DEFAULT_WINDOW_HEIGHT), G.current_screen_flags)
    else:
        G.current_screen_flags |= G.FULLSCREEN_MODE
        screen_info = pygame.display.Info()
        G.screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), G.current_screen_flags)


def handle_start_screen_click(mouse_pos):
    for btn in G.START_BUTTONS:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["action"] == "NEW":
                G.world_grid = np.zeros((G.GRID_HEIGHT, G.GRID_WIDTH), dtype=int).tolist()
                G.APP_STATE = "GAME_SCREEN"

            elif btn["action"] == "RANDOM":
                generate_random_world()
                G.APP_STATE = "GAME_SCREEN"
            return True
    return False

def draw_start_screen(screen_width, screen_height):
    G.screen.fill((20, 20, 40))

    # Title
    title_surface = G.title_font.render("Créateur de Monde Sandbox", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(screen_width / 2, screen_height / 4))
    G.screen.blit(title_surface, title_rect)

    # Draw buttons from START_BUTTONS
    for btn in G.START_BUTTONS:
        rect = btn["rect"]

        if btn["action"] == "NEW":
            color = (50, 150, 50)
            text = "Créer de zéro (Eau)"
        else:
            color = (150, 50, 50)
            text = "Monde aléatoire (Organique)"

        pygame.draw.rect(G.screen, color, rect, border_radius=10)

        text_surface = G.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        G.screen.blit(text_surface, text_rect)

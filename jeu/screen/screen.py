import pygame
import numpy as np
import jeu.globals as G

def get_dimensions():
    scr_w, scr_h = G.screen.get_size()

    G.screen_width = float(scr_w)
    G.screen_height = float(scr_h)

    G.grid_bottom_y = scr_h - G.TOOLBAR_HEIGHT


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
                G.generate_random_world()
                G.APP_STATE = "GAME_SCREEN"
            return True
    return False

def draw_start_screen(screen_width, screen_height):
    G.screen.fill((20, 20, 40))

    title_surface = G.title_font.render("Créateur de Monde Sandbox", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(int(screen_width / 2), int(screen_height / 4)))
    G.screen.blit(title_surface, title_rect)

    button_w, button_h = 300, 60
    center_x = screen_width / 2

    btn1_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 - button_h - 10, button_w, button_h)
    pygame.draw.rect(G.screen, (50, 150, 50), btn1_rect, border_radius=10)
    text1 = G.font.render("Créer de zéro (Eau)", True, (255, 255, 255))
    text1_rect = text1.get_rect(center=btn1_rect.center)
    G.screen.blit(text1, text1_rect)

    btn2_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 + 10, button_w, button_h)
    pygame.draw.rect(G.screen, (150, 50, 50), btn2_rect, border_radius=10)
    text2 = G.font.render("Monde aléatoire (Organique)", True, (255, 255, 255))
    text2_rect = text2.get_rect(center=btn2_rect.center)
    G.screen.blit(text2, text2_rect)

    global START_BUTTONS
    START_BUTTONS = [
        {"rect": btn1_rect, "action": "NEW"},
        {"rect": btn2_rect, "action": "RANDOM"}
    ]

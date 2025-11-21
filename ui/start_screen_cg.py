import pygame
import numpy as np

def draw_start_screen(screen, screen_width, screen_height, font, title_font):
    screen.fill((20, 20, 40))

    title_surface = title_font.render("Créateur de Monde Sandbox", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_surface, title_rect)

    button_w, button_h = 300, 60
    center_x = screen_width // 2

    btn1_rect = pygame.Rect(center_x - button_w // 2, screen_height // 2 - button_h - 10, button_w, button_h)
    pygame.draw.rect(screen, (50, 150, 50), btn1_rect, border_radius=10)
    text1 = font.render("Créer de zéro (Eau)", True, (255, 255, 255))
    screen.blit(text1, text1.get_rect(center=btn1_rect.center))

    btn2_rect = pygame.Rect(center_x - button_w // 2, screen_height // 2 + 10, button_w, button_h)
    pygame.draw.rect(screen, (150, 50, 50), btn2_rect, border_radius=10)
    text2 = font.render("Monde aléatoire (Organique)", True, (255, 255, 255))
    screen.blit(text2, text2.get_rect(center=btn2_rect.center))

    return [
        {"rect": btn1_rect, "action": "NEW"},
        {"rect": btn2_rect, "action": "RANDOM"}
    ]


def handle_start_screen_click(mouse_pos, buttons, world_grid, grid_w, grid_h, generate_random_world):
    for btn in buttons:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["action"] == "NEW":
                world_grid[:] = np.zeros((grid_h, grid_w), dtype=int).tolist()
                return "GAME_SCREEN"

            elif btn["action"] == "RANDOM":
                generate_random_world()
                return "GAME_SCREEN"

    return None

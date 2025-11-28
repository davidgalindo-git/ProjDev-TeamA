import pygame
from world.state import APP_STATE

def draw_start_screen(screen):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)

    title = font.render("Python World Generator", True, (255, 255, 255))
    start_msg = small_font.render("Click anywhere to start", True, (200, 200, 200))

    screen.blit(title, (200, 150))
    screen.blit(start_msg, (220, 250))


def handle_start_screen_click():
    from world.state import set_app_state
    set_app_state("RUNNING")

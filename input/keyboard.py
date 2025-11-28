import pygame
from world.state import state

def handle_keyboard_event(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F11:
            # signal main to toggle fullscreen
            state["toggle_fullscreen"] = True
        if event.key == pygame.K_ESCAPE:
            state["quit"] = True

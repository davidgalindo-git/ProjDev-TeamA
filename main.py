import pygame, sys, os
from settings import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, TOOLBAR_HEIGHT, APP_START, APP_GAME, COLORS
from world.generator import generate_random_world
from world.renderer import draw_world, update_terrain_images
from ui.toolbar import draw_toolbar, handle_toolbar_click
from ui.minimap import draw_minimap
from ui.start_screen import draw_start_screen, handle_start_screen_click
from input.mouse import handle_mouse_event
from input.keyboard import handle_keyboard_event
from world.state import state, world_grid

# ---- init pygame ----
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")
screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT))
clock = pygame.time.Clock()

# load assets
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
TERRAIN_IMAGES_RAW = {}
try:
    TERRAIN_IMAGES_RAW = {
        0: pygame.image.load(os.path.join(ASSET_DIR, "water.png")).convert_alpha(),
        1: pygame.image.load(os.path.join(ASSET_DIR, "grass.png")).convert_alpha(),
        2: pygame.image.load(os.path.join(ASSET_DIR, "dirt.png")).convert_alpha(),
        3: pygame.image.load(os.path.join(ASSET_DIR, "sand.png")).convert_alpha(),
        4: pygame.image.load(os.path.join(ASSET_DIR, "stone.png")).convert_alpha(),
    }
except Exception as e:
    print("Warning: could not load some assets:", e)

# terrain images scaled cache
TERRAIN_IMAGES = update_terrain_images(TERRAIN_IMAGES_RAW, state["tile_size"])

# generate initial world
generate_random_world()
state["app_state"] = APP_GAME

# fullscreen state
current_screen_flags = 0
FULLSCREEN_MODE = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF

def toggle_fullscreen():
    global screen, current_screen_flags
    if current_screen_flags & pygame.FULLSCREEN:
        current_screen_flags &= ~pygame.FULLSCREEN
        screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)
    else:
        current_screen_flags |= FULLSCREEN_MODE
        screen_info = pygame.display.Info()
        screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), current_screen_flags)

running = True
while running:
    scr_w, scr_h = screen.get_size()
    grid_bottom_y = scr_h - TOOLBAR_HEIGHT

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # keyboard
        handle_keyboard_event(event)
        if state.get("quit"):
            running = False
        if state.get("toggle_fullscreen"):
            toggle_fullscreen()
            state["toggle_fullscreen"] = False

        # start screen handling
        if state["app_state"] == APP_START:
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_start_screen_click()
            continue

        # toolbar click area
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if my >= grid_bottom_y:
                if handle_toolbar_click((mx,my), scr_w, grid_bottom_y):
                    # toolbar clicked and handled
                    pass
                else:
                    # could add more toolbar interactions
                    pass
            else:
                # world interactions (drawing, panning, zoom)
                handle_mouse_event(event, scr_w, grid_bottom_y)
        else:
            # mouse motion / up events also processed by handler
            handle_mouse_event(event, scr_w, grid_bottom_y)

    # update scaled images if tile size changed
    TERRAIN_IMAGES = update_terrain_images(TERRAIN_IMAGES_RAW, state["tile_size"])

    # draw
    screen.fill((0,0,0))
    if state["app_state"] == APP_START:
        draw_start_screen(screen)
    else:
        draw_world(screen, TERRAIN_IMAGES)
        draw_toolbar(screen, scr_w, grid_bottom_y)
        draw_minimap(screen, scr_w, grid_bottom_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

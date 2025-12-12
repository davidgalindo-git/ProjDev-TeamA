import pygame
import sys
import numpy as np

# --- Imports des modules refactorisés ---
# Note: Renommer world_state_cg.py en world_manager.py est recommandé
from config_cg import *
from world.world_state_cg import World
from world.generation_cg import generate_random_world
from jeu.world.draw_world import draw_world
from rendering.draw_element_cg import draw_elements
from jeu.toolbar_cg import draw_toolbar, handle_toolbar_click
from ui.minimap_cg import draw_minimap, handle_minimap_drag, handle_minimap_click


# ---------------------------------------

# --- 1. CONFIGURATION ET INITIALISATION ---

# Variables globales minimales
APP_STATE = "START_SCREEN"
FULLSCREEN_MODE = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
current_screen_flags = 0
START_BUTTONS = []

# Variables d'état d'interaction
is_panning = False
last_mouse_pos = (0, 0)
is_drawing = False
minimap_dragging = False
minimap_drag_offset = (0, 0)
scroll_offset = 0.0

# Initialisation Pygame
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")
screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)
clock = pygame.time.Clock()

# Chargement des ressources (à mettre dans un module loader_cg.py)
# Pour l'instant, on laisse le chargement ici car vous n'avez pas envoyé loader_cg.py
try:
    TERRAIN_IMAGES_RAW = {
        0: pygame.image.load("assets/water.png").convert_alpha(),
        1: pygame.image.load("assets/grass.png").convert_alpha(),
        2: pygame.image.load("assets/dirt.png").convert_alpha(),
        3: pygame.image.load("assets/sand.png").convert_alpha(),
        4: pygame.image.load("assets/stone.png").convert_alpha(),
        5: pygame.image.load("assets/S_rock1.png").convert_alpha(),
        6: pygame.image.load("assets/B_rock.png").convert_alpha(),
    }
except pygame.error as e:
    print(f"Erreur de chargement d'image. Vérifiez 'assets/'. Erreur: {e}")
    sys.exit()

# État du monde et de la caméra
world = World()
TERRAIN_IMAGES = {}  # Cache des images redimensionnées

# Fonts (pour start screen / ui)
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 48)
label_font = pygame.font.SysFont("comicsans", 15)


# --- 2. FONCTIONS DE TRANSITION ET D'UTILITAIRES ---

def get_dimensions():
    """Retourne la largeur, hauteur et la limite Y de la grille de jeu."""
    scr_w, scr_h = screen.get_size()
    grid_bottom_y = scr_h - TOOLBAR_HEIGHT
    return float(scr_w), float(scr_h), float(grid_bottom_y)


def toggle_fullscreen():
    """Bascule entre mode fenêtre et plein écran."""
    global screen, current_screen_flags

    if current_screen_flags & pygame.FULLSCREEN:
        current_screen_flags &= ~pygame.FULLSCREEN
        screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)
    else:
        current_screen_flags |= FULLSCREEN_MODE
        screen_info = pygame.display.Info()
        screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), current_screen_flags)


def handle_new_game():
    """Initialise le monde avec de l'eau."""
    world.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int).tolist()
    world.element_grid = np.zeros((ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int).tolist()
    world.reset_camera()


def handle_random_game():
    """Initialise le monde avec de la génération aléatoire."""
    world.grid = generate_random_world()
    world.element_grid = np.zeros((ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int).tolist()
    world.reset_camera()


# --- 3. ÉCRAN DE DÉMARRAGE (Logique essentielle ici) ---

def draw_start_screen(screen_width, screen_height):
    """Dessine l'écran de démarrage et définit les zones cliquables."""
    screen.fill((20, 20, 40))

    title_surface = title_font.render("Créateur de Monde Sandbox", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(int(screen_width / 2), int(screen_height / 4)))
    screen.blit(title_surface, title_rect)

    button_w, button_h = 300, 60
    center_x = screen_width / 2

    btn1_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 - button_h - 10, button_w, button_h)
    pygame.draw.rect(screen, (50, 150, 50), btn1_rect, border_radius=10)
    text1 = font.render("Créer de zéro (Eau)", True, (255, 255, 255))
    screen.blit(text1, text1.get_rect(center=btn1_rect.center))

    btn2_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 + 10, button_w, button_h)
    pygame.draw.rect(screen, (150, 50, 50), btn2_rect, border_radius=10)
    text2 = font.render("Monde aléatoire (Organique)", True, (255, 255, 255))
    screen.blit(text2, text2.get_rect(center=btn2_rect.center))

    global START_BUTTONS
    START_BUTTONS = [
        {"rect": btn1_rect, "action": "NEW"},
        {"rect": btn2_rect, "action": "RANDOM"}
    ]


def handle_start_screen_click(mouse_pos):
    global scroll_offset
    """Gère le clic sur l'écran de démarrage pour changer d'état."""
    global APP_STATE

    for btn in START_BUTTONS:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["action"] == "NEW":
                handle_new_game()
                APP_STATE = "GAME_SCREEN"

            elif btn["action"] == "RANDOM":
                handle_random_game()
                APP_STATE = "GAME_SCREEN"
            return True
    return False


# --- 4. BOUCLE PRINCIPALE ---

running = True
while running:
    screen_width, screen_height, grid_bottom_y = get_dimensions()

    # **********************************************
    # *** 1. GESTION DES ÉVÉNEMENTS ***
    # **********************************************
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if APP_STATE == "START_SCREEN":
                handle_start_screen_click(mouse_pos)
                continue

            # --- Dans l'écran de jeu ---
            if APP_STATE == "GAME_SCREEN":
                # 1. Priorité : Minimap
                result = handle_minimap_click(mouse_pos, world, screen_width, grid_bottom_y)
                if result:
                    is_drawing = False
                    is_panning = False
                    continue

                # 2. Zoom (Molette)
                if event.button == 4:
                    world.zoom_in()
                    continue

                elif event.button == 5:
                    world.zoom_out()
                    continue

                # 3. Clic Gauche (Dessin/UI)
                elif event.button == 1:
                    # Clic sur la barre d'outils?
                    scroll_offset, world.current_terrain, world.current_brush_size, clicked = \
                        handle_toolbar_click(mouse_pos, scroll_offset)
                    if clicked:
                        is_drawing = False
                        continue

                    # Clic sur la grille?
                    elif mouse_pos[1] < grid_bottom_y:
                        world_x = mouse_pos[0] + world.camera_x
                        world_y = mouse_pos[1] + world.camera_y

                        if world.current_terrain < 5:  # Terrain 16x16 (Dessin continu)
                            is_drawing = True
                        elif world.current_terrain >= 5:  # Élément (Clic unique)
                            world.place_element(world_x, world_y, world.current_terrain)
                            is_drawing = False  # Élément = pas de dessin continu


                # 4. Clic Droit (Déplacement ou Effacement)
                elif event.button == 3:
                    world_x = mouse_pos[0] + world.camera_x
                    world_y = mouse_pos[1] + world.camera_y

                    # Tenter l'effacement d'élément
                    if world.current_terrain >= 5 and mouse_pos[1] < grid_bottom_y:
                        if world.erase_element(world_x, world_y):
                            continue  # Élément effacé, ne pas activer le Panning

                    # Sinon, activer le Panning
                    is_panning = True
                    last_mouse_pos = mouse_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            minimap_dragging = False
            if event.button == 1:
                is_drawing = False
            elif event.button == 3:
                is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            if APP_STATE == "GAME_SCREEN":
                # Priorité : Drag de la minimap
                if minimap_dragging:
                    world.camera_x, world.camera_y = handle_minimap_drag(mouse_pos, minimap_drag_offset, world,
                                                                         screen_width, grid_bottom_y)
                    continue

                # Panning clic droit
                if is_panning:
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    dy = mouse_pos[1] - last_mouse_pos[1]
                    world.camera_x -= dx
                    world.camera_y -= dy
                    last_mouse_pos = mouse_pos

                # Dessin continu (Terrain 16x16)
                elif is_drawing and world.current_terrain < 5 and mouse_pos[1] < grid_bottom_y:
                    world_x = mouse_pos[0] + world.camera_x
                    world_y = mouse_pos[1] + world.camera_y
                    grid_row, grid_col = world.world_to_grid_16x16(world_x, world_y)

                    if 0 <= grid_col < GRID_WIDTH and 0 <= grid_row < GRID_HEIGHT:
                        world.paint_terrain(grid_row, grid_col, world.current_terrain)

    # **********************************************
    # *** 2. LOGIQUE D'AFFICHAGE ***
    # **********************************************
    screen.fill((0, 0, 0))

    if APP_STATE == "START_SCREEN":
        draw_start_screen(screen_width, screen_height)

    elif APP_STATE == "GAME_SCREEN":

        # Ajuster la caméra et le zoom (important avant de dessiner)
        world.adjust_camera(screen_width, grid_bottom_y)

        # 1. Dessiner le monde (Terrain 16x16)
        draw_world(screen, world, TERRAIN_IMAGES_RAW, TERRAIN_IMAGES, screen_width, grid_bottom_y)

        # 2. Dessiner les éléments 8x8 et 32x32
        draw_elements(screen, world, TERRAIN_IMAGES_RAW)

        # 3. Dessiner l'ui
        draw_toolbar(screen, world, scroll_offset, screen_width, grid_bottom_y, label_font)
        draw_minimap(screen, world, screen_width, grid_bottom_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
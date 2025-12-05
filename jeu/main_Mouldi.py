# Fichier : jeu/main_Mouldi.py (CORRECTION INTÉGRALE)

import pygame
import sys
import numpy as np

# --- 1. Imports corrigés (Style absolu/direct) ---
# NOTE: Si ces imports échouent encore (ModuleNotFoundError), vous devrez ajouter la racine du projet
# au sys.path de Python (via main.py ou votre IDE) pour qu'il trouve les dossiers.
from config_cg import *
from worldManagement import World
from imageLoader import load_all_assets, update_terrain_images  # Ajout de load/update ici

# Modules dont vous n'avez pas fourni le code (les imports circulent toujours si vous les importez)
from world.generation_cg import generate_random_world
from rendering.draw_world_cg import draw_world
from rendering.draw_element_cg import draw_elements
from ui.toolbar_cg import draw_toolbar, handle_toolbar_click
from ui.minimap_cg import draw_minimap, handle_minimap_drag, handle_minimap_click

# --- 2. Variables Globales et Initialisation ---
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")
clock = pygame.time.Clock()

# A. État du Jeu
APP_STATE = "START_SCREEN"
FULLSCREEN_MODE = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
current_screen_flags = 0
START_BUTTONS = []

# B. Monde et Assets
world = World()
TERRAIN_IMAGES_RAW = load_all_assets()  # Appel de la fonction corrigée
TERRAIN_IMAGES = {}  # Cache des images redimensionnées

# C. Interactions
is_panning = False
last_mouse_pos = (0, 0)
is_drawing = False
minimap_dragging = False
minimap_drag_offset = (0, 0)
scroll_offset = 0.0  # Décalage horizontal de la barre d'outils

# D. Pygame Affichage
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 48)
label_font = pygame.font.SysFont("comicsans", 15)
screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)


# --- 3. Fonctions Utilitaires et Écran de Démarrage (Inchagées) ---

def get_dimensions():
    """Retourne la largeur, hauteur et la limite Y de la grille de jeu."""
    scr_w, scr_h = screen.get_size()
    grid_bottom_y = scr_h - TOOLBAR_HEIGHT
    return float(scr_w), float(scr_h), float(grid_bottom_y)


# ... (toggle_fullscreen, handle_new_game, handle_random_game, draw_start_screen, handle_start_screen_click sont inchangées) ...


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
    """Initialise le monde avec de la génération aléatoire (nécessite generation_cg.py)."""
    world.grid = generate_random_world()
    world.element_grid = np.zeros((ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int).tolist()
    world.reset_camera()


def draw_start_screen(screen_width, screen_height):
    """Dessine l'écran de démarrage et définit les zones cliquables."""
    screen.fill((20, 20, 40))
    title_surface = title_font.render("Créateur de Monde Sandbox", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(int(screen_width / 2), int(screen_height / 4)))
    screen.blit(title_surface, title_rect)
    # Définition des boutons (Reste ici car utilise les globales font et title_font)
    button_w, button_h = 300, 60
    center_x = screen_width / 2
    btn1_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 - button_h - 10, button_w, button_h)
    btn2_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 + 10, button_w, button_h)
    pygame.draw.rect(screen, (50, 150, 50), btn1_rect, border_radius=10)
    text1 = font.render("Créer de zéro (Eau)", True, (255, 255, 255))
    screen.blit(text1, text1.get_rect(center=btn1_rect.center))
    pygame.draw.rect(screen, (150, 50, 50), btn2_rect, border_radius=10)
    text2 = font.render("Monde aléatoire (Organique)", True, (255, 255, 255))
    screen.blit(text2, text2.get_rect(center=btn2_rect.center))
    global START_BUTTONS
    START_BUTTONS = [
        {"rect": btn1_rect, "action": "NEW"},
        {"rect": btn2_rect, "action": "RANDOM"}
    ]


def handle_start_screen_click(mouse_pos):
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


# --- 4. Boucle de Jeu Principale ---

def run_game_loop():
    """Contient la boucle principale du jeu Pygame."""
    global running, APP_STATE, is_panning, last_mouse_pos, is_drawing, minimap_dragging, scroll_offset

    running = True
    while running:
        screen_width, screen_height, grid_bottom_y = get_dimensions()

        # **********************************************
        # *** GESTION DES ÉVÉNEMENTS ***
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
                    # On assume que handle_minimap_click utilise les globales ou la même structure que la toolbar
                    if handle_minimap_click(mouse_pos, world, minimap_dragging, minimap_drag_offset, get_dimensions):
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
                        new_scroll_offset, clicked = handle_toolbar_click(
                            mouse_pos, world, scroll_offset, get_dimensions)
                        scroll_offset = new_scroll_offset  # MISE À JOUR DE LA GLOBALE

                        if clicked:
                            is_drawing = False
                            continue

                        # Clic sur la grille?
                        elif mouse_pos[1] < grid_bottom_y:
                            world_x = mouse_pos[0] + world.camera_x
                            world_y = mouse_pos[1] + world.camera_y

                            if world.current_terrain < 5:
                                is_drawing = True
                            elif world.current_terrain >= 5:
                                world.place_element(world_x, world_y, world.current_terrain)
                                is_drawing = False

                    # 4. Clic Droit (Déplacement ou Effacement)
                    elif event.button == 3:
                        world_x = mouse_pos[0] + world.camera_x
                        world_y = mouse_pos[1] + world.camera_y
                        if world.current_terrain >= 5 and mouse_pos[1] < grid_bottom_y:
                            if world.erase_element(world_x, world_y):
                                continue
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
                    # On assume que handle_minimap_drag modifie world.camera_x/y directement.
                    if minimap_dragging:
                        handle_minimap_drag(mouse_pos, world, minimap_drag_offset)
                        continue

                    # Panning clic droit
                    if is_panning:
                        dx = mouse_pos[0] - last_mouse_pos[0]
                        dy = mouse_pos[1] - last_mouse_pos[1]
                        world.camera_x -= dx
                        world.camera_y -= dy
                        last_mouse_pos = mouse_pos

                    # Dessin continu (Clic gauche sur la grille)
                    elif is_drawing and world.current_terrain < 5 and mouse_pos[1] < grid_bottom_y:
                        world_x = mouse_pos[0] + world.camera_x
                        world_y = mouse_pos[1] + world.camera_y
                        grid_row, grid_col = world.world_to_grid_16x16(world_x, world_y)

                        if 0 <= grid_col < GRID_WIDTH and 0 <= grid_row < GRID_HEIGHT:
                            world.paint_terrain(grid_row, grid_col, world.current_terrain)

        # **********************************************
        # *** LOGIQUE D'AFFICHAGE ***
        # **********************************************
        screen.fill((0, 0, 0))

        if APP_STATE == "START_SCREEN":
            draw_start_screen(screen_width, screen_height)

        elif APP_STATE == "GAME_SCREEN":

            # Mise à jour et ajustement avant le rendu
            world.adjust_camera(screen_width, grid_bottom_y)
            # APPEL CORRIGÉ
            update_terrain_images(TERRAIN_IMAGES, TERRAIN_IMAGES_RAW, world.tile_size)

            # Rendu :
            # Les fonctions de rendu (draw_world, draw_elements) doivent accepter leurs dépendances en argument
            # Si ces fonctions ne sont pas corrigées, elles échoueront ici.
            draw_world(screen, world, TERRAIN_IMAGES, screen_width, grid_bottom_y)
            draw_elements(screen, world, TERRAIN_IMAGES_RAW)

            # APPEL CORRIGÉ
            draw_toolbar(screen, world, scroll_offset, get_dimensions, label_font)
            draw_minimap(screen, world, screen_width, grid_bottom_y)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
import pygame
import sys
import random
import math
import numpy as np
import globals as G
from opensimplex import OpenSimplex
from assets import *
from ui.minimap.minimap import draw_minimap, handle_minimap_click, handle_minimap_drag
from ui.timer.timer import timer, draw_timer, update_time_from_bar, update_day_from_bar, handle_day_bar_click
from ui.toolbar.toolbar import handle_toolbar_click, draw_toolbar
from todo import get_dimensions

# 1. Initialiser Pygame une seule fois
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")

# 3. Charger les images (Maintenant que le mode vidéo est défini)
try:
    # J'ai rétabli l'usage des G.COLORS pour la barre d'outils, car TERRAIN_IMAGES_RAW contient des surfaces.
    # L'erreur de draw_toolbar qui attend une couleur sera corrigée plus bas.
    TERRAIN_IMAGES_RAW = {
        0: pygame.image.load("../assets/water.png").convert_alpha(),
        1: pygame.image.load("../assets/grass.png").convert_alpha(),
        2: pygame.image.load("../assets/dirt.png").convert_alpha(),
        3: pygame.image.load("../assets/sand.png").convert_alpha(),
        4: pygame.image.load("../assets/stone.png").convert_alpha(),
    }
    # J'ai retiré les types 4 (stone/dirt) car ils n'étaient pas définis dans le G.COLORS ni dans TOOLBAR_BUTTONS.
    # Si vous voulez les utiliser, vous devez mettre à jour G.COLORS et TOOLBAR_BUTTONS.
except pygame.error as e:
    print(
        f"Erreur de chargement d'image : Vérifiez l'existence des fichiers dans 'assets/'. Erreur: {e}")
    sys.exit()

def toggle_fullscreen():
    """Bascule entre mode fenêtre (taille par défaut) et plein écran."""
    if G.current_screen_flags & pygame.FULLSCREEN:
        G.current_screen_flags &= ~pygame.FULLSCREEN
        G.screen = pygame.display.set_mode((G.DEFAULT_WINDOW_WIDTH, G.DEFAULT_WINDOW_HEIGHT), G.current_screen_flags)
    else:
        G.current_screen_flags |= G.FULLSCREEN_MODE
        screen_info = pygame.display.Info()
        G.screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), G.current_screen_flags)


def generate_random_world():
    """Génère un monde aléatoire avec Simplex Noise pour des formes naturelles et biomes mélangés."""

    # Réinitialisation de la caméra et du zoom
    G.TILE_SIZE = G.INIT_TILE_SIZE
    camera_x = 0.0
    camera_y = 0.0

    # Paramètres de bruit aléatoires pour la HAUTEUR et la forme de l'île
    seed_height = random.randint(0, 100000)
    simplex_height = OpenSimplex(seed=seed_height)

    # Scale très aléatoire pour garantir des formes d'îles très différentes
    SCALE_HEIGHT = random.uniform(8.0, 20.0)
    OFFSET_X = random.uniform(0.0, 1000.0)
    OFFSET_Y = random.uniform(0.0, 1000.0)

    CENTER_X = G.GRID_WIDTH / 2.0
    CENTER_Y = G.GRID_HEIGHT / 2.0

    # Le rayon peut être plus grand ou plus petit pour créer des continents ou des archipels
    MAX_RADIUS = random.uniform(G.GRID_WIDTH / 3.0, G.GRID_WIDTH / 2.0)

    # Seuils aléatoires pour plus de variété
    MOUNTAIN_THRESHOLD = random.uniform(0.65, 0.85)
    LAND_THRESHOLD = random.uniform(0.3, 0.4)

    # 1. GÉNÉRATION DE LA CARTE DE HAUTEUR
    height_map = np.zeros((G.GRID_HEIGHT, G.GRID_WIDTH), dtype=float)

    for r in range(G.GRID_HEIGHT):
        for c in range(G.GRID_WIDTH):
            # 1a. Bruit de Hauteur (Détermine si c'est de l'eau, terre ou montagne)
            noise_val_h = simplex_height.noise2(x=(c + OFFSET_X) / SCALE_HEIGHT, y=(r + OFFSET_Y) / SCALE_HEIGHT)
            normalized_noise_h = (noise_val_h + 1.0) / 2.0

            # Déformation du centre : force les bords à être de l'eau
            dist_to_center = math.sqrt((c - CENTER_X) ** 2 + (r - CENTER_Y) ** 2)
            edge_falloff = 1.0 - (dist_to_center / MAX_RADIUS) ** 2

            final_height = normalized_noise_h * max(0, edge_falloff)
            height_map[r, c] = final_height

    # 2. APPLICATION DES SEUILS ET CRÉATION DE LA GRILLE
    new_grid = np.zeros((G.GRID_HEIGHT, G.GRID_WIDTH), dtype=int)

    # Remplissage par défaut : Herbe (Type 1) pour les terres moyennes
    new_grid[(height_map > LAND_THRESHOLD)] = 1

    # Application de la Montagne/Terre Rugueuse (Type 2) sur les hauteurs
    new_grid[(height_map > MOUNTAIN_THRESHOLD)] = 2

    # Le reste est de l'eau (Type 0 par défaut de new_grid)

    # 3. POST-PROCESSUS: CRÉATION DES PLAGES DE SABLE
    final_grid = new_grid.copy()

    for r in range(G.GRID_HEIGHT):
        for c in range(G.GRID_WIDTH):
            if final_grid[r, c] == 1 or final_grid[r, c] == 2:  # Si c'est Herbe ou Montagne/Terre
                is_coastal = False

                # Vérifier si un voisin (y compris les diagonales) est de l'eau (0)
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue

                        nr, nc = r + dr, c + dc

                        if 0 <= nr < G.GRID_HEIGHT and 0 <= nc < G.GRID_WIDTH:
                            if new_grid[nr, nc] == 0:
                                is_coastal = True
                                break
                    if is_coastal: break

                # Règle : Les tuiles Herbe ou Montagne adjacentes à l'eau deviennent du sable (3).
                if is_coastal:
                    final_grid[r, c] = 3

    world_grid = final_grid.tolist()

# --- Fonction de mise à jour des images redimensionnées (INCHANGÉE) ---
def update_terrain_images():
    """Redimensionne toutes les textures pour correspondre à la G.TILE_SIZE actuelle."""
    global TERRAIN_IMAGES

    # Vérifie si le redimensionnement est nécessaire (taille non définie ou différente)
    current_size = TERRAIN_IMAGES.get(0).get_size()[0] if 0 in TERRAIN_IMAGES else -1

    if current_size != int(G.TILE_SIZE) and TERRAIN_IMAGES_RAW:  # Ajout de la vérification TERRAIN_IMAGES_RAW
        new_images = {}
        for terrain_type, raw_img in TERRAIN_IMAGES_RAW.items():
            # Redimensionne l'image brute à la G.TILE_SIZE actuelle
            new_images[terrain_type] = pygame.transform.scale(
                raw_img, (int(G.TILE_SIZE), int(G.TILE_SIZE))
            )
        TERRAIN_IMAGES = new_images


def draw_world(screen_width, grid_bottom_y):
    """Dessine la grille visible en utilisant les images redimensionnées (INCHANGÉE)."""
    global camera_x, camera_y

    # Correction du Dézoom / Bande Noire (INCHANGÉ)
    #G.min_tile_size_x
    #G.min_tile_size_y

    G.TILE_SIZE = max(G.TILE_SIZE, min(G.min_tile_size_x, G.min_tile_size_y))

    # Correction de la position de la Caméra (INCHANGÉ)
    max_camera_x = max(0.0, G.GRID_WIDTH * G.TILE_SIZE - screen_width)
    max_camera_y = max(0.0, G.GRID_HEIGHT * G.TILE_SIZE - grid_bottom_y)

    camera_x = max(0.0, min(camera_x, max_camera_x))
    camera_y = max(0.0, min(camera_y, max_camera_y))

    # Redimensionner les images pour la G.TILE_SIZE actuelle
    update_terrain_images()

    # Dessin des tuiles visibles
    start_col = max(0, int(camera_x // G.TILE_SIZE))
    end_col = min(G.GRID_WIDTH, int((camera_x + screen_width) // G.TILE_SIZE + 1))
    start_row = max(0, int(camera_y // G.TILE_SIZE))
    end_row = min(G.GRID_HEIGHT, int((camera_y + grid_bottom_y) // G.TILE_SIZE + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            terrain_type = G.world_grid[row][col]

            # Utiliser l'image redimensionnée
            image_to_draw = TERRAIN_IMAGES.get(terrain_type)

            if image_to_draw:
                screen_x = col * G.TILE_SIZE - camera_x
                screen_y = row * G.TILE_SIZE - camera_y

                # Dessin de l'image (texture)
                G.screen.blit(image_to_draw, (screen_x, screen_y))


# --- 5. GESTION DE L'ÉCRAN DE DÉMARRAGE (INCHANGÉE) ---

START_BUTTONS = []


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


def handle_start_screen_click(mouse_pos):
    for btn in START_BUTTONS:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["action"] == "NEW":
                G.world_grid = np.zeros((G.GRID_HEIGHT, G.GRID_WIDTH), dtype=int).tolist()
                G.APP_STATE = "GAME_SCREEN"

            elif btn["action"] == "RANDOM":
                generate_random_world()
                G.APP_STATE = "GAME_SCREEN"
            return True
    return False


while G.running:
    get_dimensions()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            G.running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if G.timer_button.collidepoint(event.pos):
                G.timer_active = not G.timer_active # toggle

            if G.TIME_BAR_RECT.collidepoint(event.pos):
                G.time_bar_dragging = True
                G.timer_active = False  # pause time while scrubbing
                # immediately set time based on click
                rel_x = (event.pos[0] - G.TIME_BAR_RECT.x) / G.TIME_BAR_RECT.width
                G.world_hours = rel_x * 24

            handle_day_bar_click(event.pos)

            # --- Priorité : clic sur la minimap ---
            if G.APP_STATE == "GAME_SCREEN":
                if handle_minimap_click(mouse_pos, G.screen_width, G.grid_bottom_y):
                    # On empêche le reste du code de traiter ce clic
                    G.is_drawing = False
                    G.is_panning = False
                    continue

            if G.APP_STATE == "START_SCREEN":
                handle_start_screen_click(mouse_pos)

            elif G.APP_STATE == "GAME_SCREEN":
                if event.button == 1:  # Clic Gauche (Dessin/ui)
                    if handle_toolbar_click(mouse_pos, G.screen_width, G.grid_bottom_y):
                        G.is_drawing = False
                    elif mouse_pos[1] < G.grid_bottom_y:
                        G.is_drawing = True

                elif event.button == 3:  # Clic Droit (Déplacement)
                    G.is_panning = True
                    last_mouse_pos = mouse_pos

                elif event.button == 4:  # Molette haut (Zoom in)
                    TILE_SIZE = min(64.0, TILE_SIZE + 2.0)

                elif event.button == 5:  # Molette bas (Zoom out)
                    TILE_SIZE = max(4.0, TILE_SIZE - 2.0)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                G.is_drawing = False
                G.is_dragging = False
                G.time_bar_dragging = False
                G.day_bar_dragging = False
                G.minimap_dragging = False
            elif event.button == 3:
                G.is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if G.time_bar_dragging:
                update_time_from_bar(event.pos)
            if G.day_bar_dragging:
                update_day_from_bar(event.pos)

            # Priorité : si on est en train de drag la minimap → ignorer le reste
            if G.APP_STATE == "GAME_SCREEN" and G.minimap_dragging:
                handle_minimap_drag(mouse_pos, G.screen_width, G.grid_bottom_y)
                continue

            # Panning clic droit
            if G.APP_STATE == "GAME_SCREEN" and G.is_panning:
                dx = mouse_pos[0] - last_mouse_pos[0]
                dy = mouse_pos[1] - last_mouse_pos[1]
                G.camera_x -= dx
                G.camera_y -= dy
                last_mouse_pos = mouse_pos

    # --- LOGIQUE D'AFFICHAGE ---
    G.screen.fill((0, 0, 0))

    if G.APP_STATE == "START_SCREEN":
        draw_start_screen(G.screen_width, G.screen_height)

    elif G.APP_STATE == "GAME_SCREEN":
        # 1. Dessiner le monde (maintenant avec des images) et démarrer timer
        draw_world(G.screen_width, G.grid_bottom_y)

        # 2. Application du Pinceau (Dessin)
        if G.is_drawing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < G.grid_bottom_y:
                world_x = mouse_x + G.camera_x
                world_y = mouse_y + G.camera_y

                grid_col = int(world_x // TILE_SIZE)
                grid_row = int(world_y // TILE_SIZE)

                if 0 <= grid_col < G.GRID_WIDTH and 0 <= grid_row < G.GRID_HEIGHT:
                    # compute offsets so that we paint an exact CURRENT_BRUSH x CURRENT_BRUSH square
                    N = int(G.CURRENT_BRUSH)
                    start_offset = -(N // 2)
                    # For even sizes this centers slightly up-left which is expected; you can change anchor if you want top-left.
                    for dr in range(start_offset, start_offset + N):
                        for dc in range(start_offset, start_offset + N):
                            r = grid_row + dr
                            c = grid_col + dc
                            if 0 <= r < G.GRID_HEIGHT and 0 <= c < G.GRID_WIDTH:
                                G.world_grid[r][c] = G.CURRENT_TERRAIN
        if G.timer_active:
            G.world_hours, G.world_days, G.display_hours, G.world_minutes = timer(G.world_hours, G.world_days)

        # 3. Dessiner l'ui
        draw_toolbar(G.screen_width, G.grid_bottom_y)
        draw_minimap(G.screen_width, G.grid_bottom_y)
        draw_timer(G.world_days)

    pygame.display.flip()
    G.clock.tick(60)

pygame.quit()
sys.exit()
import pygame
import sys
import random
import math
import numpy as np
from opensimplex import OpenSimplex
from Assets import *  # Assurez-vous que ce dossier existe et contient les images

# --- 1. CONFIGURATION STATIQUE ---
INIT_TILE_SIZE = 16.0
GRID_WIDTH = 100
GRID_HEIGHT = 80

TOOLBAR_HEIGHT = 60
SCROLL_BUTTON_WIDTH = 50

# Dimensions de la fenêtre par défaut
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700

# Couleurs pour les types de terrain (MAINTENU UNIQUEMENT POUR L'AFFICHAGE DE L'UI)
COLORS = {
    0: (0, 0, 200),  # Eau
    1: (0, 150, 0),  # Herbe
    2: (150, 75, 0),  # Montagne
    3: (240, 230, 140),  # Sable
}

TERRAIN_IMAGES_RAW = {}
TERRAIN_IMAGES = {}

# --- 2. INITIALISATION PYGAME ET AFFICHAGE (NOUVEL ORDRE) ---

# 1. Initialiser Pygame une seule fois
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")

# 2. Définir le mode vidéo (création de l'écran)
FULLSCREEN_MODE = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
current_screen_flags = 0

# C'est cette ligne qui définit le mode vidéo et permet le convert_alpha()
screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)

# 3. Charger les images (Maintenant que le mode vidéo est défini)
try:
    # J'ai rétabli l'usage des COLORS pour la barre d'outils, car TERRAIN_IMAGES_RAW contient des surfaces.
    # L'erreur de draw_toolbar qui attend une couleur sera corrigée plus bas.
    TERRAIN_IMAGES_RAW = {
        0: pygame.image.load("Assets/water.png").convert_alpha(),
        1: pygame.image.load("Assets/grass.png").convert_alpha(),
        2: pygame.image.load("Assets/dirt.png").convert_alpha(),
        3: pygame.image.load("Assets/sand.png").convert_alpha(),
        4: pygame.image.load("Assets/stone.png").convert_alpha(),
    }
    # J'ai retiré les types 4 (stone/dirt) car ils n'étaient pas définis dans le COLORS ni dans TOOLBAR_BUTTONS.
    # Si vous voulez les utiliser, vous devez mettre à jour COLORS et TOOLBAR_BUTTONS.
except pygame.error as e:
    print(
        f"Erreur de chargement d'image : Vérifiez l'existence des fichiers dans 'Assets/'. Erreur: {e}")
    sys.exit()

# --- FIN DE L'INITIALISATION RÉORGANISÉE ---


# Définition des boutons dans la barre d'outils
TOOLBAR_BUTTONS = [
    {"type": 1, "label": "Grass"},
    {"type": 2, "label": "Dirt"},
    {"type": 3, "label": "Sand"},
    {"type": 0, "label": "Water"},
    {"type": 4, "label": "Stone"},
]

CURRENT_TERRAIN = TOOLBAR_BUTTONS[0]["type"]

# --- ÉTATS DE L'APPLICATION ---
APP_STATE = "START_SCREEN"

# Variables de l'état du jeu
TILE_SIZE = INIT_TILE_SIZE
camera_x = 0.0
camera_y = 0.0
is_panning = False
last_mouse_pos = (0, 0)

# Variables de défilement de l'UI
scroll_offset = 0
BUTTON_GAP = 10
BUTTON_BASE_WIDTH = 50
BUTTON_HEIGHT = TOOLBAR_HEIGHT - BUTTON_GAP

# Créer la grille (carte)
world_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)

# Font plus grande pour le chiffre
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 48)
clock = pygame.time.Clock()


# --- 3. FONCTIONS DE GESTION DU MONDE (INCHANGÉES) ---

def get_dimensions():
    scr_w, scr_h = screen.get_size()
    grid_bottom_y = scr_h - TOOLBAR_HEIGHT
    return float(scr_w), float(scr_h), float(grid_bottom_y)


def toggle_fullscreen():
    """Bascule entre mode fenêtre (taille par défaut) et plein écran."""
    global screen, current_screen_flags

    if current_screen_flags & pygame.FULLSCREEN:
        current_screen_flags &= ~pygame.FULLSCREEN
        screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)
    else:
        current_screen_flags |= FULLSCREEN_MODE
        screen_info = pygame.display.Info()
        screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), current_screen_flags)


def generate_random_world():
    """Génère un monde aléatoire avec Simplex Noise pour des formes naturelles et biomes mélangés."""
    global world_grid, TILE_SIZE, camera_x, camera_y

    # Réinitialisation de la caméra et du zoom
    TILE_SIZE = INIT_TILE_SIZE
    camera_x = 0.0
    camera_y = 0.0

    # Paramètres de bruit aléatoires pour la HAUTEUR et la forme de l'île
    seed_height = random.randint(0, 100000)
    simplex_height = OpenSimplex(seed=seed_height)

    # Scale très aléatoire pour garantir des formes d'îles très différentes
    SCALE_HEIGHT = random.uniform(8.0, 20.0)
    OFFSET_X = random.uniform(0.0, 1000.0)
    OFFSET_Y = random.uniform(0.0, 1000.0)

    CENTER_X = GRID_WIDTH / 2.0
    CENTER_Y = GRID_HEIGHT / 2.0

    # Le rayon peut être plus grand ou plus petit pour créer des continents ou des archipels
    MAX_RADIUS = random.uniform(GRID_WIDTH / 3.0, GRID_WIDTH / 2.0)

    # Seuils aléatoires pour plus de variété
    MOUNTAIN_THRESHOLD = random.uniform(0.65, 0.85)
    LAND_THRESHOLD = random.uniform(0.3, 0.4)

    # 1. GÉNÉRATION DE LA CARTE DE HAUTEUR
    height_map = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=float)

    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            # 1a. Bruit de Hauteur (Détermine si c'est de l'eau, terre ou montagne)
            noise_val_h = simplex_height.noise2(x=(c + OFFSET_X) / SCALE_HEIGHT, y=(r + OFFSET_Y) / SCALE_HEIGHT)
            normalized_noise_h = (noise_val_h + 1.0) / 2.0

            # Déformation du centre : force les bords à être de l'eau
            dist_to_center = math.sqrt((c - CENTER_X) ** 2 + (r - CENTER_Y) ** 2)
            edge_falloff = 1.0 - (dist_to_center / MAX_RADIUS) ** 2

            final_height = normalized_noise_h * max(0, edge_falloff)
            height_map[r, c] = final_height

    # 2. APPLICATION DES SEUILS ET CRÉATION DE LA GRILLE
    new_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)

    # Remplissage par défaut : Herbe (Type 1) pour les terres moyennes
    new_grid[(height_map > LAND_THRESHOLD)] = 1

    # Application de la Montagne/Terre Rugueuse (Type 2) sur les hauteurs
    new_grid[(height_map > MOUNTAIN_THRESHOLD)] = 2

    # Le reste est de l'eau (Type 0 par défaut de new_grid)

    # 3. POST-PROCESSUS: CRÉATION DES PLAGES DE SABLE
    final_grid = new_grid.copy()

    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if final_grid[r, c] == 1 or final_grid[r, c] == 2:  # Si c'est Herbe ou Montagne/Terre
                is_coastal = False

                # Vérifier si un voisin (y compris les diagonales) est de l'eau (0)
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue

                        nr, nc = r + dr, c + dc

                        if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                            if new_grid[nr, nc] == 0:
                                is_coastal = True
                                break
                    if is_coastal: break

                # Règle : Les tuiles Herbe ou Montagne adjacentes à l'eau deviennent du sable (3).
                if is_coastal:
                    final_grid[r, c] = 3

    world_grid = final_grid.tolist()


# --- 4. FONCTIONS UI ET AFFICHAGE ---

def handle_toolbar_click(mouse_pos, screen_width, grid_bottom_y):
    """Gère le clic sur les boutons de la barre d'outils, y compris le défilement (INCHANGÉ)."""
    global CURRENT_TERRAIN, scroll_offset

    if mouse_pos[1] > grid_bottom_y:

        # 1. Gérer les flèches de défilement
        left_arrow_rect = pygame.Rect(0, grid_bottom_y, SCROLL_BUTTON_WIDTH, TOOLBAR_HEIGHT)
        if left_arrow_rect.collidepoint(mouse_pos):
            scroll_offset = max(0, scroll_offset - (BUTTON_BASE_WIDTH + BUTTON_GAP))
            return True

        right_arrow_rect = pygame.Rect(screen_width - SCROLL_BUTTON_WIDTH, grid_bottom_y, SCROLL_BUTTON_WIDTH,
                                       TOOLBAR_HEIGHT)
        if right_arrow_rect.collidepoint(mouse_pos):
            total_button_width = (BUTTON_BASE_WIDTH + BUTTON_GAP) * len(TOOLBAR_BUTTONS)
            available_width = screen_width - 2 * SCROLL_BUTTON_WIDTH - BUTTON_GAP
            max_offset = max(0, total_button_width - available_width)

            scroll_offset = min(max_offset, scroll_offset + (BUTTON_BASE_WIDTH + BUTTON_GAP))
            return True

        # 2. Gérer les boutons d'outils
        button_area_left = SCROLL_BUTTON_WIDTH
        corrected_x = mouse_pos[0] + scroll_offset - button_area_left
        btn_index = corrected_x // (BUTTON_BASE_WIDTH + BUTTON_GAP)

        if 0 <= btn_index < len(TOOLBAR_BUTTONS):
            btn_x_start_in_corrected_area = btn_index * (BUTTON_BASE_WIDTH + BUTTON_GAP)
            click_x_in_button_space = corrected_x - btn_x_start_in_corrected_area

            if click_x_in_button_space < BUTTON_BASE_WIDTH:
                CURRENT_TERRAIN = TOOLBAR_BUTTONS[btn_index]["type"]
                return True

    return False


def draw_toolbar(screen_width, grid_bottom_y):
    """Dessine la barre d'outils. Utilise maintenant COLORS."""

    toolbar_rect = pygame.Rect(0, grid_bottom_y, screen_width, TOOLBAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), toolbar_rect)

    # --- Dessiner les Boutons de l'Outil ---

    # Définir la zone de clipping pour les boutons
    button_area_rect = pygame.Rect(SCROLL_BUTTON_WIDTH, grid_bottom_y, screen_width - 2 * SCROLL_BUTTON_WIDTH,
                                   TOOLBAR_HEIGHT)
    screen.set_clip(button_area_rect)

    button_y = grid_bottom_y + BUTTON_GAP / 2

    for i, btn in enumerate(TOOLBAR_BUTTONS):
        btn_x_absolute = SCROLL_BUTTON_WIDTH + (i * (BUTTON_BASE_WIDTH + BUTTON_GAP)) - scroll_offset

        btn_rect = pygame.Rect(btn_x_absolute, button_y, BUTTON_BASE_WIDTH, BUTTON_HEIGHT)

        # UTILISEZ COLORS pour l'UI, car COLORS contient des tuples de couleur, pas des surfaces
        btn_color = COLORS.get(btn["type"], (50, 50, 50))

        # Dessin du bouton
        if btn["type"] == CURRENT_TERRAIN:
            # Highlight pour l'outil sélectionné
            pygame.draw.rect(screen, (200, 200, 200), btn_rect, border_radius=5)
            inner_rect = btn_rect.inflate(-4, -4)
            pygame.draw.rect(screen, btn_color, inner_rect, border_radius=3)
        else:
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)

        # Affichage du type de terrain
        text_label = str(btn["label"])
        label_font = pygame.font.SysFont("comicsans", 15)
        text_surface = label_font.render(text_label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=btn_rect.center)
        screen.blit(text_surface, text_rect)

    # Retirer la zone de clipping
    screen.set_clip(None)


# --- Fonction de mise à jour des images redimensionnées (INCHANGÉE) ---
def update_terrain_images():
    """Redimensionne toutes les textures pour correspondre à la TILE_SIZE actuelle."""
    global TERRAIN_IMAGES

    # Vérifie si le redimensionnement est nécessaire (taille non définie ou différente)
    current_size = TERRAIN_IMAGES.get(0).get_size()[0] if 0 in TERRAIN_IMAGES else -1

    if current_size != int(TILE_SIZE) and TERRAIN_IMAGES_RAW:  # Ajout de la vérification TERRAIN_IMAGES_RAW
        new_images = {}
        for terrain_type, raw_img in TERRAIN_IMAGES_RAW.items():
            # Redimensionne l'image brute à la TILE_SIZE actuelle
            new_images[terrain_type] = pygame.transform.scale(
                raw_img, (int(TILE_SIZE), int(TILE_SIZE))
            )
        TERRAIN_IMAGES = new_images


def draw_world(screen_width, grid_bottom_y):
    """Dessine la grille visible en utilisant les images redimensionnées (INCHANGÉE)."""
    global camera_x, camera_y
    global TILE_SIZE

    # Correction du Dézoom / Bande Noire (INCHANGÉ)
    min_tile_size_x = screen_width / GRID_WIDTH
    min_tile_size_y = grid_bottom_y / GRID_HEIGHT

    TILE_SIZE = max(TILE_SIZE, min(min_tile_size_x, min_tile_size_y))

    # Correction de la position de la Caméra (INCHANGÉ)
    max_camera_x = max(0.0, GRID_WIDTH * TILE_SIZE - screen_width)
    max_camera_y = max(0.0, GRID_HEIGHT * TILE_SIZE - grid_bottom_y)

    camera_x = max(0.0, min(camera_x, max_camera_x))
    camera_y = max(0.0, min(camera_y, max_camera_y))

    # Redimensionner les images pour la TILE_SIZE actuelle
    update_terrain_images()

    # Dessin des tuiles visibles
    start_col = max(0, int(camera_x // TILE_SIZE))
    end_col = min(GRID_WIDTH, int((camera_x + screen_width) // TILE_SIZE + 1))
    start_row = max(0, int(camera_y // TILE_SIZE))
    end_row = min(GRID_HEIGHT, int((camera_y + grid_bottom_y) // TILE_SIZE + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            terrain_type = world_grid[row][col]

            # Utiliser l'image redimensionnée
            image_to_draw = TERRAIN_IMAGES.get(terrain_type)

            if image_to_draw:
                screen_x = col * TILE_SIZE - camera_x
                screen_y = row * TILE_SIZE - camera_y

                # Dessin de l'image (texture)
                screen.blit(image_to_draw, (screen_x, screen_y))


# --- 5. GESTION DE L'ÉCRAN DE DÉMARRAGE (INCHANGÉE) ---

START_BUTTONS = []


def draw_start_screen(screen_width, screen_height):
    screen.fill((20, 20, 40))

    title_surface = title_font.render("Créateur de Monde Sandbox", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(int(screen_width / 2), int(screen_height / 4)))
    screen.blit(title_surface, title_rect)

    button_w, button_h = 300, 60
    center_x = screen_width / 2

    btn1_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 - button_h - 10, button_w, button_h)
    pygame.draw.rect(screen, (50, 150, 50), btn1_rect, border_radius=10)
    text1 = font.render("Créer de zéro (Eau)", True, (255, 255, 255))
    text1_rect = text1.get_rect(center=btn1_rect.center)
    screen.blit(text1, text1_rect)

    btn2_rect = pygame.Rect(center_x - button_w / 2, screen_height / 2 + 10, button_w, button_h)
    pygame.draw.rect(screen, (150, 50, 50), btn2_rect, border_radius=10)
    text2 = font.render("Monde aléatoire (Organique)", True, (255, 255, 255))
    text2_rect = text2.get_rect(center=btn2_rect.center)
    screen.blit(text2, text2_rect)

    global START_BUTTONS
    START_BUTTONS = [
        {"rect": btn1_rect, "action": "NEW"},
        {"rect": btn2_rect, "action": "RANDOM"}
    ]


def handle_start_screen_click(mouse_pos):
    global APP_STATE, world_grid

    for btn in START_BUTTONS:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["action"] == "NEW":
                world_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int).tolist()
                APP_STATE = "GAME_SCREEN"

            elif btn["action"] == "RANDOM":
                generate_random_world()
                APP_STATE = "GAME_SCREEN"
            return True
    return False


# --- 6. BOUCLE PRINCIPALE DE JEU (INCHANGÉE) ---

running = True
is_drawing = False

while running:
    screen_width, screen_height, grid_bottom_y = get_dimensions()

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

            elif APP_STATE == "GAME_SCREEN":
                if event.button == 1:  # Clic Gauche (Dessin/UI)
                    if handle_toolbar_click(mouse_pos, screen_width, grid_bottom_y):
                        is_drawing = False
                    elif mouse_pos[1] < grid_bottom_y:
                        is_drawing = True

                elif event.button == 3:  # Clic Droit (Déplacement)
                    is_panning = True
                    last_mouse_pos = mouse_pos

                elif event.button == 4:  # Molette haut (Zoom in)
                    TILE_SIZE = min(64.0, TILE_SIZE + 2.0)
                elif event.button == 5:  # Molette bas (Zoom out)
                    TILE_SIZE = max(4.0, TILE_SIZE - 2.0)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_drawing = False
            elif event.button == 3:
                is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            if APP_STATE == "GAME_SCREEN" and is_panning:
                dx = mouse_pos[0] - last_mouse_pos[0]
                dy = mouse_pos[1] - last_mouse_pos[1]

                camera_x -= dx
                camera_y -= dy

                last_mouse_pos = mouse_pos

    # --- LOGIQUE D'AFFICHAGE ---
    screen.fill((0, 0, 0))

    if APP_STATE == "START_SCREEN":
        draw_start_screen(screen_width, screen_height)

    elif APP_STATE == "GAME_SCREEN":
        # 1. Dessiner le monde (maintenant avec des images)
        draw_world(screen_width, grid_bottom_y)

        # 2. Application du Pinceau (Dessin)
        if is_drawing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < grid_bottom_y:
                world_x = mouse_x + camera_x
                world_y = mouse_y + camera_y

                grid_col = world_x // TILE_SIZE
                grid_row = world_y // TILE_SIZE

                if 0 <= grid_col < GRID_WIDTH and 0 <= grid_row < GRID_HEIGHT:
                    world_grid[int(grid_row)][int(grid_col)] = CURRENT_TERRAIN

        # 3. Dessiner la barre d'outils
        draw_toolbar(screen_width, grid_bottom_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
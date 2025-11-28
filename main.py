import pygame
import sys
import random
import math
import numpy as np
from opensimplex import OpenSimplex
from assets import *

# --- 1. CONFIGURATION STATIQUE ---
INIT_TILE_SIZE = 16.0
GRID_WIDTH = 100
GRID_HEIGHT = 80

TOOLBAR_HEIGHT = 60
SCROLL_BUTTON_WIDTH = 50

# Dimensions de la fenêtre par défaut
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700

# Couleurs pour les types de terrain (MAINTENU UNIQUEMENT POUR L'AFFICHAGE DE L'ui)
COLORS = {
    0: (0, 0, 200),  # Eau
    1: (0, 150, 0),  # Herbe
    2: (150, 75, 0),  # Montagne
    3: (240, 230, 140),  # Sable
    4: (120, 120, 120)  # Pierre
}

# --- Brush Sizes ---
BRUSH_SIZES = [1, 4, 16, 64]
CURRENT_BRUSH = 1  # default 1x1

TERRAIN_IMAGES_RAW = {}
TERRAIN_IMAGES = {}

# --- World Time Simulation ---
world_minutes = 0
world_hours = 0
world_days = 0
display_hours = 0
# 1 real second = 1 game hour
GAME_HOURS_PER_SECOND = 1

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
        0: pygame.image.load("assets/water.png").convert_alpha(),
        1: pygame.image.load("assets/grass.png").convert_alpha(),
        2: pygame.image.load("assets/dirt.png").convert_alpha(),
        3: pygame.image.load("assets/sand.png").convert_alpha(),
        4: pygame.image.load("assets/stone.png").convert_alpha(),
    }
    # J'ai retiré les types 4 (stone/dirt) car ils n'étaient pas définis dans le COLORS ni dans TOOLBAR_BUTTONS.
    # Si vous voulez les utiliser, vous devez mettre à jour COLORS et TOOLBAR_BUTTONS.
except pygame.error as e:
    print(
        f"Erreur de chargement d'image : Vérifiez l'existence des fichiers dans 'assets/'. Erreur: {e}")
    sys.exit()

# --- FIN DE L'INITIALISATION RÉORGANISÉE ---


# Définition des boutons dans la barre d'outils
TOOLBAR_BUTTONS = [
    {"type": 0, "label": "Water"},
    {"type": 1, "label": "Grass"},
    {"type": 2, "label": "Dirt"},
    {"type": 3, "label": "Sand"},
    {"type": 4, "label": "Stone"},
    {"type": "BRUSH_1", "label": "x1", "brush": 1},
    {"type": "BRUSH_2", "label": "x2", "brush": 2},
    {"type": "BRUSH_3", "label": "x4", "brush": 4},
    {"type": "BRUSH_4", "label": "x8", "brush": 8},
    {"type": "BRUSH_5", "label": "x16", "brush": 16},
    {"type": "BRUSH_6", "label": "x32", "brush": 32}
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
minimap_dragging = False
minimap_drag_offset = (0, 0)

# Variables de défilement de l'ui
scroll_offset = 0
BUTTON_GAP = 10
BUTTON_BASE_WIDTH = 50
BUTTON_HEIGHT = TOOLBAR_HEIGHT - BUTTON_GAP

# Créer la grille (carte)
world_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)

# Fonts
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 48)
label_font = pygame.font.SysFont("comicsans", 15)

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


# --- 4. FONCTIONS ui ET AFFICHAGE ---

def handle_toolbar_click(mouse_pos, screen_width, grid_bottom_y):
    """Gère le clic sur les boutons de la barre d'outils."""
    global CURRENT_TERRAIN, scroll_offset, CURRENT_BRUSH

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
        btn_index = int(corrected_x // (BUTTON_BASE_WIDTH + BUTTON_GAP))

        if 0 <= btn_index < len(TOOLBAR_BUTTONS):
            btn_x_start_in_corrected_area = btn_index * (BUTTON_BASE_WIDTH + BUTTON_GAP)
            click_x_in_button_space = corrected_x - btn_x_start_in_corrected_area

            if click_x_in_button_space < BUTTON_BASE_WIDTH:
                btn = TOOLBAR_BUTTONS[btn_index]  # full dict

                # Brush button?
                if "brush" in btn:
                    CURRENT_BRUSH = int(btn["brush"])
                else:
                    # Standard terrain selection
                    CURRENT_TERRAIN = btn["type"]
                return True

    return False

def draw_toolbar(screen_width, grid_bottom_y):
    """Dessine la barre d'outils et les boutons de brush."""
    toolbar_rect = pygame.Rect(0, grid_bottom_y, screen_width, TOOLBAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), toolbar_rect)

    # --- Dessiner les Boutons de l'Outil ---
    button_area_rect = pygame.Rect(SCROLL_BUTTON_WIDTH, grid_bottom_y, screen_width - 2 * SCROLL_BUTTON_WIDTH,
                                   TOOLBAR_HEIGHT)
    screen.set_clip(button_area_rect)

    button_y = grid_bottom_y + BUTTON_GAP / 2

    for i, btn in enumerate(TOOLBAR_BUTTONS):
        btn_x_absolute = SCROLL_BUTTON_WIDTH + (i * (BUTTON_BASE_WIDTH + BUTTON_GAP)) - scroll_offset
        btn_rect = pygame.Rect(btn_x_absolute, button_y, BUTTON_BASE_WIDTH, BUTTON_HEIGHT)

        # choose base color: for terrain use COLORS, for brush use a neutral gray
        if "brush" in btn:
            btn_color = (80, 80, 120)
        else:
            btn_color = COLORS.get(btn["type"], (50, 50, 50))

        # Highlight if selected
        is_selected = False
        if "brush" in btn and int(btn["brush"]) == int(CURRENT_BRUSH):
            is_selected = True
        if not "brush" in btn and btn["type"] == CURRENT_TERRAIN:
            is_selected = True

        if is_selected:
            pygame.draw.rect(screen, (200, 200, 200), btn_rect, border_radius=5)
            inner_rect = btn_rect.inflate(-4, -4)
            pygame.draw.rect(screen, btn_color, inner_rect, border_radius=3)
        else:
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)

        # label
        text_label = str(btn["label"])
        text_surface = label_font.render(text_label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=btn_rect.center)
        screen.blit(text_surface, text_rect)

    screen.set_clip(None)

def draw_world_time():
    global display_hours, world_minutes
    time_text = f"Day {world_days} - {display_hours:02d}:{world_minutes:02d}"
    text_surface = font.render(time_text, True, (255, 255, 255))
    screen.blit(text_surface, (20, 20))  # top-left corner

# --- MINIMAP (définir avant la boucle principale) ---
def draw_minimap(screen_width, grid_bottom_y):
    """Dessine la minimap en haut à droite et le rectangle de la vue."""
    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    # Position en haut à droite
    minimap_x = screen_width - MAP_W - MARGIN
    minimap_y = MARGIN

    # fond + bord
    pygame.draw.rect(screen, (30, 30, 30), (minimap_x - 2, minimap_y - 2, MAP_W + 4, MAP_H + 4), border_radius=4)
    pygame.draw.rect(screen, (0, 0, 0), (minimap_x, minimap_y, MAP_W, MAP_H))

    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    # dessiner la grille réduite
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            terrain_type = world_grid[r][c]
            color = COLORS.get(terrain_type, (255, 0, 255))
            px = int(minimap_x + c * cell_w)
            py = int(minimap_y + r * cell_h)
            # dessine un petit rectangle (au moins 1px)
            screen.fill(color, (px, py, max(1, int(math.ceil(cell_w))), max(1, int(math.ceil(cell_h)))))

    # rectangle de la zone visible (en tuiles)
    # largeur de la vue en tuiles = screen_width / TILE_SIZE
    view_cols = screen_width / TILE_SIZE
    view_rows = (grid_bottom_y) / TILE_SIZE

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = minimap_x + (camera_x / TILE_SIZE) * cell_w
    view_y = minimap_y + (camera_y / TILE_SIZE) * cell_h

    # tracer le rectangle (avec clamp pour garder l'affichage propre)
    pygame.draw.rect(screen, (255, 0, 0), (view_x, view_y, view_w, view_h), width=2)


def handle_minimap_click(mouse_pos, screen_width, grid_bottom_y):
    global camera_x, camera_y, minimap_dragging, minimap_drag_offset

    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    mini_x = screen_width - MAP_W - MARGIN
    mini_y = MARGIN

    mx, my = mouse_pos

    if not (mini_x <= mx <= mini_x + MAP_W and mini_y <= my <= mini_y + MAP_H):
        return False

    # coordonnées relatives
    rel_x = (mx - mini_x) / MAP_W
    rel_y = (my - mini_y) / MAP_H

    # calcul du rectangle de vue pour déterminer si on clique dedans (début drag)
    view_cols = screen_width / TILE_SIZE
    view_rows = grid_bottom_y / TILE_SIZE
    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = mini_x + (camera_x / TILE_SIZE) * cell_w
    view_y = mini_y + (camera_y / TILE_SIZE) * cell_h

    # si clic dans le rectangle rouge → start drag
    if view_x <= mx <= view_x + view_w and view_y <= my <= view_y + view_h:
        minimap_dragging = True
        minimap_drag_offset = (mx - view_x, my - view_y)
        return True

    # sinon → clic normal (téléportation instantanée)
    target_col = int(rel_x * GRID_WIDTH)
    target_row = int(rel_y * GRID_HEIGHT)

    scr_w, scr_h = screen.get_size()
    new_cam_x = (target_col + 0.5) * TILE_SIZE - scr_w / 2
    new_cam_y = (target_row + 0.5) * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT) / 2

    max_camera_x = max(0, GRID_WIDTH * TILE_SIZE - scr_w)
    max_camera_y = max(0, GRID_HEIGHT * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT))

    camera_x = max(0, min(new_cam_x, max_camera_x))
    camera_y = max(0, min(new_cam_y, max_camera_y))

    return True

def handle_minimap_drag(mouse_pos, screen_width, grid_bottom_y):
    global camera_x, camera_y, minimap_dragging

    if not minimap_dragging:
        return

    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    mini_x = screen_width - MAP_W - MARGIN
    mini_y = MARGIN

    mx, my = mouse_pos

    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    # position de la nouvelle tuile ciblée
    view_x = mx - minimap_drag_offset[0]
    view_y = my - minimap_drag_offset[1]

    # conversion en tuiles
    tile_col = (view_x - mini_x) / cell_w
    tile_row = (view_y - mini_y) / cell_h

    scr_w, scr_h = screen.get_size()
    new_cam_x = tile_col * TILE_SIZE
    new_cam_y = tile_row * TILE_SIZE

    # clamp
    max_camera_x = max(0, GRID_WIDTH * TILE_SIZE - scr_w)
    max_camera_y = max(0, GRID_HEIGHT * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT))

    camera_x = max(0, min(new_cam_x, max_camera_x))
    camera_y = max(0, min(new_cam_y, max_camera_y))

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
            # --- Priorité : clic sur la minimap ---
            if APP_STATE == "GAME_SCREEN":
                if handle_minimap_click(mouse_pos, screen_width, grid_bottom_y):
                    # On empêche le reste du code de traiter ce clic
                    is_drawing = False
                    is_panning = False
                    continue

            if APP_STATE == "START_SCREEN":
                handle_start_screen_click(mouse_pos)

            elif APP_STATE == "GAME_SCREEN":
                if event.button == 1:  # Clic Gauche (Dessin/ui)
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
            minimap_dragging = False
            if event.button == 1:
                is_drawing = False
            elif event.button == 3:
                is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            # Priorité : si on est en train de drag la minimap → ignorer le reste
            if APP_STATE == "GAME_SCREEN" and minimap_dragging:
                handle_minimap_drag(mouse_pos, screen_width, grid_bottom_y)
                continue

            # Panning clic droit
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

                grid_col = int(world_x // TILE_SIZE)
                grid_row = int(world_y // TILE_SIZE)

                if 0 <= grid_col < GRID_WIDTH and 0 <= grid_row < GRID_HEIGHT:
                    # compute offsets so that we paint an exact CURRENT_BRUSH x CURRENT_BRUSH square
                    N = int(CURRENT_BRUSH)
                    start_offset = -(N // 2)
                    # For even sizes this centers slightly up-left which is expected; you can change anchor if you want top-left.
                    for dr in range(start_offset, start_offset + N):
                        for dc in range(start_offset, start_offset + N):
                            r = grid_row + dr
                            c = grid_col + dc
                            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                                world_grid[r][c] = CURRENT_TERRAIN

        # 3. Dessiner l'ui
        draw_toolbar(screen_width, grid_bottom_y)
        draw_minimap(screen_width, grid_bottom_y)
        draw_world_time()

    # --- Update world time ---
    delta_real_seconds = clock.get_time() / 1000  # convert ms to seconds

    # Add hours according to your rule
    world_hours += delta_real_seconds * GAME_HOURS_PER_SECOND

    # Handle overflow
    while world_hours >= 24:
        world_hours -= 24
        world_days += 1

    world_minutes = int((world_hours % 1) * 60)
    display_hours = int(world_hours)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
import pygame
import sys
import random
import math
import numpy as np
from opensimplex import OpenSimplex
# Assurez-vous que ce module et la fonction draw_elements existent et sont accessibles
from rendering.draw_element_cg import draw_elements

# --- 1. CONFIGURATION STATIQUE ---
INIT_TILE_SIZE = 16.0
GRID_WIDTH = 100
GRID_HEIGHT = 80

TOOLBAR_HEIGHT = 60
SCROLL_BUTTON_WIDTH = 50

# Dimensions de la fenêtre par défaut
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700

# Paramètres pour la grille de placement d'éléments fins (8x8)
ELEMENT_GRID_SIZE = 8  # La taille de la sous-cellule en pixels (moitié de 16)
ELEMENT_SCALE_FACTOR = int(INIT_TILE_SIZE / ELEMENT_GRID_SIZE)  # 16 / 8 = 2

# Dimensions de la grille d'éléments (double de la grille de terrain)
ELEMENT_GRID_WIDTH = GRID_WIDTH * ELEMENT_SCALE_FACTOR  # 200
ELEMENT_GRID_HEIGHT = GRID_HEIGHT * ELEMENT_SCALE_FACTOR  # 160

# --- Taille des éléments en cellules 8x8 ---
BIG_ROCK_SIZE_32x32 = 4  # La grande pierre est 4x4 cellules d'éléments (32x32px initial)

# Couleurs pour les types de terrain (MAINTENU UNIQUEMENT POUR L'AFFICHAGE DE L'ui)
COLORS = {
    0: (0, 0, 200),  # Eau
    1: (0, 150, 0),  # Herbe
    2: (150, 75, 0),  # Montagne
    3: (240, 230, 140),  # Sable
    4: (120, 120, 120),  # Pierre
    5: (100, 100, 100),  # S_rock1 (8x8)
    6: (80, 80, 80),  # B_rock (32x32)
    -1: (200, 50, 50)
}

# --- Brush Sizes ---
BRUSH_SIZES = [1, 4, 16, 64]
CURRENT_BRUSH = 1  # default 1x1

TERRAIN_IMAGES_RAW = {}
TERRAIN_IMAGES = {}

# --- 2. INITIALISATION PYGAME ET AFFICHAGE ---

# 1. Initialiser Pygame une seule fois
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")

# 2. Définir le mode vidéo (création de l'écran)
FULLSCREEN_MODE = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
current_screen_flags = 0

screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), current_screen_flags)

# 3. Charger les images
try:
    TERRAIN_IMAGES_RAW = {
        0: pygame.image.load("assets/water.png").convert_alpha(),
        1: pygame.image.load("assets/grass.png").convert_alpha(),
        2: pygame.image.load("assets/dirt.png").convert_alpha(),
        3: pygame.image.load("assets/sand.png").convert_alpha(),
        4: pygame.image.load("assets/stone.png").convert_alpha(),
        5: pygame.image.load("assets/S_rock1.png").convert_alpha(),
        6: pygame.image.load("assets/B_rock.png").convert_alpha(),
        # -----------------------------
    }
except pygame.error as e:
    print(
        f"Erreur de chargement d'image : Vérifiez l'existence des fichiers dans 'assets/'. Erreur: {e}")
    sys.exit()

# Définition des boutons dans la barre d'outils
TOOLBAR_BUTTONS = [
    {"type": -1, "label": "gomme"},
    {"type": 0, "label": "Water"},
    {"type": 1, "label": "Grass"},
    {"type": 2, "label": "Dirt"},
    {"type": 3, "label": "Sand"},
    {"type": 4, "label": "Stone"},
    {"type": 5, "label": "S_rock1 (8x8)"},
    {"type": 6, "label": "B_rock (32x32)"},
    # ------------------------------------
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

# Grille pour les éléments 8x8 (0: vide, 5: petite pierre, 6: grande pierre (ancrage), -1: blocage grande pierre)
element_grid = np.zeros((ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int).tolist()
# Fonts
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 48)
label_font = pygame.font.SysFont("comicsans", 15)

clock = pygame.time.Clock()


# --- 3. FONCTIONS DE GESTION DU MONDE ---

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

    TILE_SIZE = INIT_TILE_SIZE
    camera_x = 0.0
    camera_y = 0.0

    seed_height = random.randint(0, 100000)
    simplex_height = OpenSimplex(seed=seed_height)

    SCALE_HEIGHT = random.uniform(8.0, 20.0)
    OFFSET_X = random.uniform(0.0, 1000.0)
    OFFSET_Y = random.uniform(0.0, 1000.0)

    CENTER_X = GRID_WIDTH / 2.0
    CENTER_Y = GRID_HEIGHT / 2.0
    MAX_RADIUS = random.uniform(GRID_WIDTH / 3.0, GRID_WIDTH / 2.0)
    MOUNTAIN_THRESHOLD = random.uniform(0.65, 0.85)
    LAND_THRESHOLD = random.uniform(0.3, 0.4)

    height_map = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=float)

    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            noise_val_h = simplex_height.noise2(x=(c + OFFSET_X) / SCALE_HEIGHT, y=(r + OFFSET_Y) / SCALE_HEIGHT)
            normalized_noise_h = (noise_val_h + 1.0) / 2.0

            dist_to_center = math.sqrt((c - CENTER_X) ** 2 + (r - CENTER_Y) ** 2)
            edge_falloff = 1.0 - (dist_to_center / MAX_RADIUS) ** 2

            final_height = normalized_noise_h * max(0, edge_falloff)
            height_map[r, c] = final_height

    new_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
    new_grid[(height_map > LAND_THRESHOLD)] = 1
    new_grid[(height_map > MOUNTAIN_THRESHOLD)] = 2

    final_grid = new_grid.copy()

    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if final_grid[r, c] == 1 or final_grid[r, c] == 2:
                is_coastal = False
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                            if new_grid[nr, nc] == 0:
                                is_coastal = True
                                break
                    if is_coastal: break

                if is_coastal:
                    final_grid[r, c] = 3

    world_grid = final_grid.tolist()


# --- 4. FONCTIONS UI ET AFFICHAGE ---

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
                btn = TOOLBAR_BUTTONS[btn_index]

                if "brush" in btn:
                    CURRENT_BRUSH = int(btn["brush"])
                else:
                    CURRENT_TERRAIN = btn["type"]
                return True

    return False


def draw_toolbar(screen_width, grid_bottom_y):
    """Dessine la barre d'outils et les boutons de brush."""
    toolbar_rect = pygame.Rect(0, grid_bottom_y, screen_width, TOOLBAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), toolbar_rect)

    button_area_rect = pygame.Rect(SCROLL_BUTTON_WIDTH, grid_bottom_y, screen_width - 2 * SCROLL_BUTTON_WIDTH,
                                   TOOLBAR_HEIGHT)
    screen.set_clip(button_area_rect)

    button_y = grid_bottom_y + BUTTON_GAP / 2

    for i, btn in enumerate(TOOLBAR_BUTTONS):
        btn_x_absolute = SCROLL_BUTTON_WIDTH + (i * (BUTTON_BASE_WIDTH + BUTTON_GAP)) - scroll_offset
        btn_rect = pygame.Rect(btn_x_absolute, button_y, BUTTON_BASE_WIDTH, BUTTON_HEIGHT)

        if "brush" in btn:
            btn_color = (80, 80, 120)
        else:
            btn_color = COLORS.get(btn["type"], (50, 50, 50))

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

        text_label = str(btn["label"])
        text_surface = label_font.render(text_label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=btn_rect.center)
        screen.blit(text_surface, text_rect)

    screen.set_clip(None)


def draw_minimap(screen_width, grid_bottom_y):
    """Dessine la minimap en haut à droite et le rectangle de la vue."""
    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    minimap_x = screen_width - MAP_W - MARGIN
    minimap_y = MARGIN

    pygame.draw.rect(screen, (30, 30, 30), (minimap_x - 2, minimap_y - 2, MAP_W + 4, MAP_H + 4), border_radius=4)
    pygame.draw.rect(screen, (0, 0, 0), (minimap_x, minimap_y, MAP_W, MAP_H))

    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            terrain_type = world_grid[r][c]
            color = COLORS.get(terrain_type, (255, 0, 255))
            px = int(minimap_x + c * cell_w)
            py = int(minimap_y + r * cell_h)
            screen.fill(color, (px, py, max(1, int(math.ceil(cell_w))), max(1, int(math.ceil(cell_h)))))

    view_cols = screen_width / TILE_SIZE
    view_rows = (grid_bottom_y) / TILE_SIZE

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = minimap_x + (camera_x / TILE_SIZE) * cell_w
    view_y = minimap_y + (camera_y / TILE_SIZE) * cell_h

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

    rel_x = (mx - mini_x) / MAP_W
    rel_y = (my - mini_y) / MAP_H

    view_cols = screen_width / TILE_SIZE
    view_rows = grid_bottom_y / TILE_SIZE
    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = mini_x + (camera_x / TILE_SIZE) * cell_w
    view_y = mini_y + (camera_y / TILE_SIZE) * cell_h

    if view_x <= mx <= view_x + view_w and view_y <= my <= view_y + view_h:
        minimap_dragging = True
        minimap_drag_offset = (mx - view_x, my - view_y)
        return True

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

    view_x = mx - minimap_drag_offset[0]
    view_y = my - minimap_drag_offset[1]

    tile_col = (view_x - mini_x) / cell_w
    tile_row = (view_y - mini_y) / cell_h

    scr_w, scr_h = screen.get_size()
    new_cam_x = tile_col * TILE_SIZE
    new_cam_y = tile_row * TILE_SIZE

    max_camera_x = max(0, GRID_WIDTH * TILE_SIZE - scr_w)
    max_camera_y = max(0, GRID_HEIGHT * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT))

    camera_x = max(0, min(new_cam_x, max_camera_x))
    camera_y = max(0, min(new_cam_y, max_camera_y))


def update_terrain_images():
    """Redimensionne toutes les textures pour correspondre à la TILE_SIZE actuelle."""
    global TERRAIN_IMAGES

    current_size = TERRAIN_IMAGES.get(0).get_size()[0] if 0 in TERRAIN_IMAGES else -1

    if current_size != int(TILE_SIZE) and TERRAIN_IMAGES_RAW:
        new_images = {}
        for terrain_type, raw_img in TERRAIN_IMAGES_RAW.items():
            new_images[terrain_type] = pygame.transform.scale(
                raw_img, (int(TILE_SIZE), int(TILE_SIZE))
            )
        TERRAIN_IMAGES = new_images


def draw_world(screen_width, grid_bottom_y):
    """Dessine la grille visible en utilisant les images redimensionnées."""
    global camera_x, camera_y
    global TILE_SIZE

    min_tile_size_x = screen_width / GRID_WIDTH
    min_tile_size_y = grid_bottom_y / GRID_HEIGHT

    TILE_SIZE = max(TILE_SIZE, min(min_tile_size_x, min_tile_size_y))

    max_camera_x = max(0.0, GRID_WIDTH * TILE_SIZE - screen_width)
    max_camera_y = max(0.0, GRID_HEIGHT * TILE_SIZE - grid_bottom_y)

    camera_x = max(0.0, min(camera_x, max_camera_x))
    camera_y = max(0.0, min(camera_y, max_camera_y))

    update_terrain_images()

    start_col = max(0, int(camera_x // TILE_SIZE))
    end_col = min(GRID_WIDTH, int((camera_x + screen_width) // TILE_SIZE + 1))
    start_row = max(0, int(camera_y // TILE_SIZE))
    end_row = min(GRID_HEIGHT, int((camera_y + grid_bottom_y) // TILE_SIZE + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            terrain_type = world_grid[row][col]

            image_to_draw = TERRAIN_IMAGES.get(terrain_type)

            if image_to_draw:
                screen_x = col * TILE_SIZE - camera_x
                screen_y = row * TILE_SIZE - camera_y

                screen.blit(image_to_draw, (screen_x, screen_y))


# --- 5. GESTION DE L'ÉCRAN DE DÉMARRAGE ---

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
    global APP_STATE, world_grid, element_grid

    for btn in START_BUTTONS:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["action"] == "NEW":
                world_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int).tolist()
                element_grid = np.zeros((ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int).tolist()
                APP_STATE = "GAME_SCREEN"

            elif btn["action"] == "RANDOM":
                generate_random_world()
                element_grid = np.zeros((ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int).tolist()
                APP_STATE = "GAME_SCREEN"
            return True
    return False


# --- 6. BOUCLE PRINCIPALE DE JEU (LOGIQUE D'ÉLÉMENTS 4X4 MISE À JOUR) ---

running = True
is_drawing = False

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
                if handle_minimap_click(mouse_pos, screen_width, grid_bottom_y):
                    is_drawing = False
                    is_panning = False
                    continue

                # 2. Zoom (Molette)
                if event.button == 4:  # Molette haut (Zoom in)
                    TILE_SIZE = min(64.0, TILE_SIZE + 2.0)
                    continue

                elif event.button == 5:  # Molette bas (Zoom out)
                    TILE_SIZE = max(4.0, TILE_SIZE - 2.0)
                    continue


                # 3. Clic Gauche (Dessin/ui)
                elif event.button == 1:
                    # Clic sur la barre d'outils?
                    if handle_toolbar_click(mouse_pos, screen_width, grid_bottom_y):
                        is_drawing = False

                    # Clic sur la grille?
                    elif mouse_pos[1] < grid_bottom_y:
                        world_x = mouse_pos[0] + camera_x
                        world_y = mouse_pos[1] + camera_y

                        # --- Placement de TERRAIN 16x16 (Active le dessin continu) ---
                        if CURRENT_TERRAIN < 5:
                            is_drawing = True

                        # --- Placement d'ÉLÉMENT 8x8 (Petit Rocher) : Clic unique ---
                        elif CURRENT_TERRAIN == 5:
                            cell_8x8_size = TILE_SIZE / ELEMENT_SCALE_FACTOR
                            grid_col_el = int(world_x // cell_8x8_size)
                            grid_row_el = int(world_y // cell_8x8_size)

                            if (0 <= grid_col_el < ELEMENT_GRID_WIDTH and
                                    0 <= grid_row_el < ELEMENT_GRID_HEIGHT):
                                # Placement anti-chevauchement (1x1)
                                if element_grid[grid_row_el][grid_col_el] == 0:
                                    element_grid[grid_row_el][grid_col_el] = 5

                            is_drawing = False

                        # --- NOUVEAU : Placement de GRANDE PIERRE (4x4) : Clic unique ---
                        elif CURRENT_TERRAIN == 6:
                            cell_8x8_size = TILE_SIZE / ELEMENT_SCALE_FACTOR
                            # Coordonnées du coin supérieur gauche du bloc 4x4
                            grid_col_el_start = int(world_x // cell_8x8_size)
                            grid_row_el_start = int(world_y // cell_8x8_size)

                            SIZE = BIG_ROCK_SIZE_8x8  # 4

                            # 1. Vérifier si le bloc 4x4 est entièrement dans les limites ET n'est pas chevauché
                            if (0 <= grid_col_el_start <= ELEMENT_GRID_WIDTH - SIZE and
                                    0 <= grid_row_el_start <= ELEMENT_GRID_HEIGHT - SIZE):

                                # Vérification du chevauchement (sur tout le bloc 4x4)
                                can_place = True
                                for r in range(grid_row_el_start, grid_row_el_start + SIZE):
                                    for c in range(grid_col_el_start, grid_col_el_start + SIZE):
                                        if element_grid[r][c] != 0:
                                            can_place = False
                                            break
                                    if not can_place:
                                        break

                                # 2. Si pas de chevauchement, placer
                                if can_place:
                                    # Ancrage (Type 6): Seule la cellule supérieure gauche a la valeur 6
                                    element_grid[grid_row_el_start][grid_col_el_start] = 6

                                    # Marquer les autres cellules comme "occupées" (Type -1)
                                    for r in range(grid_row_el_start, grid_row_el_start + SIZE):
                                        for c in range(grid_col_el_start, grid_col_el_start + SIZE):
                                            if r != grid_row_el_start or c != grid_col_el_start:
                                                element_grid[r][c] = -1  # Cellule occupée

                            is_drawing = False
                        # -------------------------------------------------------------

                # 4. Clic Droit (Déplacement ou Effacement 8x8/32x32)
                elif event.button == 3:
                    world_x = mouse_pos[0] + camera_x
                    world_y = mouse_pos[1] + camera_y

                    # Tenter l'effacement si l'outil 'Élément' est sélectionné
                    if (CURRENT_TERRAIN == 5 or CURRENT_TERRAIN == 6) and mouse_pos[1] < grid_bottom_y:

                        cell_8x8_size = TILE_SIZE / ELEMENT_SCALE_FACTOR
                        grid_col_el = int(world_x // cell_8x8_size)
                        grid_row_el = int(world_y // cell_8x8_size)

                        if (0 <= grid_col_el < ELEMENT_GRID_WIDTH and
                                0 <= grid_row_el < ELEMENT_GRID_HEIGHT):

                            # Si c'est un petit rocher (Type 5), effacement simple
                            if element_grid[grid_row_el][grid_col_el] == 5:
                                element_grid[grid_row_el][grid_col_el] = 0
                                continue

                            # Si c'est un point d'ancrage (Type 6) ou un marqueur (-1) de Grande Pierre
                            elif element_grid[grid_row_el][grid_col_el] == 6 or element_grid[grid_row_el][
                                grid_col_el] == -1:

                                SIZE = BIG_ROCK_SIZE_8x8  # 4

                                anchor_r = -1
                                anchor_c = -1

                                # 1. Trouver l'ancrage (cellule de type 6) pour commencer l'effacement
                                # Recherche dans le bloc 4x4 autour du clic (dr/dc va de 0 à -3)
                                for dr in range(-SIZE + 1, 1):
                                    for dc in range(-SIZE + 1, 1):
                                        r_check = grid_row_el + dr
                                        c_check = grid_col_el + dc

                                        if (0 <= r_check < ELEMENT_GRID_HEIGHT and
                                                0 <= c_check < ELEMENT_GRID_WIDTH and
                                                element_grid[r_check][c_check] == 6):
                                            anchor_r = r_check
                                            anchor_c = c_check
                                            break
                                    if anchor_r != -1:
                                        break

                                # 2. Si l'ancrage est trouvé, effacer tout le bloc 4x4.
                                if anchor_r != -1:
                                    for r in range(anchor_r, anchor_r + SIZE):
                                        for c in range(anchor_c, anchor_c + SIZE):
                                            if 0 <= r < ELEMENT_GRID_HEIGHT and 0 <= c < ELEMENT_GRID_WIDTH:
                                                element_grid[r][c] = 0

                                    continue  # Ne pas activer le Panning si on a effacé.

                    # Sinon, activer le Panning (Déplacement)
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
                    handle_minimap_drag(mouse_pos, screen_width, grid_bottom_y)
                    continue

                # Panning clic droit
                if is_panning:
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    dy = mouse_pos[1] - last_mouse_pos[1]
                    camera_x -= dx
                    camera_y -= dy
                    last_mouse_pos = mouse_pos

                # Dessin continu (Clic gauche maintenu)
                elif is_drawing and CURRENT_TERRAIN < 5:
                    pass
                    # (La logique de dessin se fait dans le bloc d'affichage ci-dessous)

    # **********************************************
    # *** 2. LOGIQUE D'AFFICHAGE ***
    # **********************************************
    screen.fill((0, 0, 0))

    if APP_STATE == "START_SCREEN":
        draw_start_screen(screen_width, screen_height)

    elif APP_STATE == "GAME_SCREEN":

        # 1. Dessiner le monde (Terrain 16x16)
        draw_world(screen_width, grid_bottom_y)

        # 2. --- Dessiner les éléments 8x8 et 32x32 PAR DESSUS ---
        WorldData = type('World', (object,), {
            'tile_size': TILE_SIZE,
            'camera_x': camera_x,
            'camera_y': camera_y,
            'INIT_TILE_SIZE': INIT_TILE_SIZE,
            'ELEMENT_GRID_SIZE': ELEMENT_GRID_SIZE,
            'TOOLBAR_HEIGHT': TOOLBAR_HEIGHT,
            'GRID_WIDTH': GRID_WIDTH,
            'GRID_HEIGHT': GRID_HEIGHT
        })
        # L'élément 5 est l'élément par défaut pour le dessin continu
        draw_elements(
            screen,
            WorldData,
            element_grid,
            TERRAIN_IMAGES_RAW,
            is_drawing and CURRENT_TERRAIN == 5,
            5
        )
        # ----------------------------------------------------

        # 3. Application du Pinceau (Dessin CONTINU - Terrain 16x16 uniquement)
        if is_drawing and CURRENT_TERRAIN < 5:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < grid_bottom_y:
                world_x = mouse_x + camera_x
                world_y = mouse_y + camera_y

                # Placement 16x16 (Terrain)
                grid_col = int(world_x // TILE_SIZE)
                grid_row = int(world_y // TILE_SIZE)

                if 0 <= grid_col < GRID_WIDTH and 0 <= grid_row < GRID_HEIGHT:
                    # Logique du pinceau 16x16
                    N = int(CURRENT_BRUSH)
                    start_offset = -(N // 2)
                    for dr in range(start_offset, start_offset + N):
                        for dc in range(start_offset, start_offset + N):
                            r = grid_row + dr
                            c = grid_col + dc
                            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                                world_grid[r][c] = CURRENT_TERRAIN

        # 4. Dessiner l'ui
        draw_toolbar(screen_width, grid_bottom_y)
        draw_minimap(screen_width, grid_bottom_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
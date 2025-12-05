# Fichier : jeu/worldManagement.py (CORRECTION INTÉGRALE)

import numpy as np
# Importation ABSOLUE/DIRECTE pour éviter l'erreur de package parent inconnu
from config_cg import *

class World:
    def __init__(self, initial_grid=None):
        # Grille de terrain (16x16)
        if initial_grid is None:
            self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int).tolist()
        else:
            self.grid = initial_grid if isinstance(initial_grid, list) else initial_grid.tolist()

        # Grille d'éléments (8x8)
        self.element_grid = np.zeros(
            (ELEMENT_GRID_HEIGHT, ELEMENT_GRID_WIDTH), dtype=int
        ).tolist()

        self.tile_size = INIT_TILE_SIZE
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.current_brush_size = 1
        self.current_terrain = 0

    # --- ZOOOM ET CAMÉRA ---
    def reset_camera(self):
        """Réinitialise la caméra et le zoom après un chargement."""
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.tile_size = INIT_TILE_SIZE

    def zoom_in(self):
        """Augmente le zoom, limité à 64.0."""
        self.tile_size = min(64.0, self.tile_size + 2.0)

    def zoom_out(self):
        """Diminue le zoom, limité à 4.0."""
        self.tile_size = max(4.0, self.tile_size - 2.0)

    def adjust_camera(self, screen_width, grid_bottom_y):
        """Ajuste et borne la caméra et le zoom en fonction de la taille de l'écran."""
        min_tile_size_x = screen_width / GRID_WIDTH
        min_tile_size_y = grid_bottom_y / GRID_HEIGHT
        self.tile_size = max(self.tile_size, min(min_tile_size_x, min_tile_size_y))
        self.tile_size = min(64.0, self.tile_size)

        max_camera_x = max(0.0, GRID_WIDTH * self.tile_size - screen_width)
        max_camera_y = max(0.0, GRID_HEIGHT * self.tile_size - grid_bottom_y)

        self.camera_x = max(0.0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0.0, min(self.camera_y, max_camera_y))

    # --- COORDONNÉES ET VUE ---
    def get_visible_tile_range(self, screen_width, grid_bottom_y):
        """Retourne les indices (row, col) des tuiles 16x16 visibles."""
        start_col = max(0, int(self.camera_x // self.tile_size))
        end_col = min(GRID_WIDTH, int((self.camera_x + screen_width) // self.tile_size + 1))
        start_row = max(0, int(self.camera_y // self.tile_size))
        end_row = min(GRID_HEIGHT, int((self.camera_y + grid_bottom_y) // self.tile_size + 1))
        return start_row, end_row, start_col, end_col

    def world_to_grid_16x16(self, world_x, world_y):
        """Convertit les coordonnées monde (pixels) en indices de grille 16x16."""
        grid_col = int(world_x // self.tile_size)
        grid_row = int(world_y // self.tile_size)
        return grid_row, grid_col

    def world_to_grid_8x8(self, world_x, world_y):
        """Convertit les coordonnées monde (pixels) en indices de grille 8x8."""
        cell_8x8_size = self.tile_size / ELEMENT_SCALE_FACTOR
        grid_col_el = int(world_x // cell_8x8_size)
        grid_row_el = int(world_y // cell_8x8_size)
        return grid_row_el, grid_col_el

    # --- LOGIQUE DE PEINTURE/PLACEMENT ---
    def paint_terrain(self, grid_row, grid_col, terrain_type):
        """Applique le pinceau (taille current_brush_size) au terrain 16x16."""
        N = self.current_brush_size
        offset = -(N // 2)
        for dr in range(offset, offset + N):
            for dc in range(offset, offset + N):
                r = grid_row + dr
                c = grid_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    self.grid[r][c] = terrain_type

    def place_element(self, world_x, world_y, element_type):
        """Place un élément (petit ou grand rocher) dans la grille 8x8 (clic unique)."""
        grid_row_el, grid_col_el = self.world_to_grid_8x8(world_x, world_y)

        if element_type == 5:
            if (0 <= grid_col_el < ELEMENT_GRID_WIDTH and
                    0 <= grid_row_el < ELEMENT_GRID_HEIGHT):
                if self.element_grid[grid_row_el][grid_col_el] == 0:
                    self.element_grid[grid_row_el][grid_col_el] = 5
                    return True

        elif element_type == 6:
            SIZE = BIG_ROCK_SIZE_ELEMENTS
            grid_col_el_start = grid_col_el
            grid_row_el_start = grid_row_el

            if not (0 <= grid_col_el_start <= ELEMENT_GRID_WIDTH - SIZE and
                    0 <= grid_row_el_start <= ELEMENT_GRID_HEIGHT - SIZE):
                return False

            can_place = True
            for r in range(grid_row_el_start, grid_row_el_start + SIZE):
                for c in range(grid_col_el_start, grid_col_el_start + SIZE):
                    if self.element_grid[r][c] != 0:
                        can_place = False
                        break
                if not can_place:
                    break

            if can_place:
                self.element_grid[grid_row_el_start][grid_col_el_start] = 6
                for r in range(grid_row_el_start, grid_row_el_start + SIZE):
                    for c in range(grid_col_el_start, grid_col_el_start + SIZE):
                        if r != grid_row_el_start or c != grid_col_el_start:
                            self.element_grid[r][c] = -1
                return True

        return False

    def erase_element(self, world_x, world_y):
        """Efface un élément 8x8 ou 32x32."""
        grid_row_el, grid_col_el = self.world_to_grid_8x8(world_x, world_y)

        if not (0 <= grid_col_el < ELEMENT_GRID_WIDTH and
                0 <= grid_row_el < ELEMENT_GRID_HEIGHT):
            return False

        element_val = self.element_grid[grid_row_el][grid_col_el]

        if element_val == 5:
            self.element_grid[grid_row_el][grid_col_el] = 0
            return True

        elif element_val == 6 or element_val == -1:
            SIZE = BIG_ROCK_SIZE_ELEMENTS
            anchor_r = -1
            anchor_c = -1

            # Recherche de l'ancre
            for dr in range(-SIZE + 1, 1):
                for dc in range(-SIZE + 1, 1):
                    r_check = grid_row_el + dr
                    c_check = grid_col_el + dc

                    if (0 <= r_check < ELEMENT_GRID_HEIGHT and
                            0 <= c_check < ELEMENT_GRID_WIDTH and
                            self.element_grid[r_check][c_check] == 6):
                        anchor_r = r_check
                        anchor_c = c_check
                        break
                if anchor_r != -1:
                    break

            if anchor_r != -1:
                # Effacement du bloc 4x4
                for r in range(anchor_r, anchor_r + SIZE):
                    for c in range(anchor_c, anchor_c + SIZE):
                        if 0 <= r < ELEMENT_GRID_HEIGHT and 0 <= c < ELEMENT_GRID_WIDTH:
                            self.element_grid[r][c] = 0
                return True

        return False
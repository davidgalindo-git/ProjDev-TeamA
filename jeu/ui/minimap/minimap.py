import pygame
import math
import jeu.globals as G

def draw_minimap(screen_width, grid_bottom_y):
    """Dessine la minimap en haut à droite et le rectangle de la vue."""
    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    minimap_x = screen_width - MAP_W - MARGIN
    minimap_y = MARGIN

    pygame.draw.rect(G.screen, (30, 30, 30),
                     (minimap_x - 2, minimap_y - 2, MAP_W + 4, MAP_H + 4),
                     border_radius=4)
    pygame.draw.rect(G.screen, (0, 0, 0),
                     (minimap_x, minimap_y, MAP_W, MAP_H))

    cell_w = MAP_W / G.GRID_WIDTH
    cell_h = MAP_H / G.GRID_HEIGHT

    # grille réduite
    for r in range(G.GRID_HEIGHT):
        for c in range(G.GRID_WIDTH):
            terrain = G.world_grid[r][c]
            color = G.COLORS.get(terrain, (255, 0, 255))
            px = int(minimap_x + c * cell_w)
            py = int(minimap_y + r * cell_h)
            G.screen.fill(
                color,
                (
                    px, py,
                    max(1, int(math.ceil(cell_w))),
                    max(1, int(math.ceil(cell_h)))
                )
            )

    # rectangle de vue
    view_cols = screen_width / G.TILE_SIZE
    view_rows = grid_bottom_y / G.TILE_SIZE

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = minimap_x + (G.camera_x / G.TILE_SIZE) * cell_w
    view_y = minimap_y + (G.camera_y / G.TILE_SIZE) * cell_h

    pygame.draw.rect(G.screen, (255, 0, 0),
                     (view_x, view_y, view_w, view_h), width=2)

def handle_minimap_click(mouse_pos, screen_width, grid_bottom_y):
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

    # vue
    view_cols = screen_width / G.TILE_SIZE
    view_rows = grid_bottom_y / G.TILE_SIZE

    cell_w = MAP_W / G.GRID_WIDTH
    cell_h = MAP_H / G.GRID_HEIGHT

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h

    view_x = mini_x + (G.camera_x / G.TILE_SIZE) * cell_w
    view_y = mini_y + (G.camera_y / G.TILE_SIZE) * cell_h

    # drag dans rectangle rouge
    if view_x <= mx <= view_x + view_w and view_y <= my <= view_y + view_h:
        G.minimap_dragging = True
        G.minimap_drag_offset = (mx - view_x, my - view_y)
        return True

    # clic simple = téléportation
    target_col = int(rel_x * G.GRID_WIDTH)
    target_row = int(rel_y * G.GRID_HEIGHT)

    scr_w, scr_h = G.screen.get_size()

    new_cam_x = (target_col + 0.5) * G.TILE_SIZE - scr_w / 2
    new_cam_y = (target_row + 0.5) * G.TILE_SIZE - (scr_h - G.TOOLBAR_HEIGHT) / 2

    max_camera_x = max(0, G.GRID_WIDTH * G.TILE_SIZE - scr_w)
    max_camera_y = max(0, G.GRID_HEIGHT * G.TILE_SIZE - (scr_h - G.TOOLBAR_HEIGHT))

    G.camera_x = max(0, min(new_cam_x, max_camera_x))
    G.camera_y = max(0, min(new_cam_y, max_camera_y))

    return True

def handle_minimap_drag(mouse_pos, screen_width, grid_bottom_y):
    if not G.minimap_dragging:
        return

    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    mini_x = screen_width - MAP_W - MARGIN
    mini_y = MARGIN

    mx, my = mouse_pos

    cell_w = MAP_W / G.GRID_WIDTH
    cell_h = MAP_H / G.GRID_HEIGHT

    view_x = mx - G.minimap_drag_offset[0]
    view_y = my - G.minimap_drag_offset[1]

    tile_col = (view_x - mini_x) / cell_w
    tile_row = (view_y - mini_y) / cell_h

    scr_w, scr_h = G.screen.get_size()

    new_cam_x = tile_col * G.TILE_SIZE
    new_cam_y = tile_row * G.TILE_SIZE

    max_camera_x = max(0, G.GRID_WIDTH * G.TILE_SIZE - scr_w)
    max_camera_y = max(0, G.GRID_HEIGHT * G.TILE_SIZE - (scr_h - G.TOOLBAR_HEIGHT))

    G.camera_x = max(0, min(new_cam_x, max_camera_x))
    G.camera_y = max(0, min(new_cam_y, max_camera_y))
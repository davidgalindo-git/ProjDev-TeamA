import pygame
import math

def draw_minimap(screen, world_grid, camera_x, camera_y, screen_width, grid_bottom_y, TILE_SIZE, COLORS):
    """Dessine la minimap en haut à droite et le rectangle de la vue."""
    GRID_HEIGHT = len(world_grid)
    GRID_WIDTH = len(world_grid[0])

    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    minimap_x = screen_width - MAP_W - MARGIN
    minimap_y = MARGIN

    pygame.draw.rect(screen, (30, 30, 30), (minimap_x - 2, minimap_y - 2, MAP_W + 4, MAP_H + 4), border_radius=4)
    pygame.draw.rect(screen, (0, 0, 0), (minimap_x, minimap_y, MAP_W, MAP_H))

    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    # grille minimap
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            color = COLORS.get(world_grid[r][c], (255, 0, 255))
            px = int(minimap_x + c * cell_w)
            py = int(minimap_y + r * cell_h)
            screen.fill(color, (px, py, max(1, int(cell_w)), max(1, int(cell_h))))

    # zone visible
    view_cols = screen_width / TILE_SIZE
    view_rows = grid_bottom_y / TILE_SIZE

    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = minimap_x + (camera_x / TILE_SIZE) * cell_w
    view_y = minimap_y + (camera_y / TILE_SIZE) * cell_h

    pygame.draw.rect(screen, (255, 0, 0), (view_x, view_y, view_w, view_h), width=2)

def handle_minimap_click(mouse_pos, screen, world_grid, camera_x, camera_y,
                         screen_width, grid_bottom_y, TILE_SIZE, TOOLBAR_HEIGHT):
    GRID_HEIGHT = len(world_grid)
    GRID_WIDTH = len(world_grid[0])

    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    mini_x = screen_width - MAP_W - MARGIN
    mini_y = MARGIN
    mx, my = mouse_pos

    # hors-zone minimap ?
    if not (mini_x <= mx <= mini_x + MAP_W and mini_y <= my <= mini_y + MAP_H):
        return None

    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    # rectangle de vue actuel
    view_cols = screen_width / TILE_SIZE
    view_rows = grid_bottom_y / TILE_SIZE
    view_w = view_cols * cell_w
    view_h = view_rows * cell_h
    view_x = mini_x + (camera_x / TILE_SIZE) * cell_w
    view_y = mini_y + (camera_y / TILE_SIZE) * cell_h

    # clic sur rectangle → activer drag
    if view_x <= mx <= view_x + view_w and view_y <= my <= view_y + view_h:
        drag_offset = (mx - view_x, my - view_y)
        return ("DRAG_START", drag_offset)

    # clic normal → téléportation caméra
    rel_x = (mx - mini_x) / MAP_W
    rel_y = (my - mini_y) / MAP_H

    target_col = int(rel_x * GRID_WIDTH)
    target_row = int(rel_y * GRID_HEIGHT)

    scr_w, scr_h = screen.get_size()
    new_cam_x = (target_col + 0.5) * TILE_SIZE - scr_w / 2
    new_cam_y = (target_row + 0.5) * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT) / 2

    max_cx = max(0, GRID_WIDTH * TILE_SIZE - scr_w)
    max_cy = max(0, GRID_HEIGHT * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT))

    camera_x = max(0, min(new_cam_x, max_cx))
    camera_y = max(0, min(new_cam_y, max_cy))

    return ("MOVE", camera_x, camera_y)

def handle_minimap_drag(mouse_pos, drag_offset, screen, world_grid,
                        TILE_SIZE, TOOLBAR_HEIGHT, screen_width, grid_bottom_y):
    GRID_HEIGHT = len(world_grid)
    GRID_WIDTH = len(world_grid[0])

    MAP_W = 200
    MAP_H = 160
    MARGIN = 10

    mini_x = screen_width - MAP_W - MARGIN
    mini_y = MARGIN
    mx, my = mouse_pos

    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT

    # nouvelle position du coin du rectangle
    view_x = mx - drag_offset[0]
    view_y = my - drag_offset[1]

    # converti en tuiles
    tile_col = (view_x - mini_x) / cell_w
    tile_row = (view_y - mini_y) / cell_h

    scr_w, scr_h = screen.get_size()

    new_cam_x = tile_col * TILE_SIZE
    new_cam_y = tile_row * TILE_SIZE

    max_cx = max(0, GRID_WIDTH * TILE_SIZE - scr_w)
    max_cy = max(0, GRID_HEIGHT * TILE_SIZE - (scr_h - TOOLBAR_HEIGHT))

    camera_x = max(0, min(new_cam_x, max_cx))
    camera_y = max(0, min(new_cam_y, max_cy))

    return (camera_x, camera_y)

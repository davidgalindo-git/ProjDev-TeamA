from jeu.main_david_old import *
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

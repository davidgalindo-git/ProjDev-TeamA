import pygame, math
from settings import GRID_WIDTH, GRID_HEIGHT
from world.state import world_grid, state
from settings import COLORS

def draw_minimap(screen, screen_width, grid_bottom_y):
    MAP_W = 200; MAP_H = 160; MARGIN = 10
    minimap_x = screen_width - MAP_W - MARGIN
    minimap_y = MARGIN
    pygame.draw.rect(screen, (30,30,30), (minimap_x-2, minimap_y-2, MAP_W+4, MAP_H+4), border_radius=4)
    pygame.draw.rect(screen, (0,0,0), (minimap_x, minimap_y, MAP_W, MAP_H))
    cell_w = MAP_W / GRID_WIDTH
    cell_h = MAP_H / GRID_HEIGHT
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            t = world_grid[r][c]
            col = COLORS.get(t, (255,0,255))
            px = int(minimap_x + c*cell_w); py = int(minimap_y + r*cell_h)
            screen.fill(col, (px, py, max(1,int(math.ceil(cell_w))), max(1,int(math.ceil(cell_h)))))
    # view rect
    tile_size = state["tile_size"]
    view_cols = screen_width / tile_size
    view_rows = grid_bottom_y / tile_size
    view_w = view_cols * cell_w; view_h = view_rows * cell_h
    view_x = minimap_x + (state["camera_x"]/tile_size)*cell_w
    view_y = minimap_y + (state["camera_y"]/tile_size)*cell_h
    pygame.draw.rect(screen, (255,0,0), (view_x, view_y, view_w, view_h), width=2)

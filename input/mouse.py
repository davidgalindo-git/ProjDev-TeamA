import pygame
from world.state import state, world_grid
from settings import GRID_WIDTH, GRID_HEIGHT, TOOLBAR_HEIGHT

def apply_brush(mx, my):
    cam_x = state["camera_x"]; cam_y = state["camera_y"]; tile = state["tile_size"]
    brush = int(state["current_brush"]); terrain = int(state["current_terrain"])
    # mouse coords are relative to screen; convert to world coords then to grid
    grid_x = int((mx + cam_x) // tile); grid_y = int((my + cam_y) // tile)
    # center brush
    start = -(brush//2)
    for dr in range(start, start+brush):
        for dc in range(start, start+brush):
            r = grid_y + dr; c = grid_x + dc
            if 0<=r<GRID_HEIGHT and 0<=c<GRID_WIDTH:
                world_grid[r][c] = terrain

def handle_mouse_event(event, screen_width, grid_bottom_y):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            mx,my = event.pos
            if my < grid_bottom_y:
                # click on world
                apply_brush(mx, my)
            else:
                # toolbar click handled in main
                pass
        elif event.button == 3:
            state["is_panning"] = True
            state["pan_start"] = event.pos
            state["mouse_start_cam"] = (state["camera_x"], state["camera_y"])
        elif event.button == 4:
            state["tile_size"] = min(64.0, state["tile_size"]+2.0)
        elif event.button == 5:
            state["tile_size"] = max(4.0, state["tile_size"]-2.0)
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 3:
            state["is_panning"] = False
    elif event.type == pygame.MOUSEMOTION:
        if state["is_panning"]:
            mx,my = event.pos
            dx = mx - state["pan_start"][0]; dy = my - state["pan_start"][1]
            # subtract dx to pan in direction of mouse drag
            state["camera_x"] = state["mouse_start_cam"][0] - dx
            state["camera_y"] = state["mouse_start_cam"][1] - dy

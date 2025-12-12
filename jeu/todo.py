# Fonctions à implémenter
import globals as G
# Screen
#screen
#APP_STATE
#camera_x
#camera_y
def get_dimensions():
    scr_w, scr_h = G.screen.get_size()

    G.screen_width = float(scr_w)
    G.screen_height = float(scr_h)

    G.grid_bottom_y = scr_h - G.TOOLBAR_HEIGHT


def toggle_fullscreen():
    pass
def handle_start_screen_click():
    pass
def draw_start_screen():
    pass

# World creation/management
def draw_world():
    pass
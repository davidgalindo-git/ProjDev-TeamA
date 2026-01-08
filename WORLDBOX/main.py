import pygame
import sys
import config as cfg
from worldManagement import World
from draw_world import draw_world, COULEURS
from ui import draw_toolbar, get_toolbar_click
from minimap import draw_minimap, is_minimap_clicked, update_camera_from_minimap
from timer import update_timer, draw_timer_ui, handle_timer_logic
from save_system import SaveLoadSystem
from assets import AssetManager

# On initialise le gestionnaire d'assets globalement


def menu(screen, sl_system):
    # ... (Le code du menu reste identique jusqu'au retour du world) ...
    font = pygame.font.SysFont("Arial", 32, bold=True)
    btn_vide = pygame.Rect(cfg.DEFAULT_WINDOW_WIDTH // 2 - 150, 250, 300, 50)
    btn_aleat = pygame.Rect(cfg.DEFAULT_WINDOW_WIDTH // 2 - 150, 330, 300, 50)
    btn_load = pygame.Rect(cfg.DEFAULT_WINDOW_WIDTH // 2 - 150, 410, 300, 50)

    world = None
    while world is None:
        screen.fill((30, 30, 35))
        for btn, txt in zip([btn_vide, btn_aleat, btn_load], ["VIDE", "ALÉATOIRE", "CHARGER SAVE"]):
            pygame.draw.rect(screen, (80, 80, 80), btn, border_radius=10)
            surf = font.render(txt, True, (255, 255, 255))
            screen.blit(surf, surf.get_rect(center=btn.center))
        sl_system.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if sl_system.load_menu_active:
                res = sl_system.handle_event(event, None)
                if res == "LOAD_SUCCESS":
                    world = World(mode="vide")
                    sl_system.apply_to_world(world)
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_vide.collidepoint(event.pos): world = World(mode="vide")
                if btn_aleat.collidepoint(event.pos): world = World(mode="aleatoire")
                if btn_load.collidepoint(event.pos): sl_system.open_load_menu()
    return world


def main():
    pygame.init()
    am = AssetManager()
    screen = pygame.display.set_mode((cfg.DEFAULT_WINDOW_WIDTH, cfg.DEFAULT_WINDOW_HEIGHT))
    pygame.display.set_caption("Sandbox World Creator")
    clock = pygame.time.Clock()
    font_ui = pygame.font.SysFont("Arial", 18, bold=True)

    sl_system = SaveLoadSystem(font_ui)
    world = menu(screen, sl_system)

    selected_terrain = 1
    brush_size = 1
    is_painting = False
    is_panning = False
    is_dragging_minimap = False
    last_mouse_pos = (0, 0)

    while True:
        dt = clock.tick(60) / 1000.0
        update_timer(dt)

        scr_w, scr_h = screen.get_size()
        limit_y = scr_h - cfg.TOOLBAR_HEIGHT
        min_tile_size = max(scr_w / cfg.GRID_WIDTH, limit_y / cfg.GRID_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

            m_pos = getattr(event, 'pos', None)

            if sl_system.handle_event(event, world):
                is_painting = False
                continue

            if m_pos and handle_timer_logic(m_pos, is_click=(event.type == pygame.MOUSEBUTTONDOWN)):
                is_painting = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if is_minimap_clicked(event.pos):
                    is_dragging_minimap = True
                    update_camera_from_minimap(event.pos, world, scr_w, limit_y)
                    is_painting = False
                elif get_toolbar_click(event.pos, scr_h):
                    res = get_toolbar_click(event.pos, scr_h)
                    if res[0] == "terrain":
                        selected_terrain = res[1]
                    else:
                        brush_size = res[1]
                    is_painting = False
                else:
                    if event.button == 1: is_painting = True
                    if event.button == 3:
                        is_panning = True
                        last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                is_painting = False
                is_panning = False
                is_dragging_minimap = False
                cfg.day_bar_dragging = False
                cfg.time_bar_dragging = False

            elif event.type == pygame.MOUSEWHEEL:
                # LOGIQUE CRUE : On change la taille ET on vide le cache
                # Sinon la RAM va exploser avec des milliers d'images de tailles différentes
                world.tile_size = max(min_tile_size, min(128, world.tile_size + event.y * 4))
                am.cache.clear()

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_minimap:
                    update_camera_from_minimap(event.pos, world, scr_w, limit_y)
                elif cfg.day_bar_dragging or cfg.time_bar_dragging:
                    handle_timer_logic(event.pos)
                elif is_panning:
                    dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                    world.camera_x -= dx
                    world.camera_y -= dy
                    last_mouse_pos = event.pos

        # LOGIQUE DE PEINTURE
        mx, my = pygame.mouse.get_pos()
        ui_hover = (
                is_minimap_clicked((mx, my)) or
                cfg.timer_button.collidepoint(mx, my) or
                cfg.TIME_BAR_RECT.collidepoint(mx, my) or
                cfg.DAY_BAR_RECT.collidepoint(mx, my) or
                sl_system.save_button.collidepoint(mx, my) or
                my >= limit_y
        )

        if is_painting and not ui_hover and not sl_system.input_active:
            gx = int((mx + world.camera_x) // world.tile_size)
            gy = int((my + world.camera_y) // world.tile_size)
            off = brush_size // 2
            for r in range(gy - off, gy - off + brush_size):
                for c in range(gx - off, gx - off + brush_size):
                    if 0 <= r < cfg.GRID_HEIGHT and 0 <= c < cfg.GRID_WIDTH:
                        world.grid[r][c] = selected_terrain

        # CAMÉRA CLAMPING
        world.camera_x = max(0, min(world.camera_x, cfg.GRID_WIDTH * world.tile_size - scr_w))
        world.camera_y = max(0, min(world.camera_y, cfg.GRID_HEIGHT * world.tile_size - limit_y))

        # 5. RENDU (C'est ici que la magie opère)
        screen.fill((0, 0, 0))

        # On passe 'am' à draw_world pour qu'il puisse dessiner les textures animées
        draw_world(screen, world, am)

        draw_toolbar(screen, selected_terrain, brush_size)
        draw_timer_ui(screen, font_ui)
        draw_minimap(screen, world, COULEURS)
        sl_system.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
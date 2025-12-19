import pygame
import os
import json


class LoadManager:
    def __init__(self, font):
        self.font = font
        self.base_dir = "MyWorlds"
        self.active = False
        self.files = []
        self.selected_world_data = None
        self.overlay_rect = pygame.Rect(0, 0, 400, 500)

    def open_menu(self):
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.files = [f for f in os.listdir(self.base_dir) if f.endswith('.json')]
        self.active = True

    def draw(self, screen):
        if not self.active: return

        screen_w, screen_h = screen.get_size()
        self.overlay_rect.center = (screen_w // 2, screen_h // 2)

        # Draw Background Overlay
        pygame.draw.rect(screen, (30, 30, 30), self.overlay_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.overlay_rect, 2, border_radius=10)

        # Title
        title = self.font.render("Choisir un monde", True, (255, 255, 255))
        screen.blit(title, (self.overlay_rect.x + 20, self.overlay_rect.y + 20))

        # List Files
        for i, filename in enumerate(self.files):
            file_rect = pygame.Rect(self.overlay_rect.x + 20, self.overlay_rect.y + 70 + (i * 45), 360, 40)
            pygame.draw.rect(screen, (60, 60, 60), file_rect, border_radius=5)

            name_surf = self.font.render(filename, True, (255, 255, 255))
            screen.blit(name_surf, (file_rect.x + 10, file_rect.y + 10))

        # Close hint
        hint = self.font.render("ESC to cancel", True, (150, 150, 150))
        screen.blit(hint, (self.overlay_rect.centerx - hint.get_width() // 2, self.overlay_rect.bottom - 30))

    def handle_event(self, event):
        if not self.active: return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if clicked a file
            for i, filename in enumerate(self.files):
                file_rect = pygame.Rect(self.overlay_rect.x + 20, self.overlay_rect.y + 70 + (i * 45), 360, 40)
                if file_rect.collidepoint(mouse_pos):
                    return self.load_file(filename)

            # Close if clicked outside
            if not self.overlay_rect.collidepoint(mouse_pos):
                self.active = False
                return True
        return True

    def load_file(self, filename):
        path = os.path.join(self.base_dir, filename)
        try:
            with open(path, "r") as f:
                self.selected_world_data = json.load(f)
            self.active = False
            return "LOAD_SUCCESS"
        except Exception as e:
            print(f"Load Error: {e}")
            return False
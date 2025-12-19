import pygame
import json
import os


class SaveManager:
    def __init__(self, font):
        self.font = font
        self.button_rect = pygame.Rect(0, 0, 150, 40)
        self.input_active = False
        self.filename = "my_world"
        self.feedback_timer = 0

    def draw(self, screen):
        screen_w, screen_h = screen.get_size()
        # Relative positioning to stay safe during refactoring
        toolbar_h = 60
        self.button_rect.bottomright = (screen_w - 20, screen_h - toolbar_h - 20)

        # 1. Draw the Button or the Input Box
        if not self.input_active:
            color = (100, 255, 100) if self.feedback_timer > 0 else (70, 70, 70)
            text = "SAVED!" if self.feedback_timer > 0 else "SAVE WORLD"
            pygame.draw.rect(screen, color, self.button_rect, border_radius=5)
        else:
            # Drawing the input box
            pygame.draw.rect(screen, (40, 40, 40), self.button_rect, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), self.button_rect, 2, border_radius=5)
            text = self.filename + "|"  # Cursor indicator

        # 2. Render Text
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.button_rect.center)
        screen.blit(text_surf, text_rect)

        # 3. Handle feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1

    def handle_event(self, event, world_grid):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.input_active = True
                return True
            else:
                self.input_active = False  # Cancel if clicking elsewhere

        if self.input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.save_to_disk(world_grid)
                self.input_active = False
                self.feedback_timer = 90  # 1.5 seconds at 60fps
            elif event.key == pygame.K_BACKSPACE:
                self.filename = self.filename[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.input_active = False
            else:
                # Limit filename length and allow only alphanumeric/underscore
                if len(self.filename) < 15 and event.unicode.isalnum() or event.unicode == "_":
                    self.filename += event.unicode
            return True  # Consume keys so they don't trigger other game actions

        return False

    def save_to_disk(self, world_grid):
        # Create MyWorlds folder if it doesn't exist
        if not os.path.exists("MyWorlds"):
            os.makedirs("MyWorlds")

        full_path = f"MyWorlds/{self.filename}.json"
        try:
            with open(full_path, "w") as f:
                json.dump(world_grid, f)
            print(f"Saved: {full_path}")
        except Exception as e:
            print(f"Error: {e}")
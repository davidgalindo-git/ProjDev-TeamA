import pygame
import json
import os
import config as cfg


class SaveLoadSystem:
    def __init__(self, font):
        self.font = font
        self.save_button = pygame.Rect(0, 0, 160, 40)
        self.input_active = False
        self.filename = "mon_monde"
        self.feedback_timer = 0

        # Menu de chargement
        self.load_menu_active = False
        self.files = []
        self.overlay_rect = pygame.Rect(0, 0, 400, 500)

        # Stockage temporaire pour le transfert
        self.temp_grid = None
        self.temp_tile_size = 32

    def draw(self, screen):
        scr_w, scr_h = screen.get_size()

        # 1. Bouton Sauvegarder (Bas droite, au dessus de la barre d'outils)
        self.save_button.bottomright = (scr_w - 20, scr_h - cfg.TOOLBAR_HEIGHT - 20)

        if not self.input_active:
            color = (50, 200, 50) if self.feedback_timer > 0 else (70, 70, 70)
            txt = "SAUVEGARDÉ !" if self.feedback_timer > 0 else "SAUVEGARDER"
            pygame.draw.rect(screen, color, self.save_button, border_radius=5)
        else:
            pygame.draw.rect(screen, (40, 40, 40), self.save_button, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), self.save_button, 2, border_radius=5)
            txt = self.filename + "|"

        surf = self.font.render(txt, True, (255, 255, 255))
        screen.blit(surf, surf.get_rect(center=self.save_button.center))

        if self.feedback_timer > 0: self.feedback_timer -= 1

        # 2. Menu de Chargement (Overlay)
        if self.load_menu_active:
            self.overlay_rect.center = (scr_w // 2, scr_h // 2)
            pygame.draw.rect(screen, (30, 30, 30), self.overlay_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), self.overlay_rect, 2, border_radius=10)

            title = self.font.render("CHARGER UN MONDE", True, (255, 255, 255))
            screen.blit(title, (self.overlay_rect.x + 20, self.overlay_rect.y + 20))

            for i, name in enumerate(self.files):
                # On définit précisément la zone de clic pour chaque fichier
                file_rect = pygame.Rect(self.overlay_rect.x + 20, self.overlay_rect.y + 70 + (i * 45), 360, 40)
                pygame.draw.rect(screen, (60, 60, 60), file_rect, border_radius=5)
                name_surf = self.font.render(name, True, (255, 255, 255))
                screen.blit(name_surf, (file_rect.x + 10, file_rect.y + 10))

    def handle_event(self, event, world):
        # Menu chargement actif
        if self.load_menu_active:
            # Escape ferme le menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.load_menu_active = False
                return True

            # Gestion du clic pour le chargement du monde (clic sur un nom)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, name in enumerate(self.files):
                    file_rect = pygame.Rect(self.overlay_rect.x + 20, self.overlay_rect.y + 70 + (i * 45), 360, 40)
                    if file_rect.collidepoint(event.pos):
                        self.load_world_data(name)
                        self.load_menu_active = False
                        return "LOAD_SUCCESS"  # Prévient la boucle principale du jeu qu'il faut rafraîchir l'affichage

                if not self.overlay_rect.collidepoint(event.pos):
                    self.load_menu_active = False
            return True

        # Input de nom de fichier actif
        if self.input_active:
            if event.type == pygame.KEYDOWN:
                # Return valide la sauvegarde
                if event.key == pygame.K_RETURN:
                    self.save_world_to_disk(world)
                    self.input_active = False
                    self.feedback_timer = 90
                # Backspace efface le dernier caractère
                elif event.key == pygame.K_BACKSPACE:
                    self.filename = self.filename[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                else:
                    if len(self.filename) < 15 and (event.unicode.isalnum() or event.unicode == "_"):
                        self.filename += event.unicode
                return True

            if event.type == pygame.MOUSEBUTTONDOWN and not self.save_button.collidepoint(event.pos):
                self.input_active = False
            return True

        # Clic sur le bouton Sauvegarder
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.save_button.collidepoint(event.pos):
                self.input_active = True
                return True

        return False

    def save_world_to_disk(self, world):
        try:
            # Dossier de sauvegardes
            if not os.path.exists("Saves"): os.makedirs("Saves")

            # Correction crash : On vérifie si c'est du Numpy ou une liste pour convertir en liste
            grid_to_save = world.grid.tolist() if hasattr(world.grid, 'tolist') else world.grid

            data = {
                "grid": grid_to_save,
                "hours": cfg.world_hours,
                "days": cfg.world_days,
                "tile_size": world.tile_size
            }
            with open(f"Saves/{self.filename}.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def open_load_menu(self):
        if not os.path.exists("Saves"): os.makedirs("Saves")
        self.files = [f for f in os.listdir("Saves") if f.endswith('.json')]
        self.load_menu_active = True

    def load_world_data(self, filename):
        """Lit le fichier et stocke les variables en tampon en mettant à jour les globales."""
        try:
            with open(f"Saves/{filename}", "r") as f:
                data = json.load(f)
                self.temp_grid = data["grid"]
                cfg.world_hours = data["hours"]
                cfg.world_days = data["days"]
                self.temp_tile_size = data["tile_size"]
        except Exception as e:
            print(f"Erreur lecture : {e}")

    def apply_to_world(self, world):
        """Injecte les données tampon dans le monde réel."""
        if self.temp_grid is not None:
            world.grid = self.temp_grid
            world.tile_size = self.temp_tile_size
            self.temp_grid = None  # Reset de la variable temporaire
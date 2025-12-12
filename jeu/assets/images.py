import pygame
import jeu.globals as G

def update_terrain_images():
    # Vérifie si le redimensionnement est nécessaire (taille non définie ou différente)
    current_size = G.TERRAIN_IMAGES.get(0).get_size()[0] if 0 in G.TERRAIN_IMAGES else -1

    if current_size != int(G.TILE_SIZE) and G.TERRAIN_IMAGES_RAW:  # Ajout de la vérification TERRAIN_IMAGES_RAW
        new_images = {}
        for terrain_type, raw_img in G.TERRAIN_IMAGES_RAW.items():
            # Redimensionne l'image brute à la G.TILE_SIZE actuelle
            new_images[terrain_type] = pygame.transform.scale(
                raw_img, (int(G.TILE_SIZE), int(G.TILE_SIZE))
            )
        G.TERRAIN_IMAGES = new_images
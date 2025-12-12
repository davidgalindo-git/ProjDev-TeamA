import pygame
import sys
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

def load_all_assets():
    """Charge toutes les images brutes. Retourne le dictionnaire des images RAW."""
    G.TERRAIN_IMAGES = {
        0: "water.png", 1: "grass.png", 2: "dirt.png", 3: "sand.png",
        4: "stone.png", 5: "S_rock1.png", 6: "B_rock.png",
    }
    G.TERRAIN_IMAGES_RAW = {}
    try:
        for terrain_id, filename in G.TERRAIN_IMAGES.items():
            path = G.ASSETS_PATH + filename
            G.TERRAIN_IMAGES_RAW[terrain_id] = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Erreur de chargement d'image. Vérifiez le dossier '{G.ASSETS_PATH}'. Erreur: {e}")
        sys.exit()
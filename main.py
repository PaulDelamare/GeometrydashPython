import pygame
from pygame.locals import *
from game import *  # Importer toutes les classes et fonctions depuis game.py
from player_ai import PlayerAI  # Importer la classe PlayerAI de player_ai.py
import config  # Importer la configuration

# Initialiser Pygame
pygame.init()

# Définir la taille de la fenêtre
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))  # Utiliser config.WIDTH et config.HEIGHT
pygame.display.set_caption('Plateforme avec Pygame')

# Charger les images après l'initialisation de l'affichage
load_images()

# Charger l'image de fond
bg_image = pygame.image.load("assets/bg.png").convert()
bg_image = pygame.transform.scale(bg_image, (config.WIDTH, config.HEIGHT))  # Ajuster à la taille de la fenêtre

# Charger la carte
level = load_level('level_1.csv')  # Remplacer par le chemin correct de votre niveau
obstacles = generate_obstacles(level)

# Créer le joueur
player = Player()

# Créer un groupe de sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(*obstacles)

# Calculer la largeur du niveau
level_width = len(level[0]) * TILE_SIZE  # Largeur du niveau

# Créer la caméra
camera = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)  # Utiliser config.WIDTH et config.HEIGHT

# Boucle de jeu
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.jump()  # Le joueur saute si la touche espace est appuyée

    # Mettre à jour les sprites (le joueur et les obstacles)
    all_sprites.update(obstacles)

    # Mettre à jour la caméra pour suivre le joueur
    camera.centerx = player.rect.centerx
    camera.x = max(0, camera.x)
    camera.x = min(camera.x, level_width - config.WIDTH)

    # Dessiner le fond
    screen.blit(bg_image, (0, 0))

    # Dessiner les sprites
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))

    # Actualiser l'affichage
    pygame.display.flip()

    # Limiter les FPS
    clock.tick(60)

pygame.quit()

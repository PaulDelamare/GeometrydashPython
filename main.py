import pygame
from pygame.locals import *
from game import *  # Importer toutes les classes et fonctions depuis game.py
from player_ai import PlayerAI  # Importer la classe PlayerAI de player_ai.py
import config  # Importer la configuration
import random
import numpy as np

# Initialiser Pygame
pygame.init()

# Définir la taille de la fenêtre
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))  # Utiliser config.WIDTH et config.HEIGHT
pygame.display.set_caption('Geometry Dash avec IA et Mode Manuel')

# Charger les images après l'initialisation de l'affichage
load_images()

# Charger l'image de fond
bg_image = pygame.image.load("assets/bg.png").convert()
bg_image = pygame.transform.scale(bg_image, (config.WIDTH, config.HEIGHT))  # Ajuster à la taille de la fenêtre

# Charger la carte
level = load_level('level_1.csv')  # Remplacer par le chemin correct de votre niveau
obstacles = generate_obstacles(level)

# Créer un groupe de sprites
all_sprites = pygame.sprite.Group()

# Calculer la largeur du niveau
level_width = len(level[0]) * TILE_SIZE  # Largeur du niveau

# Créer la caméra
camera = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)  # Utiliser config.WIDTH et config.HEIGHT

# Boucle de jeu
clock = pygame.time.Clock()

# Hyperparamètres Q-Learning
ACTIONS = [0, 1]  # Actions possibles : 0 = ne rien faire, 1 = sauter
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EPSILON = 1.0
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01

# Q-Table
Q = {}

def initialize_q_table():
    """Initialise une Q-table pour tous les états possibles."""
    for distance in range(0, 1500, 100):
        for height in range(0, 300, 50):
            for player_y in range(0, 400, 50):
                state = (distance, height, player_y)
                Q[state] = [0, 0]  # Initialisation à zéro pour chaque action

initialize_q_table()

def get_state(player, obstacles):
    """Retourne un état simplifié basé sur la position du joueur et le premier obstacle."""
    if obstacles:
        first_obstacle = obstacles[0]  # On prend le premier obstacle
        obstacle_distance = first_obstacle.rect.x - player.rect.x
        obstacle_height = first_obstacle.rect.height
    else:
        obstacle_distance = 1000  # Une valeur par défaut
        obstacle_height = 0

    return (obstacle_distance, obstacle_height, player.rect.y)

def manual_mode():
    """Lancer le mode manuel."""
    player = Player()
    all_sprites.add(player)
    all_sprites.add(*obstacles)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()  # Le joueur saute si la touche espace est appuyée

        # Mettre à jour les sprites
        all_sprites.update(obstacles)

        # Mettre à jour la caméra pour suivre le joueur
        camera.centerx = player.rect.centerx
        camera.x = max(0, camera.x)
        camera.x = min(camera.x, level_width - 800)

        # Dessiner le fond
        screen.blit(bg_image, (0, 0))

        # Dessiner les sprites
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))

        # Actualiser l'affichage
        pygame.display.flip()

        # Limiter les FPS
        clock.tick(60)

def main_menu():
    """Afficher le menu principal et choisir le mode."""
    font = pygame.font.Font(None, 36)
    running = True

    while running:
        screen.fill((0, 0, 0))
        title_text = font.render("Geometry Dash - Choisissez un mode", True, (255, 255, 255))
        manual_text = font.render("1. Mode Manuel", True, (255, 255, 255))
        ai_text = font.render("2. Mode IA (Q-Learning)", True, (255, 255, 255))
        screen.blit(title_text, (config.WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(manual_text, (config.WIDTH // 2 - manual_text.get_width() // 2, 300))
        screen.blit(ai_text, (config.WIDTH // 2 - ai_text.get_width() // 2, 350))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    manual_mode()  # Mode manuel
                elif event.key == pygame.K_2:
                    manual_mode()  # Mode manuel

if __name__ == "__main__":
    main_menu()  # Afficher le menu principal
    pygame.quit()  # Quitter Pygame

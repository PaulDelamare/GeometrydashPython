# config.py
import pygame
# Dimensions de l'écran
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Vitesse du jeu
FPS = 60

# Taille d'une tuile (tile)
TILE_SIZE = 40

# Vitesse de déplacement des obstacles
OBSTACLE_SPEED = 8

# Couleur
WHITE = (255, 255, 255)

# Initialise Pygame
pygame.init()

# Définir la taille de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Utiliser config.WIDTH et config.HEIGHT
pygame.display.set_caption('Geometry Dash\'ier avec IA et Mode Manuel')

spike_image = pygame.image.load("assets/spike.png").convert_alpha()
# Redimensionner le spike
spike_image_size = pygame.transform.scale(spike_image, (TILE_SIZE, TILE_SIZE))

player_image = pygame.image.load("assets/player.png").convert_alpha()
# Redimensionner le spike
player_image_size = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))

block_image = pygame.image.load("assets/block_1.png").convert_alpha()
# Redimensionner le spike
block_image_size = pygame.transform.scale(block_image, (TILE_SIZE, TILE_SIZE))


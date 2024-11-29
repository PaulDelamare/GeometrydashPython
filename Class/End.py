# Import Dépendances
import pygame

# Import Variable
from config import TILE_SIZE, OBSTACLE_SPEED

class End(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Définir les dimensions de l'objet "End"
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        # Créer une image (un carré rouge)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))  # Remplit le carré avec une couleur rouge (RGB)

        # Définir le rectangle englobant pour le positionnement
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def move(self):
        """
        Déplace le bout de niveau vers la gauche d'une distance définie par OBSTACLE_SPEED.
        """
        self.rect.x -= OBSTACLE_SPEED


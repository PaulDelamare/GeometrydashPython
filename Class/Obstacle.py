# Import Dependances
import pygame

# Import Variable
from config import block_image_size, OBSTACLE_SPEED

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = block_image_size
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def move(self):
        """
        Rapproche le block vers la gauche (le joueur ne bouge pas ce sont les obstacles)
        """
        
        self.rect.x -= OBSTACLE_SPEED
    
    # Dessine le block
    def draw(self, screen):
        """
        Dessine l'obstacle.
        
        :param screen: L' cran sur lequel l'obstacle sera dessin .
        :type screen: pygame.Surface
        """

        screen.blit(self.image, self.rect)

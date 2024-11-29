# Import Dependances
import pygame

# Import Variable
from config import TILE_SIZE, spike_image_size, OBSTACLE_SPEED

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Redimensionner le spike
        self.image = spike_image_size
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Créer une surface pour le masque triangulaire
        self.mask = pygame.mask.Mask((TILE_SIZE, TILE_SIZE), True)  # Créer un masque de la même taille que l'image

        # Remplir le masque avec un triangle pointant vers le haut
        # (on va remplir une surface triangulaire)
        for x in range(TILE_SIZE):
            for y in range(TILE_SIZE):
                # La condition pour remplir un triangle pointant vers le haut
                if y <= (-x + TILE_SIZE):  # Crée un triangle équilatéral inversé
                    self.mask.set_at((x, y), 1)  # Définir les pixels du masque comme "1"
    
    # Rapproche le spike vers la gauche
    def move(self):
        
        """
        Déplace le spike vers la gauche d'une distance définie par OBSTACLE_SPEED.
        """
        self.rect.x -= OBSTACLE_SPEED
    
    # Verifie si le joueur touche le spike
    def check_collision(self, player_rect):
        """Verifie si le joueur est en collision avec le spike.
        Return True si le joueur est en collision avec le spike, False sinon.
        """
        
        return self.rect.colliderect(player_rect)
    
    # Dessine le spike
    def draw(self, screen):
        """
        Dessine le spike sur l'écran.
        
        :param screen: L'écran sur lequel le spike sera dessiné.
        :type screen: pygame.Surface
        """
        screen.blit(self.image, self.rect)

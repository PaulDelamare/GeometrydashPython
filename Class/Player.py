# Import Dependances
import pygame
import sys

# Import Class
from Class.Spike import  Spike

# Import Variable
from config import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, player_image_size

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        try:
            self.image = pygame.image.load("assets/player.png")
        except pygame.error as e:
            # print(f"Erreur : Impossible de charger player.png : {e}")
            sys.exit()

        # self.image = pygame.image.load("assets/player.png").convert_alpha()
        # Redimensionner le joueur
        self.image = player_image_size
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100  # Le joueur au bas de l'écran
        
        self.rect.bottom = self.rect.y + TILE_SIZE - 10
        self.gravity = 0
        self.is_jumping = True
        super().__init__()
        self.velocity = 0  # Vitesse verticale (pour le saut)
        self.on_ground = False  # Si le joueur est sur le sol

    def jump(self):
        """Permet au joueur de sauter s'il est sur le sol."""
        if self.on_ground:  # Le joueur ne peut sauter que s'il est sur le sol
            self.velocity = -15  # La vitesse du saut est négative (vers le haut)
            self.on_ground = False  # Le joueur n'est plus sur le sol pendant le saut

    def move(self, obstacles):
        """        
        Si le joueur touche un obstacle, il est arrêté et mis sur le sol.
        Si le joueur touche un spike, il meurt et le jeu s'arrête.
        """

        self.on_ground = False  # Réinitialise la vérification du sol

        # Appliquer la gravité
        self.velocity += 1
        # Mettre à jour la position verticale
        self.rect.y += self.velocity 

        # Vérifier la collision avec le sol ou les obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):  # Si le joueur touche un obstacle
                if isinstance(obstacle, Spike):  # Vérifier si l'obstacle est un pique (spike)
                    # Si le joueur touche un pic, il meurt ou est arrêté
                    self.is_running = False
                    return False
                
                if self.velocity > 0:  # Si le joueur tombe
                    self.rect.bottom = obstacle.rect.top  # Ajuster la position pour que le joueur ne passe pas à travers l'obstacle
                    self.velocity = 0  # Stopper le mouvement vertical
                    self.on_ground = True  # Le joueur est maintenant sur le sol


        # Empêcher le joueur de passer sous le sol
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity = 0  # Arrêter la chute

    # Dessine le bloc joueur
    def draw(self, screen):
        """
        Dessine le joueur sur l'écran donné.

        :param screen: L'écran sur lequel le joueur sera dessiné.
        :type screen: pygame.Surface
        """
        screen.blit(self.image, self.rect)

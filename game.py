import pygame
import csv
from pygame.locals import *

# Définir les constantes
TILE_SIZE = 40  # Taille de chaque case en pixels
GRAVITY = 0.5  # Gravité
JUMP_STRENGTH = 10  # Force du saut

# Variables pour les images (elles seront chargées plus tard)
player_image = None
block_image = None
spike_image = None

# Classe pour l'obstacle
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Classe pour le joueur
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image  # L'image du joueur
        self.original_image = player_image  # Image sans rotation
        self.rect = self.image.get_rect()
        self.start_x = 100  # Position initiale en x
        self.start_y = 100  # Position initiale en y
        self.reset()  # Initialisation complète

    def reset(self):
        """Réinitialise le joueur à sa position de départ."""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vel_x = 7  # Vitesse horizontale
        self.vel_y = 0  # Vitesse verticale
        self.rotation_angle = 0  # Angle de rotation
        self.on_ground = False  # Le joueur n'est pas au sol
        self.image = self.original_image  # Image sans rotation

    def die(self):
        """Réinitialise le joueur lorsqu'il touche un spike."""
        print("Le joueur est mort et réinitialisé !")  # Message de débogage
        self.reset()  # Réinitialise les positions et l'état du joueur

    def jump(self):
        print(self.rect)
        """Permet au joueur de sauter si il est au sol."""
        if self.on_ground:  # Le saut est autorisé seulement si le joueur est au sol
            self.vel_y = -JUMP_STRENGTH  # Applique une force vers le haut
            self.on_ground = False  # Le joueur quitte le sol

    def update(self, obstacles):
        """Met à jour la position du joueur et gère la rotation en l'air."""
        self.on_ground = False

        # Mouvement horizontal constant
        self.rect.x += self.vel_x

        # Appliquer la gravité
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        if self.rect.y > 600:
            print("Le joueur est à y = 100, il meurt !")
            self.die()  # Réinitialise le joueur si la condition est remplie

        # Vérifier les collisions avec les obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):  # Vérifier la collision avec le rect de l'obstacle
                if isinstance(obstacle, Obstacle):  # Collision avec un bloc solide
                    if self.vel_y > 0:  # Collision verticale (chute)
                        self.rect.bottom = obstacle.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        
                        if self.vel_x > 0 and self.rect.right > obstacle.rect.left and self.rect.left < obstacle.rect.left:
                            # Si le joueur se déplace vers la droite et touche un obstacle à gauche
                            print(f"Contact latéral avec obstacle à gauche : {obstacle.rect}")
                            
                            # Vérifier s'il touche également le dessus de cet obstacle
                            if self.rect.bottom != obstacle.rect.top or self.rect.bottom <= obstacle.rect.top :
                                print(f"Contact avec le haut de l'obstacle à {obstacle.rect.top}")
                                self.die()  # Le joueur se réinitialise
                            
                elif isinstance(obstacle, Spike):  # Collision avec un spike
                    # Vérification de la collision entre le masque du joueur et celui du spike
                    if pygame.sprite.collide_mask(self, obstacle):  # Test de la collision par masque
                        self.die()  # Réinitialise le joueur en cas de collision avec un spike

        # Appliquer la rotation uniquement en l'air
        if not self.on_ground:
            self.rotation_angle -= 10  # Diminue l'angle pour tourner dans l'autre sens
            self.rotation_angle %= 360  # Garde l'angle entre 0 et 359
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        else:
            self.image = self.original_image  # Remet l'image droite
            self.rotation_angle = 0  # Réinitialise l'angle de rotation

            # Si le joueur est au sol et la barre d'espace est maintenue, il saute à nouveau
            keys = pygame.key.get_pressed()
            if keys[K_SPACE]:  # Si la barre d'espace est enfoncée
                self.jump()  # Effectuer un saut immédiatement


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = spike_image  # L'image du spike
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

# Fonction pour charger la carte depuis un fichier CSV
def load_level(filename):
    level = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            level.append(row)
    return level

# Fonction pour générer les obstacles
def generate_obstacles(level):
    obstacles = []
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            if cell == '0':  # Bloc solide
                obstacles.append(Obstacle(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, block_image))
            elif cell.lower() == 'spike':  # Spike
                obstacles.append(Spike(x * TILE_SIZE, y * TILE_SIZE))  # Ajoute le spike à la liste des obstacles
    return obstacles

# Fonction pour charger les images
def load_images():
    global player_image, block_image, spike_image
    player_image = pygame.image.load("assets/player.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image du joueur

    block_image = pygame.image.load("assets/block_1.png").convert_alpha()
    block_image = pygame.transform.scale(block_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image du bloc

    spike_image = pygame.image.load("assets/spike.png").convert_alpha()
    spike_image = pygame.transform.scale(spike_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image des spikes

import pygame
import neat
from pygame.locals import *
from game import *  # Assurez-vous que tu as toutes les fonctions nécessaires

class PlayerAI(pygame.sprite.Sprite):
    def __init__(self, genome, config, level, obstacles):
        """
        Initialise l'IA avec le génome et la configuration NEAT.
        """
        super().__init__()
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)
        
        # On crée le sprite du joueur AI avec l'image que tu utilises
        self.image = pygame.Surface((30, 30))  # Remplacer par une texture réelle si tu as une image
        self.image.fill((255, 0, 0))  # Utilise une couleur ou une texture ici
        self.rect = self.image.get_rect()
        self.rect.x = 100  # Position initiale X
        self.rect.y = 300  # Position initiale Y
        self.velocity = 0  # Vitesse verticale
        
        # Niveau et obstacles pour prendre en compte les interactions
        self.level = level
        self.obstacles = obstacles

    def get_inputs(self):
        """
        Récupère les entrées du réseau neuronal : position, vitesse, obstacles.
        """
        player_x, player_y = self.rect.x, self.rect.y
        velocity = self.velocity
        
        # Distance au prochain obstacle
        distance_to_obstacle = self.get_distance_to_next_obstacle(self.obstacles)
        
        # Hauteur du prochain obstacle
        obstacle_height = self.get_obstacle_height(self.obstacles)
        
        # Retourne les 5 entrées
        return [
            player_x / 500,  # Normalisation de la position X
            player_y / 500,  # Normalisation de la position Y
            velocity / 10,  # Normalisation de la vitesse verticale
            distance_to_obstacle / 500,  # Normalisation de la distance à l'obstacle
            obstacle_height / 500  # Normalisation de la hauteur de l'obstacle
        ]
        
    def get_distance_to_next_obstacle(self, obstacles):
        """
        Calcule la distance à l'obstacle le plus proche à droite.
        """
        closest_distance = float('inf')
        for obstacle in obstacles:
            distance = self.rect.x - obstacle.rect.x
            if distance > 0 and distance < closest_distance:
                closest_distance = distance
        return closest_distance if closest_distance != float('inf') else 0

    def get_obstacle_height(self, obstacles):
        """
        Retourne la hauteur de l'obstacle le plus proche.
        """
        closest_height = 0
        for obstacle in obstacles:
            distance = self.rect.x - obstacle.rect.x
            if distance > 0 and distance < 500:
                closest_height = max(closest_height, obstacle.rect.height)
        return closest_height

    def update(self):
        """
        Met à jour l'état du joueur AI : décisions basées sur le réseau neuronal.
        """
        # Récupère les entrées pour le réseau neuronal
        inputs = self.get_inputs()
        
        # Passe les entrées dans le réseau pour obtenir les sorties
        outputs = self.net.activate(inputs)

        # Si la sortie 0 du réseau est plus grande que 0.5, on saute
        if outputs[0] > 0.5:  # Si l'IA décide de sauter
            self.jump()

        # Met à jour la position du joueur AI (intégration de la gravité et des obstacles)
        self.velocity += 1  # Applique la gravité
        self.rect.y += self.velocity
        
        # Limite la position du joueur AI
        if self.rect.y > 500:  # Si le joueur AI touche le sol
            self.rect.y = 500
            self.velocity = 0

        # Vérifie la collision avec les obstacles
        self.handle_collision()

    def jump(self):
        """Simule un saut de l'IA."""
        self.velocity = -10  # On applique une vitesse négative pour faire sauter l'IA

    def handle_collision(self):
        """Gère les collisions avec les obstacles."""
        for obstacle in self.obstacles:
            if self.rect.colliderect(obstacle.rect):  # Si le joueur AI touche un obstacle
                self.rect.x -= 10  # Reculer légèrement pour simuler une collision
                break  # Terminer la boucle après avoir traité la collision

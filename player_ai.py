import pygame
import neat
from pygame.locals import *
from game import *  # Assurez-vous que tu as toutes les fonctions nécessaires

class PlayerAI(Player):
    def __init__(self, genome, config, level, obstacles):
        super().__init__()  # Appel du constructeur de Player pour conserver le comportement de base
        self.genome = genome
        self.config = config  # Enregistre la configuration NEAT ici
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)  # Utilisation de config pour créer le réseau
        self.level = level
        self.obstacles = obstacles
        self.fitness = 0  # Initialisation de la fitness
        self.best_fitness = -float('inf')  # Aucune fitness au départ
        self.last_fitness = 0  # Initialisation de la fitness précédente
        self.running = True

    def die(self):
        """Réinitialise l'IA en cas de mort"""
        super().die()  # Appelle la méthode de réinitialisation du joueur
        self.running = False
        
        # Réinitialisation du réseau neuronal avec la configuration correcte
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)  # Utilise self.config ici

    def updateAI(self):
        """Mise à jour spécifique à l'IA sans interférer avec les contrôles du joueur"""
        # Appel à la méthode update() de Player pour gérer les mouvements standards
        super().update(self.obstacles)

        # Obtenir les entrées pour le réseau neuronal
        inputs = self.get_inputs()
        output = self.net.activate(inputs)

        # Si la sortie du réseau est > 0.5, l'IA décide de sauter
        if output[0] > 0.2:
            self.jump()
            
    def get_inputs(self):
        """Préparer les entrées pour le réseau neuronal de l'IA"""
        closest_obstacle = self.get_closest_obstacle()  # Trouver l'obstacle le plus proche
        if closest_obstacle:
            # Calculer les entrées normalisées
            horizontal_distance = (closest_obstacle.rect.x - self.rect.x) / 800
            vertical_distance = (closest_obstacle.rect.y - self.rect.y) / 600
            vertical_speed = self.vel_y / 10.0
            horizontal_speed = self.vel_x / 10.0  # Ajout de la vitesse horizontale pour plus de contexte

            # print(horizontal_distance, vertical_distance, vertical_speed, horizontal_speed)
            # Retourner les entrées
            inputs = [horizontal_distance, vertical_distance, vertical_speed, horizontal_speed]
        else:
            # Si aucun obstacle n'est trouvé, utilise des valeurs par défaut
            inputs = [1, 1, self.vel_y / 10.0, self.vel_x / 10.0]
        
        return inputs

    def get_closest_obstacle(self):
        """Retourne l'obstacle le plus proche du joueur"""
        closest_obstacle = None
        for obstacle in self.obstacles:
            if obstacle.rect.x > self.rect.x:
                closest_obstacle = obstacle
                break
        return closest_obstacle

    def play_game(self):
        """Lance une partie et retourne la fitness à la fin de la partie"""
        fitness = 0
        last_fitness = self.last_fitness  # Garde la dernière fitness

        while not self.is_game_over():
            self.updateAI()  # Met à jour l'IA
            fitness = self.get_fitness()  # Récupère la fitness actuelle

            # Si la fitness actuelle est plus faible que la dernière, passe au génome suivant
            if fitness < last_fitness:
                print(f"Fitness est plus faible. Passer au génome suivant... (ancien fitness: {last_fitness}, nouveau fitness: {fitness})")
                break  # Arrêter le jeu et passer au génome suivant

            self.last_fitness = fitness  # Met à jour la fitness pour la comparaison suivante

        return fitness  # Retourner la fitness après la fin du jeu

    def get_fitness(self):
        """Calculer et retourner la fitness actuelle"""
        # La logique ici dépend de la façon dont tu calcules la fitness dans ton jeu
        # Par exemple, tu pourrais baser la fitness sur le temps de survie, le score, etc.
        return self.level.get_score()  # Exemple de récupération du score comme fitness

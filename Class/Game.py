# Import Dépendances
import pygame
import neat

# Import Class
from Class.Player import Player
from Class.Obstacle import Obstacle
from Class.Spike import Spike
from Class.Detection import DetectionGrid
from Class.End import End

# Import Fonction
from Function.load_level import load_level
from Function.generate_obstacles import generate_obstacles

# Import Variable
from config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Game:
    def __init__(self):
        
        self.player = Player()  # Crée le joueur
        self.spawn_timer = 0
        self.score = 0
        self.is_running = True
        self.background = pygame.image.load("assets/bg.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Charger le niveau et générer les obstacles à partir du CSV
        self.level = load_level("level_2.csv")
        self.obstacles = generate_obstacles(self.level)
        self.isWin = False

        # Créer un groupe de sprites
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(*self.obstacles)  # Ajouter les obstacles au groupe de sprites
        
        # Gestion de la caméra
        self.camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_width = len(self.level[0]) * TILE_SIZE  # Largeur du niveau, basée sur le fichier CSV
        
        self.grid = DetectionGrid(self.player)
        
        # Configuration NEAT
        self.config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                        "neat-config.ini")
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        self.population.add_reporter(neat.Checkpointer(5))

    # Lancer l'entraînement des génomes
    def update(self):
        # Mettre à jour la grille
        """Mise à jour du jeu, qui met à jour la grille, le joueur, la
        position de la caméra, les obstacles, et vérifie les collisions."""
        
        self.grid.update(self.obstacles)
    
        # Mettre à jour le joueur
        self.player.move(self.obstacles)
        
        # Mettre à jour la position de la caméra
        if self.player.rect.bottom > SCREEN_HEIGHT - 50:
            self.is_running = False  # Arrêter le jeu si le joueur est trop bas

        # Mettre à jour les obstacles
        for obstacle in self.obstacles:
            obstacle.move()

        # Vérifier les collisions et les autres logiques de jeu
        self.check_collisions()

        # Mettre à jour le score
        self.score += 1

    def is_win(self):
        """Renvoie True si le joueur a gagné (a atteint la fin du niveau),
        False sinon."""
        return self.isWin
    
    # Vérifie les colisions
    def check_collisions(self):
        """Vérifie les collisions avec les obstacles (spikes, blocs ou end)."""
        for obstacle in self.obstacles:
            # Vérifier les collisions avec les pics (spikes)
            if isinstance(obstacle, Spike):
                
                if obstacle.check_collision(self.player.rect):
                    self.is_running = False
                    return

            # Vérifier les collisions avec les blocs
            elif isinstance(obstacle, Obstacle):
                if self.player.rect.colliderect(obstacle.rect):  # Collision avec un bloc

                    # Vérifier si la collision est latérale (gauche/droite)
                    if self.player.rect.right > obstacle.rect.left and self.player.rect.left < obstacle.rect.right:
                        # Si la collision est latérale (gauche ou droite) et non par en dessous
                        if self.player.rect.bottom > obstacle.rect.top:
                            # Le joueur est sur le côté du bloc
                            self.is_running = False  # Le joueur meurt, on arrête le jeu
                            return
            elif isinstance(obstacle, End):
                if self.player.rect.colliderect(obstacle.rect):
                    self.isWin = True
                # self.is_running = False
    
    #  Dessine le jeu
    def draw(self, screen):
        # Dessiner le fond
        """
        Dessine le jeu sur l'écran.

        :param screen: L'écran sur lequel le jeu sera dessiné.
        :type screen: pygame.Surface
        """
        
        screen.blit(self.background, (0, 0))

        # Dessiner les éléments du jeu (joueur et obstacles)
        for sprite in self.all_sprites:
            screen.blit(sprite.image, sprite.rect.move(-self.camera.x, -self.camera.y))

        # Dessiner le score
        self.draw_score(screen)
        
        # Positionner la grille pour que le joueur soit tout à gauche
        grid_x = self.player.rect.left  # Aligner la colonne gauche sur le joueur
        grid_y = (self.player.rect.centery - (self.grid.grid_size // 2) * self.grid.cell_size
            - self.grid.cell_size - self.grid.cell_size / 2)  # Centrer verticalement et déplacer d'une case et demi plus haut

        # Dessiner la grille avec l'orientation
        for i, row in enumerate(self.grid.grid):
            for j, cell in enumerate(row):
                if cell == 3:  # Indicateur du joueur
                    border_color = (255, 255, 0)  # Jaune
                elif cell == 1:  # Bloc
                    border_color = (255, 0, 0)  # Rouge
                elif cell == 2:  # Pique
                    border_color = (0, 255, 0)  # Vert
                else:  # Vide
                    border_color = (0, 255, 255)  # Cyan

                pygame.draw.rect(screen, border_color, 
                                (grid_x + i * self.grid.cell_size,  # `i` correspond à x
                                grid_y + j * self.grid.cell_size,  # `j` correspond à y
                                self.grid.cell_size, self.grid.cell_size), 2)

    # Dessine le score
    def draw_score(self, screen):
        """
        Dessine le score actuel sur l'écran donné.

        :param screen: La surface Pygame sur laquelle le score sera affiché.
        :type screen: pygame.Surface
        """
        font = pygame.font.SysFont("Arial", 30)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

    # Récupère l'état de la grille
    def get_state(self):
        # Récupérer l'état de la grille comme vecteur d'entrées pour NEAT
        """
        Récupère l'état de la grille sous forme de vecteur pour les entrées du réseau de neurones.

        :return: L'état de la grille en tant que liste 1D.
        :rtype: List[int]
        """
        return self.grid.get_grid_state()

    # Récupère le score
    def get_reward(self):
        """
        Récupère le score actuel comme récompense.

        :return: Le score actuel du jeu.
        :rtype: int
        """
        return self.score

    # Verifie si le jeu est encore en cours
    def is_alive(self):
        """
        Vérifie si le jeu est encore en cours.

        :return: Si le jeu est encore en cours.
        :rtype: bool
        """
        return self.is_running

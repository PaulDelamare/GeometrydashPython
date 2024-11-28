import pygame
import neat
import os
import sys
import random
import csv

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GENERATION = 0
TILE_SIZE = 40  # Taille de chaque case en pixels

player_image = None
block_image = None
spike_image = None

pygame.init()

# Définir la taille de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Utiliser config.WIDTH et config.HEIGHT
pygame.display.set_caption('Geometry Dash avec IA et Mode Manuel')

def load_images():
    
    global player_image, block_image, spike_image
    player_image = pygame.image.load("assets/player.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image du joueur

    block_image = pygame.image.load("assets/block_1.png").convert_alpha()
    block_image = pygame.transform.scale(block_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image du bloc

    spike_image = pygame.image.load("assets/spike.png").convert_alpha()
    spike_image = pygame.transform.scale(spike_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image des spikes


load_images()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

all_sprites = pygame.sprite.Group()

def load_level(filename):
    level = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            level.append(row)
    return level

class DetectionGrid:
    def __init__(self, player, grid_size=6, cell_size=40):
        self.player = player
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.grid = [[0] * grid_size for _ in range(grid_size)]  # 0 = vide, 1 = bloc, 2 = pique

    def update(self, obstacles):
        # Réinitialiser la grille à vide
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        
        # Calculer les coordonnées de la grille par rapport à la position du joueur
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                grid_x = self.player.rect.x + i * self.cell_size
                grid_y = self.player.rect.bottom - (self.grid_size * self.cell_size) + j * self.cell_size

                # Vérifier s'il y a un obstacle à cette position
                for obstacle in obstacles:
                    if obstacle.rect.collidepoint(grid_x, grid_y):
                        if isinstance(obstacle, Spike):
                            self.grid[i][j] = 2  # Cellule contenant un spike
                        else:
                            self.grid[i][j] = 1  # Cellule contenant un bloc


    def draw(self, screen):
        # Dessiner uniquement les bordures de la grille et ne pas remplir l'intérieur des cellules
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Déterminer la couleur de la bordure en fonction du type de cellule
                if self.grid[i][j] == 1:  # Bloc
                    border_color = (255, 0, 0)  # Rouge pour les blocs
                elif self.grid[i][j] == 2:  # Pique
                    border_color = (0, 255, 255)  # Vert pour les piques
                else:  # Vide
                    border_color = (0, 0, 0)  # Blanc pour les cellules vides

                # Dessiner les bordures de la cellule
                pygame.draw.rect(screen, border_color, 
                                 (self.player.rect.x + i * self.cell_size, 
                                    self.player.rect.bottom - (self.grid_size * self.cell_size) + j * self.cell_size, 
                                    self.cell_size, self.cell_size), 2)  # '2' est l'épaisseur de la bordure

        # Dessiner les bordures globales de la grille
        for i in range(self.grid_size + 1):
            pygame.draw.line(screen, (0, 255, 255), 
                             (self.player.rect.x + i * self.cell_size, self.player.rect.bottom - (self.grid_size * self.cell_size)),
                             (self.player.rect.x + i * self.cell_size, self.player.rect.bottom - (self.grid_size * self.cell_size) + self.grid_size * self.cell_size), 2)
            pygame.draw.line(screen, (0, 255, 255), 
                             (self.player.rect.x, self.player.rect.bottom - (self.grid_size * self.cell_size) + i * self.cell_size),
                             (self.player.rect.x + self.grid_size * self.cell_size, self.player.rect.bottom - (self.grid_size * self.cell_size) + i * self.cell_size), 2)

    def get_grid_state(self):
        # Retourne l'état de la grille, prêt à être envoyé au réseau
        return [cell for row in self.grid for cell in row]

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        try:
            self.image = pygame.image.load("assets/player.png")
        except pygame.error as e:
            print(f"Erreur : Impossible de charger player.png : {e}")
            sys.exit()

        self.image = player_image  # Redimensionner le joueur
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100  # Le joueur au bas de l'écran
        
        self.rect.bottom = self.rect.y + TILE_SIZE - 10
        self.gravity = 0
        self.is_jumping = False
        super().__init__()

    def jump(self):
        if not self.is_jumping:
            self.gravity = -15
            self.is_jumping = True

    def move(self):
        self.gravity += 1
        self.rect.y += self.gravity

        # Gestion de la collision avec le sol
        if self.rect.bottom >= SCREEN_HEIGHT - 120:  # La position du sol
            self.rect.bottom = SCREEN_HEIGHT - 120  # Stopper le joueur au sol
            self.gravity = 0  # Réinitialiser la gravité
            self.is_jumping = False  # Le joueur n'est plus en train de sauter

    def draw(self, screen):
        
        screen.blit(self.image, self.rect)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def move(self):
        self.rect.x -= 10
        
    def off_screen(self):
        return self.rect.x + self.rect.width < 0
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

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
    def move(self):
        self.rect.x -= 10  # Déplace le spike vers la gauche, comme un obstacle normal
    
    def off_screen(self):
        return self.rect.x + self.rect.width < 0
    
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Game Class
class Game:
    def __init__(self):
        self.player = Player()  # Crée le joueur
        self.spawn_timer = 0
        self.score = 0
        self.is_running = True
        self.background = pygame.image.load("assets/bg.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Charger le niveau et générer les obstacles à partir du CSV
        self.level = load_level("level_1.csv")
        self.obstacles = generate_obstacles(self.level)

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

    def spawn_obstacle(self):
        if self.spawn_timer <= 0:
            height = random.randint(50, 150)
            self.obstacles.append(Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT - height, 50, height))
            self.spawn_timer = random.randint(30, 60)
        else:
            self.spawn_timer -= 1

    def update(self):
        self.player.move()

        # Mettre à jour les obstacles
        for obstacle in self.obstacles:
            obstacle.move()

        # Nettoyer les obstacles qui ne sont plus à l'écran
        self.obstacles = [obs for obs in self.obstacles if not obs.off_screen()]

        # Vérifier les collisions
        for obstacle in self.obstacles:
            if isinstance(obstacle, Spike):
                if obstacle.check_collision(self.player.rect):
                    self.is_running = False  # Collision avec un pique
            # elif self.player.rect.colliderect(obstacle.rect):
            #     self.is_running = False  # Collision avec un obstacle classique

        # Mettre à jour le score
        self.score += 1

    def draw(self, screen):
        # Dessiner le fond
        screen.blit(self.background, (0, 0))

        # Dessiner les éléments du jeu (joueur et obstacles)
        for sprite in self.all_sprites:
            screen.blit(sprite.image, sprite.rect.move(-self.camera.x, -self.camera.y))

        # Dessiner le score
        self.draw_score(screen)
        
        # Positionner la grille par rapport au joueur
        grid_x = self.player.rect.x  # Le joueur est déjà à gauche, donc on garde son X pour la grille
        grid_y = self.player.rect.bottom - self.grid.cell_size * len(self.grid.grid)  # Positionner la grille en bas du joueur

        # Dessiner la grille avec la nouvelle position
        for i, row in enumerate(self.grid.grid):
            for j, cell in enumerate(row):
                # Déterminer la couleur de la bordure selon le contenu de la cellule
                if cell == 1:  # Bloc
                    border_color = (255, 0, 0)  # Rouge pour les blocs
                elif cell == 2:  # Pique
                    border_color = (0, 255, 0)  # Vert pour les piques
                else:  # Vide
                    border_color = (0, 255, 255)  # Cyan pour les cellules vides (optionnel)

                # Dessiner uniquement les bordures des cellules
                pygame.draw.rect(screen, border_color, 
                                (grid_x + i * self.grid.cell_size, 
                                grid_y + j * self.grid.cell_size, 
                                self.grid.cell_size, self.grid.cell_size), 2)  # '2' est l'épaisseur de la bordure

    def draw_score(self, screen):
        font = pygame.font.SysFont("Arial", 30)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

    def get_state(self):
        # Récupérer l'état de la grille comme vecteur d'entrées pour NEAT
        return self.grid.get_grid_state()

    def get_reward(self):
        return self.score

    def is_alive(self):
        return self.is_running


def load_level(filename):
    """Charger le niveau à partir d'un fichier CSV."""
    level = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            level.append(row)
    return level

def generate_obstacles(level):
    """Générer les obstacles à partir du niveau."""
    obstacles = []
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            if cell == '0':  # Bloc solide
                obstacles.append(Obstacle(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, block_image))
            elif cell.lower() == 'spike':  # Spike
                obstacles.append(Spike(x * TILE_SIZE, y * TILE_SIZE))  # Ajoute un obstacle de type spike
    return obstacles

level = load_level('level_1.csv')  # Remplacer par le chemin correct de votre niveau
obstacles = generate_obstacles(level)

# Evaluation des génomes pour NEAT
def eval_genomes(genomes, config):
    global GENERATION
    GENERATION += 1

    # Initialize pygame and game objects
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Boucle principale pour chaque génome
    for genome_id, genome in genomes:
        # Créer un réseau de neurones pour chaque génome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game()  # Crée un seul jeu par génome
        genome.fitness = 0  # Réinitialiser la fitness du génome

        running = True
        while running:
            # Gérer les événements pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if game.is_alive():
                # Obtenir l'état actuel du jeu
                state = game.get_state()
                
                # Calculer l'action à prendre avec le réseau de neurones
                output = net.activate(state)
                                
                # Si le réseau sort une valeur > 0.5, on fait sauter le joueur
                if output[0] > 0.5:
                    game.player.jump()

                # Mettre à jour l'état du jeu
                game.update()

                # Mettre à jour la fitness du génome
                genome.fitness += game.get_reward()

            else:
                print('mort')

                # Le jeu est terminé pour ce génome
                running = False  # Sortir de la boucle while

            # Dessiner les éléments du jeu à chaque frame
            screen.fill(WHITE)
            game.draw(screen)

            # Afficher la génération en cours
            generation_font = pygame.font.SysFont("Arial", 30)
            generation_text = generation_font.render(f"Generation: {GENERATION}", True, BLACK)
            screen.blit(generation_text, (10, 50))

            # Afficher l'ID et la fitness du génome
            fitness_font = pygame.font.SysFont("Arial", 30)
            fitness_text = fitness_font.render(f"Genome ID: {genome_id} Fitness: {genome.fitness}", True, BLACK)
            screen.blit(fitness_text, (10, 100))

            pygame.display.flip()
            clock.tick(FPS)

    # Après avoir testé tous les génomes, vous pouvez avancer à la génération suivante

if __name__ == "__main__":
    
    all_sprites.add(*obstacles)

    # Load NEAT config
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.ini")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Run NEAT
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    p.run(eval_genomes, 50)
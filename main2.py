import pygame
import neat
import os
import sys
import random
import csv
import pickle


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

def save_progress(population, max_fitness, filename='save_state.pkl'):
    with open(filename, 'wb') as f:
        # Sauvegarder l'état de la population et le fitness maximal
        pickle.dump((population, max_fitness), f)
    print("Progression sauvegardée.")
    
    # Fonction pour charger l'état sauvegardé de la population
def load_progress(filename='save_state.pkl'):
    try:
        with open(filename, 'rb') as f:
            # Charger l'état de la population et le fitness maximal
            population, max_fitness = pickle.load(f)
            print("Progression chargée.")
            return population, max_fitness
    except FileNotFoundError:
        # Si le fichier n'existe pas, retourner None pour une nouvelle initialisation
        print("Aucune sauvegarde trouvée. Démarrage d'une nouvelle partie.")
        return None, -float('inf')  # Fitness initial très faible


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
        self.indicator_pos = None  # Indicateur de position
        self.gridWithout3 = [[0] * grid_size for _ in range(grid_size)] 

    def update(self, obstacles):
        # Réinitialiser la grille à vide
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        
        # Réinitialiser l'indicateur, s'il n'est pas défini
        if self.indicator_pos is None:
            self.indicator_pos = (0, 0)  # Valeur par défaut pour éviter les erreurs

        # Calculer les coordonnées de la grille par rapport à la position du joueur
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Calculer les coordonnées (x, y) de la cellule de la grille
                grid_x = self.player.rect.x + (i - self.grid_size // 2) * self.cell_size
                grid_y = self.player.rect.y + (j - self.grid_size // 2) * self.cell_size

                # Ajuster les coordonnées verticales pour mieux aligner avec l'affichage
                grid_y -= 2 * self.cell_size  # Ajuster ici pour compenser le décalage vertical

                # Ajuster grid_x pour compenser le décalage de 4 blocs vers la droite
                grid_x += 4 * self.cell_size  # Décalage de 4 blocs vers la droite

                # Vérifier s'il y a un obstacle à cette position
                for obstacle in obstacles:
                    if obstacle.rect.collidepoint(grid_x, grid_y):
                        if isinstance(obstacle, Spike):
                            self.grid[i][j] = 2  # Cellule contenant un pique
                            self.gridWithout3[i][j] = 2
                        else:
                            self.grid[i][j] = 1  # Cellule contenant un bloc
                            self.gridWithout3[i][j] = 1

        
        # Marquer la cellule sélectionnée avec un `3`
        # row, col = self.indicator_pos  # Obtenir la position de l'indicateur
        # if 0 <= row < self.grid_size and 0 <= col < self.grid_size:  # Vérifier les limites
        #     self.grid[row][col] = 3  # Marquer la cellule choisie comme spéciale
            
        # self.check_for_jump()

    def choose_random_cell(self):
        """ Choisit une case aléatoire dans la grille de 6x6 et renvoie un index. """
        random_index = random.randint(0, self.grid_size * self.grid_size - 1)  # Génère un nombre aléatoire entre 0 et 35
        return random_index
    
    # def check_for_jump(self):
    #     """
    #     Vérifie si la cellule avec l'indicateur (3) a un obstacle (1) et effectue un saut si nécessaire.
    #     """
    #     # Parcourir les grilles pour comparer les positions
    #     for i in range(self.grid_size):
    #         for j in range(self.grid_size):
    #             # Vérifier si la grille avec l'indicateur contient un `3` à la position (i, j)
    #             if self.grid[i][j] == 3:
    #                 # Vérifier si la grille sans l'indicateur contient un `1` (obstacle) à la même position
    #                 if self.gridWithout3[i][j] == 2:
    #                     self.player.jump()  # Effectuer le saut si un obstacle est détecté

    def set_indicator_pos(self, cell_index):
        """Définit la case à colorier (en jaune)."""
        row = cell_index // self.grid_size
        col = cell_index % self.grid_size
        self.indicator_pos = (row, col)  # Enregistrer la position de la case choisie
        self.indicator_pos

    def draw(self, screen):
        # Dessiner la grille
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
                                    (self.player.rect.x + (i - self.grid_size // 2) * self.cell_size, 
                                    self.player.rect.bottom - (self.grid_size * self.cell_size) + (j - self.grid_size // 2) * self.cell_size, 
                                    self.cell_size, self.cell_size), 2)

        # Dessiner la case choisie (en jaune)
        if self.indicator_pos:
            row, col = self.indicator_pos
            pygame.draw.rect(screen, (255, 255, 0),  # Jaune
                                (self.player.rect.x + (col - self.grid_size // 2) * self.cell_size, 
                                self.player.rect.bottom - (self.grid_size * self.cell_size) + (row - self.grid_size // 2) * self.cell_size, 
                                self.cell_size, self.cell_size))

        # Dessiner les bordures globales de la grille
        for i in range(self.grid_size + 1):
            pygame.draw.line(screen, (0, 255, 255), 
                             (self.player.rect.x + (i - self.grid_size // 2) * self.cell_size, 
                              self.player.rect.bottom - (self.grid_size * self.cell_size)),
                             (self.player.rect.x + (i - self.grid_size // 2) * self.cell_size, 
                              self.player.rect.bottom - (self.grid_size * self.cell_size) + self.grid_size * self.cell_size), 2)
            pygame.draw.line(screen, (0, 255, 255), 
                                (self.player.rect.x, 
                              self.player.rect.bottom - (self.grid_size * self.cell_size) + (i - self.grid_size // 2) * self.cell_size),
                             (self.player.rect.x + self.grid_size * self.cell_size, 
                              self.player.rect.bottom - (self.grid_size * self.cell_size) + (i - self.grid_size // 2) * self.cell_size), 2)
            
    def get_grid_state(self):
        # Retourner l'état de la grille sous forme de vecteur pour l'IA
        return [cell for row in self.grid for cell in row]  # Transforme la grille en un vecteur 1D
    
    def choose_random_cell(self):
        """
        Choisit une case aléatoire parmi les 36 cases de la grille et retourne son index.
        L'index est compris entre 0 et 35.
        """
        return random.randint(1, 36)


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        try:
            self.image = pygame.image.load("assets/player.png")
        except pygame.error as e:
            # print(f"Erreur : Impossible de charger player.png : {e}")
            sys.exit()

        self.image = player_image  # Redimensionner le joueur
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
        if self.on_ground:  # Le joueur ne peut sauter que s'il est sur le sol
            self.velocity = -15  # La vitesse du saut est négative (vers le haut)
            self.on_ground = False  # Le joueur n'est plus sur le sol pendant le saut

    def move(self, obstacles):
        keys = pygame.key.get_pressed()
        self.on_ground = False  # Réinitialise la vérification du sol

        # Appliquer la gravité
        self.velocity += 1  # La gravité fait descendre le joueur
        self.rect.y += self.velocity  # Mettre à jour la position verticale

        # Vérifier la collision avec le sol ou les obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):  # Si le joueur touche un obstacle
                if isinstance(obstacle, Spike):  # Vérifier si l'obstacle est un pique (spike)
                    # Si le joueur touche un pic, il meurt ou est arrêté
                    self.is_running = False  # Le joueur est touché par le pic
                    return False
                
                if self.velocity > 0:  # Si le joueur tombe
                    self.rect.bottom = obstacle.rect.top  # Ajuster la position pour que le joueur ne passe pas à travers l'obstacle
                    self.velocity = 0  # Stopper le mouvement vertical
                    self.on_ground = True  # Le joueur est maintenant sur le sol


        # Empêcher le joueur de passer sous le sol
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity = 0  # Arrêter la chute
                
    def check_block_collision(self, obstacles):
        """ Vérifie si le joueur est en collision avec un bloc. """
        for obstacle in obstacles:
            if isinstance(obstacle, Obstacle):  # Si c'est un bloc
                if self.rect.colliderect(obstacle.rect):  # Si le joueur entre en collision avec un bloc
                    # Vérifier la direction de la collision pour décider si le joueur est sur le bloc ou non
                    if self.rect.bottom <= obstacle.rect.top + 10:  # Le joueur est sur le bloc
                        self.rect.bottom = obstacle.rect.top  # Positionner le joueur juste sur le bloc
                        self.gravity = 0  # Réinitialiser la gravité pour éviter que le joueur tombe
                        self.is_jumping = False  # Indiquer que le joueur n'est plus en train de sauter
                    else:
                        # Si la collision est autre, on gère la logique de mouvement ou d'arrêt (par exemple, arrêter le mouvement horizontal)
                        pass


    def draw(self, screen):
        
        screen.blit(self.image, self.rect)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def move(self):
        self.rect.x -= 8
        
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
        self.rect.x -= 8 # Déplace le spike vers la gauche, comme un obstacle normal
    
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
        self.level = load_level("level_2.csv")
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
        self.grid.update(self.obstacles)
    
        self.player.move(self.obstacles)
        
        if self.player.rect.bottom > SCREEN_HEIGHT - 50:
            self.is_running = False  # Arrêter le jeu si le joueur est trop bas

        # Mettre à jour les obstacles
        for obstacle in self.obstacles:
            obstacle.move()

        # Vérifier les collisions et les autres logiques de jeu
        self.check_collisions()

        # Mettre à jour le score
        self.score += 1

    def check_collisions(self):
        """Vérifie les collisions avec les obstacles (spikes et blocs)."""
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
                if cell == 3:  # Indicateur spécial
                    border_color = (255, 255, 0)  # Jaune
                elif cell == 1:  # Bloc
                    border_color = (255, 0, 0)  # Rouge
                elif cell == 2:  # Pique
                    border_color = (0, 255, 0)  # Vert
                else:  # Vide
                    border_color = (0, 255, 255)  # Cyan

                pygame.draw.rect(screen, border_color, 
                                (grid_x + i * self.grid.cell_size, 
                                grid_y + j * self.grid.cell_size, 
                                self.grid.cell_size, self.grid.cell_size), 2)

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

level = load_level('level_2.csv')  # Remplacer par le chemin correct de votre niveau
obstacles = generate_obstacles(level)

# Déclarer le fitness max globalement avant la fonction eval_genomes
max_fitness_global = -float('inf')  # Initialiser à une valeur très faible

# Charger la progression (si elle existe)
population, max_fitness_global = load_progress()

# Créer une population NEAT
if population is None:
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.ini")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)  # Créer une nouvelle population si aucune sauvegarde
else:
    # Si la population est chargée, la réutiliser
    p = population

# Ajouter des reporteurs pour afficher les résultats
p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

# Fonction d'évaluation des génomes
def eval_genomes(genomes, config):
    global GENERATION, max_fitness_global
    GENERATION += 1  # Incrémenter la génération

    # Initialiser Pygame et l'écran
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Créer des réseaux et des jeux
    nets = []
    games = []

    # Assigner des IDs séquentiels et créer les réseaux et les jeux pour chaque génome
    for idx, (genome_id, genome) in enumerate(genomes):
        # Assigner un ID unique séquentiel
        genome_id = idx + 1  # Assigner un ID allant de 1 à n

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0  # Réinitialiser la fitness

        # Initialiser un nouveau jeu pour chaque génome
        game = Game()
        game.grid = DetectionGrid(game.player)
        games.append(game)

    # Vérification que le nombre de jeux correspond au nombre de génomes
    if len(games) != len(genomes):
        print(f"Erreur : le nombre de jeux ({len(games)}) ne correspond pas au nombre de génomes ({len(genomes)}).")
        pygame.quit()
        sys.exit(1)

    # Boucle principale pour chaque génération
    for idx, (genome_id, genome) in enumerate(genomes):
        if genome_id > len(games):  # Vérifier que l'ID est valide
            print(f"Erreur : génome_id {genome_id} dépasse le nombre de jeux ({len(games)}).")
            continue  # Passer au génome suivant si l'indice est hors de portée

        # Assigner à nouveau un ID séquentiel lors de l'évaluation (optionnel si vous réinitialisez les génomes)
        genome_id = idx + 1  # Toujours garantir que l'ID est de 1 à n

        game = games[genome_id - 1]  # Assurez-vous que l'indice est valide
        net = nets[genome_id - 1]
        game.grid.set_indicator_pos(game.grid.choose_random_cell())

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)  # Sortie propre de l'application

            grid_state = game.grid.get_grid_state()  # Récupérer l'état de la grille
            output = net.activate(grid_state)  # Activer le réseau avec l'état de la grille

            action = output.index(max(output))  # Décision de l'IA (sauter ou non)
            if action == 1:
                game.player.jump()

            # Mettre à jour la fitness
            if game.is_alive():
                game.update()
                genome.fitness += game.get_reward()  # Mise à jour de la fitness du génome
            else:
                running = False

            # Garder la trace du meilleur fitness
            if genome.fitness > max_fitness_global:
                max_fitness_global = genome.fitness

            # Dessiner l'état actuel du jeu
            screen.fill(WHITE)
            game.draw(screen)

            font = pygame.font.SysFont("Arial", 30)
            generation_text = font.render(f"Generation: {GENERATION}", True, (255, 255, 255))
            screen.blit(generation_text, (10, 10))

            fitness_current_text = font.render(f"Fitness actuel (ID {genome_id}): {genome.fitness}", True, (255, 255, 255))
            screen.blit(fitness_current_text, (10, 50))

            fitness_max_text = font.render(f"Fitness max global: {max_fitness_global}", True, (255, 255, 255))
            screen.blit(fitness_max_text, (10, 90))

            pygame.display.flip()
            clock.tick(FPS)

    # Sauvegarder la progression à la fin de la génération
    save_progress(p, max_fitness_global)  # Sauvegarder l'état après chaque génération

    pygame.quit()

if __name__ == "__main__":
    # Charger le fichier de configuration NEAT
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.ini")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Créer une population NEAT
    p = neat.Population(config)
    
    # Ajouter des reporteurs pour afficher les résultats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Lancer l'entraînement des génomes
    p.run(eval_genomes, 1000)  # 50 générations d'entraînement

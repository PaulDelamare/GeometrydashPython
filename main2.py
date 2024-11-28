import pygame
import neat
import os
import sys
import csv
import pickle


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 600
GENERATION = 0
TILE_SIZE = 40  # Taille de chaque case en pixels

# Variable pour les images
player_image = None
block_image = None
spike_image = None

# Initialise Pygame
pygame.init()

# Définir la taille de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Utiliser config.WIDTH et config.HEIGHT
pygame.display.set_caption('Geometry Dash\'ier avec IA et Mode Manuel')

# Fonction pour load les images
def load_images():
    
    global player_image, block_image, spike_image
    player_image = pygame.image.load("assets/player.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image du joueur

    block_image = pygame.image.load("assets/block_1.png").convert_alpha()
    block_image = pygame.transform.scale(block_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image du bloc

    spike_image = pygame.image.load("assets/spike.png").convert_alpha()
    spike_image = pygame.transform.scale(spike_image, (TILE_SIZE, TILE_SIZE))  # Redimensionner l'image des spikes

load_images()

# Fonction pour sauvegarder la progression
def save_progress(population, generation, max_fitness, filename='save_state.pkl'):
    """ Sauvegarde la progression de la simulation (population, génération, fitness max, etc.). """
    
    # Sauvegarde de la population, génération et fitness max
    with open(filename, 'wb') as f:
        # On sauvegarde la population, la génération, et le fitness max
        pickle.dump((population, generation, max_fitness), f)
    
    print(f"Progression sauvegardée sous : {filename}")

    
# Fonction pour charger l'état sauvegardé de la population
def load_progress(filename='save_state.pkl'):
    try:
        # Si un fichier de sauvegarde existe, on le charge
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                population, generation, max_fitness = pickle.load(f)
                print(f"Progression chargée : Génération {generation}, Fitness max {max_fitness}")
                return population, generation, max_fitness

        # Si aucune sauvegarde n'existe, recommencer une nouvelle partie
        print("Aucune sauvegarde trouvée. Démarrage d'une nouvelle partie.")
        return None, 0, 0  # Pas de population et génération à 0, fitness max à 0
    
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")
        return None, 0, 0

# Colors
WHITE = (255, 255, 255)

all_sprites = pygame.sprite.Group()

# Charge le niveau à partir du csv
def load_level(filename):
    level = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            level.append(row)
    return level

# Class pour la grille de détection
class DetectionGrid:
    def __init__(self, player, grid_size=6, cell_size=40):
        self.player = player
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.grid = [[0] * grid_size for _ in range(grid_size)]  # 0 = vide, 1 = bloc, 2 = pique
        self.indicator_pos = None  # Indicateur de position
        self.gridWithout3 = [[0] * grid_size for _ in range(grid_size)]  # Grille sans l'indicateur

    def update(self, obstacles):
        # Réinitialiser la grille à vide
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        
        # Réinitialiser l'indicateur, s'il n'est pas défini
        if self.indicator_pos is None:
            #Valeur par défaut pour éviter les erreurs
            self.indicator_pos = (0, 0)

        # Calculer les coordonnées de la grille par rapport à la position du joueur
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Calculer les coordonnées (x, y) de la cellule de la grille
                grid_x = self.player.rect.x + (i - self.grid_size // 2) * self.cell_size
                grid_y = self.player.rect.y + (j - self.grid_size // 2) * self.cell_size

                # Ajuster la position de la grille visuellement (pour ne pas déplacer la grille)
                grid_y -= 2 * self.cell_size  # Décaler visuellement pour compenser les 2 cases en plus

                # Ajuster grid_x pour compenser le décalage de 4 blocs vers la droite
                grid_x += 4 * self.cell_size  # Décalage de 4 blocs vers la droite

                # Déplacer la détection de 2 cases vers le bas (ajuster la position de la détection)
                grid_y += 2 * self.cell_size  # Détecter 2 cases plus bas que la position visuelle

                # Vérifier s'il y a un obstacle à cette position
                for obstacle in obstacles:
                    if obstacle.rect.collidepoint(grid_x, grid_y):
                        if isinstance(obstacle, Spike):
                            self.grid[i][j] = 2  # Cellule contenant un pique
                            self.gridWithout3[i][j] = 2
                        else:
                            self.grid[i][j] = 1  # Cellule contenant un bloc
                            self.gridWithout3[i][j] = 1

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
    
    # Retourne l'étât de la grille avec les informations sur les blocs et les piques
    def get_grid_state(self):
        # Retourner l'état de la grille sous forme de vecteur pour l'IA
        return [cell for row in self.grid for cell in row]  # Transforme la grille en un vecteur 1D

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
        screen.blit(self.image, self.rect)

# Obstacle Class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    # Rapproche le block vers la gauche (le joueur ne bouge aps ce sont les obstacles)
    def move(self):
        self.rect.x -= 8
    
    # Dessine le block
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Spike Class
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
    
    # Rapproche le spike vers la gauche
    def move(self):
        self.rect.x -= 8
    
    # Verifie si le joueur touche le spike
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
    
    # Dessine le spike
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

    # Lancer l'entraînement des génomes
    def update(self):
        # Mettre à jour la grille
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

    # Vérifie les colisions
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
    
    #  Dessine le jeu
    def draw(self, screen):
        # Dessiner le fond
        screen.blit(self.background, (0, 0))

        # Dessiner les éléments du jeu (joueur et obstacles)
        for sprite in self.all_sprites:
            screen.blit(sprite.image, sprite.rect.move(-self.camera.x, -self.camera.y))

        # Dessiner le score
        self.draw_score(screen)
        
        # Positionner la grille pour que le joueur soit tout à gauche
        grid_x = self.player.rect.left  # Aligner la colonne gauche sur le joueur
        grid_y = (self.player.rect.centery - (self.grid.grid_size // 2) * self.grid.cell_size 
                - self.grid.cell_size / 2)  # Centrer verticalement et déplacer une demi-case plus haut

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
        font = pygame.font.SysFont("Arial", 30)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

    # Récupère l'état de la grille
    def get_state(self):
        # Récupérer l'état de la grille comme vecteur d'entrées pour NEAT
        return self.grid.get_grid_state()

    # Récupère le score
    def get_reward(self):
        return self.score

    # Verifie si le jeu est encore en cours
    def is_alive(self):
        return self.is_running

# Fonction pour charger le niveau à partir d'un fichier CSV
def load_level(filename):
    """Charger le niveau à partir d'un fichier CSV."""
    level = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            level.append(row)
    return level

# Fonction pour générer les obstacles à partir du niveau
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

# Charge le niveau
level = load_level('level_2.csv')
# Charge els obstacles
obstacles = generate_obstacles(level)

# Charger la progression (si elle existe)
population, generation, max_fitness = load_progress()
max_fitness_global = max_fitness

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

# Défini la génération
GENERATION = generation

# Fonction d'évaluation des génomes
def eval_genomes(genomes, config):
    global GENERATION, max_fitness_global
    GENERATION += 1  # Incrémenter la génération

    # Compteur d'individus
    individu = 0

    # Initialiser Pygame et l'écran
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Liste pour les réseaux et les jeux, réinitialisée pour chaque génération
    nets = []
    games = []
    print()
    # Afficher des informations au début de chaque génération
    print(f"            ************ DEBUT DE LA GENERATION {GENERATION} ************")
    print()

    # Afficher la fitness du meilleur génome précédent (s'il y en a un)
    if p.best_genome is None:
        print(f"[Début de la génération {GENERATION}] Aucun meilleur génome précédent trouvé. Initialisation.")
    else:
        print(f"[Début de la génération {GENERATION}] Meilleur génome précédent - Fitness = {p.best_genome.fitness}")

    # Créer les réseaux et initialiser les jeux pour chaque génome
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0  # Réinitialiser la fitness

        # Créer un nouveau jeu pour chaque génome
        game = Game()  # Assurez-vous que Game() crée un nouvel état pour chaque joueur
        game.grid = DetectionGrid(game.player)  # Associer une nouvelle grille
        games.append(game)

    # Si c'est la première génération, ou si aucun meilleur génome n'a été sauvegardé
    if p.best_genome is None:
        best_genome = None  # C'est la première génération, initialiser best_genome à None
        print(f"[Generation {GENERATION}] Aucun meilleur génome précédent.")
    else:
        best_genome = p.best_genome  # Charger le meilleur génome existant
        print(f"[Generation {GENERATION}] Meilleur génome précédent : Fitness = {p.best_genome.fitness}")

    # Boucle principale pour évaluer chaque génome
    for idx, (genome_id, genome) in enumerate(genomes):
        # Associer le réseau et le jeu correspondants
        net = nets[idx]
        game = games[idx]

        # Changer l'individu
        individu += 1
        if individu > 36:
            individu = 1

        # Placer un nouvel indicateur dans la grille
        running = True
        while running:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            # Obtenir l'état de la grille et passer dans le réseau
            grid_state = game.grid.get_grid_state()
            output = net.activate(grid_state)

            # Prendre une décision basée sur la sortie du réseau
            action = output.index(max(output))  # 0 ou 1
            if action == 1:
                game.player.jump()

            # Mettre à jour le jeu et calculer la fitness
            if game.is_alive():
                game.update()
                genome.fitness += game.get_reward()  # Augmenter la fitness
            else:
                running = False

            # Mise à jour du meilleur fitness global
            if genome.fitness > max_fitness_global:
                max_fitness_global = genome.fitness

            # Mettre à jour le meilleur génome de la génération
            if best_genome is None or genome.fitness > best_genome.fitness:
                best_genome = genome

            # Dessiner le jeu
            screen.fill(WHITE)
            game.draw(screen)

            # Afficher les informations de debug
            font = pygame.font.SysFont("Arial", 30)
            generation_text = font.render(f"Generation: {GENERATION}", True, (255, 255, 255))
            screen.blit(generation_text, (10, 10))

            fitness_current_text = font.render(f"Fitness actuel (ID {individu}): {genome.fitness}", True, (255, 255, 255))
            screen.blit(fitness_current_text, (10, 50))

            fitness_max_text = font.render(f"Fitness max global: {max_fitness_global}", True, (255, 255, 255))
            screen.blit(fitness_max_text, (10, 90))
            
            # Si c'est le premier individu de la génération, assignez le best_genome
            if individu == 1 and best_genome is not None:
                genome = best_genome  # Forcer le premier individu à être le meilleur génome

            pygame.display.flip()
            clock.tick(FPS)

    # Assigner le meilleur génome trouvé dans la génération à p.best_genome
    p.best_genome = best_genome
    print(f"[Fin de la génération {GENERATION}] Meilleur génome : Fitness = {best_genome.fitness}")
    
    # Sauvegarder la progression à la fin de la génération
    save_progress(p, GENERATION, max_fitness_global)

    # Debug final : afficher le meilleur génome après la génération
    print(f"[Generation {GENERATION}] Meilleur génome après évaluation : Fitness = {best_genome.fitness}")

    pygame.quit()




# Lancer l'entraînement
if __name__ == "__main__":
    
    # Charger le fichier de configuration NEAT
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.ini")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Créer une population NEAT
    if population is None:
        p = neat.Population(config)
    

    # Lancer l'entraînement des génomes
    p.run(eval_genomes, 1000)  # 50 générations d'entraînement

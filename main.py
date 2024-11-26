import pygame
from pygame.locals import *
from game import *  # Importer toutes les classes et fonctions depuis game.py
from player_ai import PlayerAI  # Importer la classe PlayerAI de player_ai.py
import config  # Importer la configuration
import neat
import os

# Initialiser Pygame
pygame.init()

# Définir la taille de la fenêtre
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))  # Utiliser config.WIDTH et config.HEIGHT
pygame.display.set_caption('Geometry Dash avec IA et Mode Manuel')

# Charger les images après l'initialisation de l'affichage
load_images()

# Charger l'image de fond
bg_image = pygame.image.load("assets/bg.png").convert()
bg_image = pygame.transform.scale(bg_image, (config.WIDTH, config.HEIGHT))  # Ajuster à la taille de la fenêtre

# Charger la carte
level = load_level('level_1.csv')  # Remplacer par le chemin correct de votre niveau
obstacles = generate_obstacles(level)

# Créer un groupe de sprites
all_sprites = pygame.sprite.Group()

# Calculer la largeur du niveau
level_width = len(level[0]) * TILE_SIZE  # Largeur du niveau

# Créer la caméra
camera = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)  # Utiliser config.WIDTH et config.HEIGHT

# Boucle de jeu
clock = pygame.time.Clock()


def eval_genomes(genomes, config):
    """Fonction de fitness pour évaluer les IA."""
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0  # Initialiser la fitness à 0
        player = Player()  # Créer un joueur
        running = True
        obstacles = generate_obstacles(level)  # Générer les obstacles
        
        while running:
            screen.blit(bg_image, (0, 0))  # Dessiner le fond

            # Trouver le prochain obstacle
            closest_obstacle = None
            for obstacle in obstacles:
                if obstacle.rect.x > player.rect.x:  # Obstacle devant le joueur
                    closest_obstacle = obstacle
                    break

            # Préparer les entrées pour le réseau neuronal
            if closest_obstacle:
                inputs = [
                    (closest_obstacle.rect.x - player.rect.x) / config.WIDTH,  # Distance x normalisée
                    (closest_obstacle.rect.y - player.rect.y) / config.HEIGHT,  # Distance y normalisée
                    player.vel_y / 10.0,  # Vitesse verticale normalisée
                ]
            else:
                inputs = [1, 1, player.vel_y / 10.0]

            # Obtenir la sortie du réseau
            output = net.activate(inputs)
            if output[0] > 0.5:  # Si la sortie est > 0.5, le joueur saute
                player.jump()

            # Mettre à jour le joueur
            player.update(obstacles)
            if player.rect.y > config.HEIGHT or player.rect.x < 0:
                running = False  # Fin de la simulation si le joueur meurt

            # Afficher les sprites
            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))
            pygame.display.flip()
            clock.tick(60)

            # Incrémenter la fitness en fonction de la distance parcourue
            genome.fitness += 0.1


def neat_mode():
    """Lancer le mode IA."""
    # Charger le fichier de configuration NEAT
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.txt")
    # print(neat.DefaultSpeciesSet.compatibility_disjoint_coefficient)
    
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )
    

    # Créer une population NEAT
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Lancer l'évolution
    winner = population.run(eval_genomes, 50)  # 50 générations

    # Afficher le gagnant
    print("\nMeilleur génome :\n{!s}".format(winner))


def manual_mode():
    """Lancer le mode manuel."""
    player = Player()
    all_sprites.add(player)
    all_sprites.add(*obstacles)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    player.jump()  # Le joueur saute si la touche espace est appuyée

        # Mettre à jour les sprites
        all_sprites.update(obstacles)

        # Mettre à jour la caméra pour suivre le joueur
        camera.centerx = player.rect.centerx
        camera.x = max(0, camera.x)
        camera.x = min(camera.x, level_width - config.WIDTH)

        # Dessiner le fond
        screen.blit(bg_image, (0, 0))

        # Dessiner les sprites
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))

        # Actualiser l'affichage
        pygame.display.flip()

        # Limiter les FPS
        clock.tick(60)


def main_menu():
    """Afficher le menu principal et choisir le mode."""
    font = pygame.font.Font(None, 36)
    running = True

    while running:
        screen.fill((0, 0, 0))
        title_text = font.render("Geometry Dash - Choisissez un mode", True, (255, 255, 255))
        manual_text = font.render("1. Mode Manuel", True, (255, 255, 255))
        ai_text = font.render("2. Mode IA", True, (255, 255, 255))
        screen.blit(title_text, (config.WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(manual_text, (config.WIDTH // 2 - manual_text.get_width() // 2, 300))
        screen.blit(ai_text, (config.WIDTH // 2 - ai_text.get_width() // 2, 350))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_1:
                    manual_mode()  # Mode manuel
                elif event.key == K_2:
                    neat_mode()  # Mode IA


if __name__ == "__main__":
    main_menu()
    pygame.quit()

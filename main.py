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
    """Évaluation des génomes."""
    for genome_id, genome in genomes:
        print(f"Évaluation du génome {genome_id}")  # Afficher l'ID du génome actuel
        
        # Créer un réseau neuronal pour ce génome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0  # Initialiser la fitness à 0

        # Effacer tous les anciens joueurs du groupe de sprites
        all_sprites.empty()  # Vide le groupe de sprites

        # Créer un nouveau joueur AI pour ce génome
        player_ai = PlayerAI(genome, config, level, obstacles)  # Passer les bons arguments pour PlayerAI
        all_sprites.add(player_ai)  # Ajouter le nouveau joueur AI au groupe de sprites
        
        last_fitness = genome.fitness  # Suivi de la dernière fitness
        all_sprites.add(*obstacles)  # Ajouter les obstacles au groupe de sprites

        # Boucle de jeu pour cet individu
        while player_ai.running:  # Tant que player_ai.running est True, la boucle continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('Fermeture de la fenêtre détectée.')
                    player_ai.running = False  # Fermer proprement la boucle si l'utilisateur ferme la fenêtre
                    break

            # Dessiner le fond
            screen.blit(bg_image, (0, 0))

            # Préparer les entrées pour le réseau neuronal
            inputs = player_ai.get_inputs()
            output = net.activate(inputs)

            # Si la sortie est > 0.5, le joueur saute
            if output[0] > 0.5:
                player_ai.jump()

            # Mettre à jour l'IA du joueur
            player_ai.updateAI()

            # Vérification si le joueur meurt (appel à die)
            if player_ai.rect.y > 600 or player_ai.rect.x < 0:
                # Le joueur est mort, donc on met à jour la fitness et on arrête l'évaluation
                genome.fitness += 0.1  # Ajouter une récompense pour avoir survécu un peu
                print(f"Génome {genome_id} mort, fitness finale : {genome.fitness}")
                
                # Appeler la méthode die pour mettre running à False
                player_ai.die()  # La méthode die() met running à False
                break  # Fin de l'évaluation de ce génome

            # Augmenter la fitness pendant que le joueur est en vie
            genome.fitness += 0.1  # Plus le joueur reste en vie longtemps, plus la fitness augmente

            # Vérifier si la fitness a diminué, si c'est le cas, on passe au génome suivant
            if genome.fitness < last_fitness:
                print(f"Fitness a diminué pour le génome {genome_id}, passage au génome suivant.")
                break  # Sortir de la boucle pour ce génome

            # Mettre à jour la dernière fitness
            last_fitness = genome.fitness

            # Mise à jour de la caméra et affichage des éléments
            camera.centerx = player_ai.rect.centerx
            camera.x = max(0, camera.x)
            camera.x = min(camera.x, level_width - 800)

            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))

            pygame.display.flip()  # Mettre à jour l'affichage
            clock.tick(60)  # Limiter les FPS

        # Fin de l'évaluation pour ce génome. L'IA passe au génome suivant dans la boucle.
        print(f"Évaluation terminée pour le génome {genome_id} avec fitness: {genome.fitness}")

def neat_mode():
    """Lancer le mode IA."""
    # Charger le fichier de configuration NEAT
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.ini")

    # Créer la configuration NEAT
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
    winner = population.run(eval_genomes, 50)  # Réduit le nombre de générations pour les tests

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
        camera.x = min(camera.x, level_width - 800)

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
    main_menu()  # Afficher le menu principal
    pygame.quit()  # Quitter Pygame

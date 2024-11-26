import neat
import pygame
from game import *  # Importer toutes les classes du jeu
from player_ai import PlayerAI  # Importer la classe PlayerAI

def run_neat(config_file):
    """Exécute NEAT et entraîne l'IA à jouer."""
    # Charger la configuration de NEAT
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Créer une population
    population = neat.Population(config)

    # Ajouter des statistiques pour suivre l'évolution
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    # Créer une fonction d'évaluation qui appelle la méthode `update` de PlayerAI
    def eval_genomes(genomes, config):
        for genome_id, genome in genomes:
            genome.fitness = 0
            player_ai = PlayerAI(genome, config)  # Créer une instance de l'IA
            obstacles = generate_obstacles(load_level('level_1.csv'))
            fitness = player_ai.update(obstacles)  # Mettre à jour l'IA
            genome.fitness = fitness

    # Configurer l'évaluation de l'IA
    population.run(eval_genomes, 50)  # Lancer l'évolution pour 50 générations

if __name__ == "__main__":
    config_file = "config-feedforward.txt"  # Fichier de configuration NEAT
    run_neat(config_file)

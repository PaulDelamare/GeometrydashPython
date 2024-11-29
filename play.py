# Import dépendances
import neat
import os

# Import FOnction
from Function.load_progress import load_progress

# Import Class
from Class.GenomeEvaluator import GenomeEvaluator

# Charger la progression (si elle existe)
population, generation, max_fitness_global = load_progress()

# Créer une population NEAT
if population is None:
    # Récupère le fichier Config NEAT
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.ini")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    # Créer une nouvelle population si aucune sauvegarde
    p = neat.Population(config)  
else:
    # Si la population est chargée, la réutiliser
    p = population

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
    evaluator = GenomeEvaluator(config, p, max_fitness_global, generation)
    p.run(evaluator.eval_genomes, 50)

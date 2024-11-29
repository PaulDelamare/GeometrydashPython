# Import dépendances
import pickle

def save_progress(population, generation, max_fitness, filename='save_state.pkl'):
    """ Sauvegarde la progression de la simulation (population, génération, fitness max, etc.). """
    
    # Sauvegarde de la population, génération et fitness max
    with open(filename, 'wb') as f:
        # On sauvegarde la population, la génération, et le fitness max
        pickle.dump((population, generation, max_fitness), f)
    
    print(f"Progression sauvegardée sous : {filename}")

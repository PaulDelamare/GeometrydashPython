# Import dépendances
import os
import pickle

def load_progress(filename='save_state.pkl'):
    """
    Charge la progression d'une partie sauvegardée.

    La fonction charge un fichier de sauvegarde et renvoie la population, la génération courante et le fitness maximum.
    Si le fichier n'existe pas, recommence une nouvelle partie.

    :param str filename: Le nom du fichier de sauvegarde (par défaut 'save_state.pkl')
    :return: La population, la génération courante et le fitness maximum, ou None, 0, 0 si la sauvegarde n'existe pas.
    :rtype: tuple[neat.Population, int, float]
    """
   
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
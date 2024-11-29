# Import Dépendances
import csv

def load_level(filename):
    """Charger le niveau à partir d'un fichier CSV."""
    level = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            level.append(row)
    return level

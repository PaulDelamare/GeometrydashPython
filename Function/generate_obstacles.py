# Import Class
from Class.Obstacle import Obstacle
from Class.Spike import Spike
from Class.End import End

# Import Variable
from config import TILE_SIZE, block_image_size

def generate_obstacles(level):
    """Générer les obstacles à partir du niveau."""
    obstacles = []
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            if cell == '0':  # Bloc solide
                obstacles.append(Obstacle(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, block_image_size))
            elif cell.lower() == 'spike':  # Spike
                obstacles.append(Spike(x * TILE_SIZE, y * TILE_SIZE))  # Ajoute un obstacle de type spike
            elif cell.lower() == 'end':  # Goal
                obstacles.append(End(x * TILE_SIZE, y * TILE_SIZE))
    return obstacles
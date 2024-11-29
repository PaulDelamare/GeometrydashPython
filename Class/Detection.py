# Import Dependances
import pygame

# Import Class
from Class.Spike import  Spike

class DetectionGrid:
    def __init__(self, player, grid_size=7, cell_size=40):
        self.player = player
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.grid = [[0] * grid_size for _ in range(grid_size)]  # 0 = vide, 1 = bloc, 2 = pique
        self.indicator_pos = None  # Indicateur de position
        self.gridWithout3 = [[0] * grid_size for _ in range(grid_size)]  # Grille sans l'indicateur

    def update(self, obstacles):
        # Réinitialiser la grille à vide
        
        """
        Met à jour la grille de détection en fonction de la position actuelle du joueur et des obstacles.

        Cette fonction réinitialise la grille et vérifie chaque cellule pour déterminer si elle contient
        un obstacle (soit un bloc, soit un pique). La position du joueur est utilisée comme référence
        pour calculer les coordonnées de la grille. Si un obstacle est détecté dans une cellule, elle est marquée
        en conséquence dans la grille.

        Args:
            obstacles (list): Une liste d'objets d'obstacles à vérifier pour les collisions avec les cellules de la grille.
        """
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
        """
        Dessine la grille sur l'écran.

        :param screen: L'écran sur lequel la grille sera dessinée.
        :type screen: pygame.Surface
        """
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
        """
        Retourne l'état de la grille sous forme de vecteur pour l'IA.

        :return: L'état de la grille en tant que liste 1D.
        :rtype: List[int]
        """
        
        return [cell for row in self.grid for cell in row]  # Transforme la grille en un vecteur 1D

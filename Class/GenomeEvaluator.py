# Import Dependances
import pygame
import neat
import sys

# Import Class
from Class.Game import Game
from Class.Detection import DetectionGrid

# Import Fonction
from Function.save_progress import save_progress

# Import Variable
from config import  SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE


class GenomeEvaluator:
    def __init__(self, config, p, max_fitness_global=-float('inf'), generation = 0):
        self.config = config
        self.p = p
        self.GENERATION = generation
        self.max_fitness_global = max_fitness_global
        self.previous_fitness = 0

    def eval_genomes(self, genomes, config):
        """
        Méthode d'évaluation des génomes NEAT. Elle crée un jeu pour chaque génome, 
        évalue les réseaux de neurones correspondants et met à jour les fitness.
        """
        self.GENERATION += 1  # Incrémenter la génération

        # Compteur d'individus
        individu = 0

        # Initialiser Pygame et l'écran
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()

        # Liste pour les réseaux et les jeux, réinitialisée pour chaque génération
        nets = []
        games = []

        # Variable pour stocker le meilleur fitness de la génération en cours
        max_fitness_generation = -float('inf')  # Initialisé à une très faible valeur

        print()
        # Afficher des informations au début de chaque génération
        print(f"            ************ DEBUT DE LA GENERATION {self.GENERATION} ************")
        print()

        # Afficher la fitness du meilleur génome précédent (s'il y en a un)
        if self.p.best_genome is None:
            print(f"[Début de la génération {self.GENERATION}] Aucun meilleur génome précédent trouvé. Initialisation.")
        else:
            print(f"[Début de la génération {self.GENERATION}] Meilleur génome précédent - Fitness = {self.max_fitness_global}")

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
        if self.p.best_genome is None:
            best_genome = None  # C'est la première génération, initialiser best_genome à None
            print(f"[Generation {self.GENERATION}] Aucun meilleur génome précédent.")
        else:
            best_genome = self.p.best_genome  # Charger le meilleur génome existant

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
                
                if game.is_win():
                    genome.fitness = 10000000000000
                    running = False

                # Mise à jour du meilleur fitness global
                if genome.fitness > self.max_fitness_global:
                    self.max_fitness_global = genome.fitness

                # Mise à jour du meilleur fitness pour la génération en cours
                if genome.fitness > max_fitness_generation:
                    max_fitness_generation = genome.fitness

                # Mettre à jour le meilleur génome de la génération
                if best_genome is None or genome.fitness > best_genome.fitness:
                    best_genome = genome

                # Dessiner le jeu
                screen.fill(WHITE)
                game.draw(screen)

                # Afficher les informations de debug
                font = pygame.font.SysFont("Arial", 30)
                generation_text = font.render(f"Generation: {self.GENERATION}", True, (255, 255, 255))
                screen.blit(generation_text, (10, 10))

                fitness_current_text = font.render(f"Fitness actuel (ID {individu}): {genome.fitness}", True, (255, 255, 255))
                screen.blit(fitness_current_text, (10, 50))

                fitness_max_text = font.render(f"Fitness max global: {self.max_fitness_global}", True, (255, 255, 255))
                screen.blit(fitness_max_text, (10, 90))

                # Afficher le meilleur fitness de la génération
                fitness_generation_text = font.render(f"Fitness max génération {self.GENERATION}: {max_fitness_generation}", True, (255, 255, 255))
                screen.blit(fitness_generation_text, (10, 130))

                pygame.display.flip()
                clock.tick(FPS)

            # Mettez à jour la variable précédente pour la prochaine génération
            previous_fitness = max_fitness_generation

        # Assigner le meilleur génome trouvé dans la génération à p.best_genome
        self.p.best_genome = best_genome
        print(f"[Fin de la génération {self.GENERATION}] Meilleur génome : Fitness = {best_genome.fitness}")
        print(f"[Fin de la génération {self.GENERATION}] Meilleur fitness de la génération {max_fitness_generation}")

        # Sauvegarder la progression à la fin de la génération
        save_progress(self.p, self.GENERATION, self.max_fitness_global)

        # Debug final : afficher le meilleur génome après la génération
        print(f"[Generation {self.GENERATION}] Meilleur génome après évaluation : Fitness = {best_genome.fitness}")

        pygame.quit()


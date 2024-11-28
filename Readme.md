# Geometry Dash'ier
Ce programme est une démonstration d'un modèle NEAT (Neuroevolution of augmenting topologies). Il fait jouer à une machine learning le jeu Geometry Dash.

## Fonctionnement du NEAT

NEAT (NeuroEvolution of Augmenting Topologies) est un algorithme d'évolution artificielle qui permet de faire évoluer des réseaux de neurones. Dans le cas de Geometry Dash, il sert à créer des IA capables de jouer de manière de plus en plus complexe. Il permet d'analyser l'environnement autour du joueur pour permettre au système d'effectuer des choix par rapport à celui-ci. Pour cela, il place des neurones sur des emplacements de son environnement virtuel. Suite à cela, le système analyse si un élément (Pique, block ou vide) passe devant son neurone pour actionner son action. Il y a donc un neurone par type de block, mais existe également les neurones "anti-block". Ces neurones ont un système différent. Ils analysent quand **il n'y a pas** le block sur le neurone pour effectuer l'action. Tout cela est fait de manière aléatoire et un système de récompenses permet au NEAT de comprendre ce qui a fonctionné. Dans notre cas, la distance parcourue est la récompense. Pour rendre le système plus complexe et permettre plus de possibilités, NEAT créer des réseaux. Un réseau est un ensemble de neurones. L'action s'active si tous ces neurones remplissent leur condition. Ce genre de système fonctionne par génération. Une génération est un ensemble d'individus, c'est-à-dire que si une génération possède 10 individus, alors elle fonctionnera 10 fois de manière différente. Tous les individus fonctionneront de manière aléatoire et n'apprendront pas les unes des autres. Une fois la génération terminée, la prochaine génération héritera de certaines caractéristiques de l'individu ayant réalisé les meilleures performances, mais tout en gardant certains individus avec un comportement encore aléatoire. En effet, même si une solution permet de gagner le plus de point, elle n'est pas forcément la seule fonctionnelle ou la plus intéressante pour la suite de la progression. C'est pour cela qu'on peut constater que le système n'apprend pas tout le temps de ce qu'il a préalablement réalisé.

## Prérequis

- Posséder Python version 3.11 : https://www.python.org/downloads/release/python-3110/
  
## Faire fonctionner le projet

- Récupèrer le projet :
```bash
git clone https://github.com/PaulDelamare/GeometrydashPython.git
```

- Entrer sur le projet :
```bash
cd GeometrydashPython
```
# Extracteur Web & Générateur de Pages HTML

Ce projet a été développé par Yanis Boulogne et Karl-Antoine Plouffe pour le cours IFT3225 à l'Université de Montréal.

## Objectif du projet

L'objectif principal de ce projet est de créer un outil en ligne de commande qui:
1. Extrait des médias (images, vidéos, SVG) à partir de sites web
2. Génère des pages HTML présentant les médias extraits
3. Fonctionne avec différents types de sites et différentes configurations

## Fonctionnalités principales

### Extraction de médias
- Extraction d'images (formats JPG, PNG, etc.)
- Extraction de vidéos
- Extraction de SVG (fichiers .svg et SVG inline)
- Options de filtrage par type de média et formats spécifiques
- Gestion des chemins relatifs et absolus
- Sauvegarde locale des médias extraits

### Génération de pages HTML
- Création de pages HTML structurées à partir des médias extraits
- Utilisation d'un gabarit HTML pour une génération élégante
- Intégration de Bootstrap pour un design responsive
- Manipulation du DOM avec JavaScript
- Affichage optimisé des différents types de médias

## Stack technique

- **Python**: Extraction des données avec BeautifulSoup et requests
- **JavaScript**: Manipulation du DOM et interactivité de la page générée
- **TCSH**: Scripts wrapper pour faciliter l'exécution des commandes
- **Bootstrap**: Framework CSS pour le design de la page générée
- **HTML/CSS**: Structure et présentation des pages générées

## Installation et exécution

### Prérequis
- Python 3
- TCSH (shell)
- Les bibliothèques Python suivantes:
  - BeautifulSoup 4
  - requests
  - sys, os, re, io (intégrées à Python)

### Installation des dépendances

```bash
pip install beautifulsoup4 requests
```

### Exécution

Le projet comporte deux commandes principales:
- `extract`: Extrait les médias d'un site web
- `genere`: Génère une page HTML à partir des médias extraits

#### Extraction des médias
```bash
./extract [options] "URL"
```
Options disponibles:
- `-p <dossier>`: Spécifie le dossier de destination pour les médias extraits
- `-i`: Extrait les images
- `-v`: Extrait les vidéos
- `-s`: Extrait les SVG
- `-r <extension>`: Filtre les médias par extension
- `-u`: Évite de télécharger les images externes

#### Génération de la page HTML
```bash
./extract [options] "URL" | ./genere > page.html
```

### Exemples d'utilisation

#### Exemple 1: Extraction d'images et vidéos
```bash
./extract -p ./img1 -i -v "https://www.ableton.com/en/" | ./genere > page1.html
```

#### Exemple 2: Extraction de SVG
```bash
./extract -p ./img2 -s "https://www.ville-dechy.fr/" | ./genere > page2.html
```

#### Exemple 3: Extraction d'images filtrées par extension
```bash
./extract -p ./img3 -r .jpg -s "https://www.umontreal.ca/" | ./genere > page3.html
```

## Structure du projet

- `extract`: Script wrapper TCSH pour lancer l'extraction
- `extract.py`: Module Python pour l'extraction des médias
- `genere`: Script wrapper TCSH pour la génération
- `genere.py`: Module Python pour la génération de pages HTML
- `template.html`: Gabarit HTML utilisé pour la génération de pages

## Défis rencontrés et solutions

### 1. Récupération d'images avec chemins complexes
**Problème**: Les images peuvent avoir des chemins relatifs complexes ou être situées à différents niveaux dans la structure du site.

**Solution**: Nous avons implémenté un algorithme qui part de la racine de l'URL et remonte progressivement en ajoutant les sous-dossiers présents dans l'URL de base jusqu'à trouver l'image ou atteindre l'URL fournie par l'utilisateur.

### 2. Gestion des SVG inline
**Problème**: Les SVG peuvent être présents soit sous forme de fichiers .svg, soit directement intégrés dans le HTML (inline).

**Solution**: Nous avons créé des fonctions spécifiques pour extraire et traiter les deux types de SVG. Pour les SVG inline, nous récupérons le contenu entre les balises `<svg>` et leur donnons un nom basé sur leur ID s'il existe, sinon un nom générique.

### 3. Images externes
**Problème**: Certaines pages affichent des images hébergées sur d'autres domaines.

**Solution**: Nous avons ajouté l'option `-u` pour permettre à l'utilisateur de choisir s'il souhaite télécharger ces images externes. Si nécessaire, nous ajoutons une extension aux images qui n'en ont pas.

### 4. Génération propre de HTML
**Problème**: Générer du HTML propre et structuré peut être complexe en Python.

**Solution**: Nous avons utilisé un gabarit HTML externe dans lequel nous insérons les ressources extraites, plutôt que de construire le HTML avec des chaînes de caractères, ce qui rend le code plus lisible et maintenable.

## Répartition des tâches

### Yanis Boulogne
- Création du module Python pour extraire les images, vidéos et SVG
- Création du module Python pour générer la page web en intégrant les médias extraits

### Karl-Antoine Plouffe
- Création du gabarit HTML
- Implémentation des styles avec Bootstrap
- Implémentation du scriptage DOM avec JavaScript
- Création des scripts "wrapper"
- Tests d'exécution des commandes
- Rédaction du rapport

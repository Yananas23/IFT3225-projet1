#!/usr/bin/tcsh -f


# Initialisation des variables
set regex = ""
set path = ""
set url = ""
set img = "true"
set vid = "true"

# Vérification des arguments
if ($#argv == 0) then
    goto afficher_aide
endif

while ($#argv > 0)
    switch ($argv[1])
        case "-r":  # Option -r (Regex)
            if ($#argv < 2) then
                echo "Erreur: -r nécessite une regex en argument."
                exit 1
            endif
            $regex = $argv[2]
            shift  # Supprime "-r"
            shift  # Supprime la regex
            breaksw

        case "-p":  # Option -p (Path)
            if ($#argv < 2) then
                echo "Erreur: -p nécessite un chemin en argument."
                exit 1
            endif
            set path = $argv[2]
            shift  # Supprime "-p"
            shift  # Supprime le chemin
            breaksw

        case "-i": # Option -i, retire les images du résultat
            set img = "false"
            breaksw

        case "-v": # Option -v, retire les vidéos du résultat
            set vid = "false"
            breaksw

        case "-h":  # Option d'aide
            goto afficher_aide
            breaksw

        default:  # Si ce n'est pas une option, on suppose que c'est une URL
            if ("$url" != "") then
                echo "Erreur: Une seule URL est autorisée."
                exit 1
            endif
            set url = $argv[1]
            shift  # Supprime l'URL
            breaksw
    endsw
end

# Vérification et affichage des valeurs récupérées
if ("$url" == "") then
    echo "Erreur: Aucun paramètre fourni."
    goto afficher_aide
else
    goto get_all
endif

# Sortir du script
exit 0

# Label pour afficher le message d'aide
afficher_aide:
    echo "Usage: extract [-r <regex>] [-i] [-v] [-p <path>] <url>"
    echo ""
    echo "Options:"
    echo "  -r <regex>  Filtrer les ressources par une expression régulière sur leur nom"
    echo "  -i          Exclure les éléments <img> de la liste"
    echo "  -v          Exclure les éléments <video> de la liste"
    echo "  -p <path>   Copier les ressources img et/ou vidéo dans <path>"
    echo "  -h          Afficher ce message d'aide et quitter"
    echo ""
    echo "Auteurs: Yanis Boulogne - Karl-Antoine Plouffe"
exit 1


get_all:
    echo a faire


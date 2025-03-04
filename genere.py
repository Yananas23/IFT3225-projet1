#!/usr/bin/python3
import sys
import re
import io

# Forcer l'encodage en UTF-8 sur l'entrée/sortie
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def help():
    """
    Affiche le message d'aide pour l'utilisation du script.
    """
    print("Usage: extract | genere >! fichier_sortie")
    print("Options:")
    print("  -h              Affiche ce message d'aide et les auteurs")
    print("fichier_sortie    Nom du fichier HTML généré (ex: mapage.html)")
    print("Auteurs: Yanis Boulogne - Karl-Antoine Plouffe")
    sys.exit(0)

def generer_html(images, videos):
    """
    Génère le contenu HTML en insérant les ressources images et vidéos dans un modèle existant.

    :param images: Liste de tuples (src, alt) représentant les images.
    :param videos: Liste des chemins des vidéos.
    :return: Contenu HTML sous forme de chaîne de caractères avec les ressources insérées dans la balise <tbody>.

    Cette fonction lit un fichier template.html existant et y insère les ressources fournies (images et vidéos)
    dans la section <tbody>. En cas d'erreur de lecture du modèle, le script s'arrête avec un message approprié.
    """
    try:
        with open("$2y$10$16Z2JOTZ74IW9OcZejNYjeyTawTpXXqt4iOrt282RdtE095khYjUm.html", "r", encoding="utf-8") as template_file:
            template = template_file.read()
    except FileNotFoundError:
        print("Erreur: Le fichier template.html est introuvable.")
        sys.exit(1)

    ressources_html = ""
    ressources_html += f"<tr class=\"d-none\"></tr>\n"

    for src, alt in images:
        ressources_html += f"<tr><td>{src}</td><td>{alt}</td></tr>\n"

    for src in videos:
        ressources_html += f"<tr><td>{src}</td><td>Video</td></tr>\n"

    # Remplacement du contenu de <tbody> par les ressources
    template = re.sub(r'(<tbody>.*?</tbody>)', f"<tbody>{ressources_html}</tbody>", template, flags=re.S)

    return template

def adjust_src(path, src):
    """
    Ajuste le chemin d'une ressource en fonction du chemin de base fourni.

    :param path: Chemin de base donné (ex: './' ou une URL).
    :param src: Chemin relatif de la ressource.
    :return: Chemin ajusté de la ressource sous forme de chaîne de caractères.

    Si le chemin commence par './', seule la dernière partie du chemin est conservée.
    Si le chemin est une URL, il est concaténé directement avec la source.
    """
    if path.endswith("./"):
        # Garde uniquement ce qui suit le dernier '/'
        src = src.rsplit("/", 1)[-1]
        return f"{path}{src}"    
    elif path.startswith("./") or path.startswith("/"):
        src = src.rsplit("/", 1)[-1]
        return f"{path}/{src}"    
    elif path.startswith("http"):
        return f"{path}{src}"    
    else:
        src = src.rsplit("/", 1)[-1]
        return f"{path}/{src}"


def main():
    """
    Fonction principale du script.
    
    Cette fonction lit l'entrée standard, analyse les informations sur les images et vidéos,
    ajuste les chemins des ressources, et génère un contenu HTML.
    """
    args = sys.argv
    if "-h" in args or len(args) == 0:
        help()
        return

    images = []
    videos = []
    path = ""

    # Lecture de l'entrée standard
    for line in sys.stdin:
        line = line.strip()
        if line.startswith("PATH"):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                _, path = parts

        elif line.startswith("IMAGE"):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                _, src, alt = parts
                adjusted_src = adjust_src(path, src)
                images.append((adjusted_src, alt.strip('"')))

        elif line.startswith("VIDEO"):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                _, src = parts
                adjusted_src = adjust_src(path, src)
                videos.append(adjusted_src)

    html_content = generer_html(images, videos)

    print(html_content.encode('utf-8').decode('utf-8'))

if __name__ == "__main__":
    main()

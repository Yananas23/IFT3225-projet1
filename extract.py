#!/usr/bin/python3
import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import io

# Forcer l'encodage en UTF-8 sur l'entrée/sortie
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fetch_content(url):
    """
    Récupère le contenu HTML d'une URL donnée.
    
    :param url: L'URL de la page à récupérer
    :return: Le contenu HTML sous forme de texte, ou None en cas d'erreur
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        response.encoding = 'utf-8'  # Force le décodage en UTF-8
        return response.text
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de la page: {e}")
        return None

def extract_images(soup, regex_filter, exclude_svg = True):
    """
    Extrait les images d'un objet BeautifulSoup.
    
    :param soup: L'objet BeautifulSoup analysant la page HTML
    :param regex_filter: Une expression régulière pour filtrer les images (facultatif)
    :return: Une liste de tuples contenant le chemin de l'image et son attribut alt
    """
    images = []
    for img in soup.find_all("img"):  # Recherche toutes les balises <img>
        src = img.get("src").lstrip("./")  # Supprime le ./ du chemin de l'URL
        alt = img.get("alt", "")  # Récupère le texte alternatif si présent
        if src:
            # Exclure les .svg si demandé
            if exclude_svg and src.lower().endswith(".svg"):
                continue
            if not regex_filter or re.search(regex_filter, src):
                images.append((src, alt))  # Ajoute l'image et son alt à la liste
    return images

def extract_videos(soup, regex_filter):
    """
    Extrait les vidéos d'un objet BeautifulSoup.
    
    :param soup: L'objet BeautifulSoup analysant la page HTML
    :param regex_filter: Une expression régulière pour filtrer les vidéos (facultatif)
    :return: Une liste des sources des vidéos
    """
    videos = []
    for video in soup.find_all("video"):  # Recherche toutes les balises <video>
        for source in video.find_all("source"):  # Recherche toutes les sources dans <video>
            src = source.get("src").lstrip("./")  # Supprime le ./ du chemin de l'URL
            if src:
                if not regex_filter or re.search(regex_filter, src):
                    videos.append(src)  # Ajoute la vidéo à la liste
    return videos

def extract_svg(soup):
    """
    Extrait les SVG inline et ceux liés via des balises <img>

    :param soup: L'objet BeautifulSoup analysant la page HTML
    :return: Une liste de tuples
    """
    svgs = []

    # SVG inline avec id ou un nom unique généré
    for i, svg in enumerate(soup.find_all("svg")):
        svg_content = str(svg)

        # Récupération du nom : id > génération unique
        svg_id = svg.get("id")
        name = svg_id if svg_id else f"inline{i}"

        svgs.append((svg_content, name))

    # SVG via <img> (en réutilisant l'approche du regex)
    for img in extract_images(soup, ".svg", False):
        svgs.append(img)

    return svgs

def save_files(files, url, save_path):
    """
    Télécharge et enregistre les fichiers extraits (images ou vidéos).
    
    :param files: Liste des fichiers à télécharger
    :param url: URL de la page d'origine
    :param save_path: Dossier de sauvegarde des fichiers
    """
    os.makedirs(save_path, exist_ok=True)  # Crée le répertoire de destination si inexistant

    def join_url(base, path):
        """Concatène un chemin à une URL en gérant les séparateurs."""
        if not base.endswith('/'):
            base += '/'
        return base + path.lstrip('/')

    def get_root_url(url):
        """Extrait la racine d'une URL (ex: http://site.fr)."""
        parts = url.split('/')
        return f"{parts[0]}//{parts[2]}"

    for file_url, _ in files:
        file_name = os.path.join(save_path, os.path.basename(file_url))

        # 1. Explorer en ajoutant des niveaux (vers le bas)
        urls_to_try = []
        root_url = get_root_url(url)

        # Récupérer la partie après le domaine
        path_after_root = url[len(root_url):].strip('/')

        # Construire les sous-dossiers progressivement
        sub_paths = path_after_root.split('/')
        current_path = root_url

        for folder in sub_paths:
            current_path = join_url(current_path, folder)
            urls_to_try.append(join_url(current_path, file_url))

        # 2. Essayer l'URL directe en dernier
        urls_to_try.append(join_url(url, file_url))

        # Télécharger le fichier
        for full_url in urls_to_try:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(full_url, headers=headers, stream=True)
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    break
            except requests.RequestException as e:
                print(f"Erreur lors du téléchargement de {full_url}: {e}")
                
def ensure_svg_namespace(svg_content):
    """
    Vérifie et ajoute l'attribut xmlns à l'élément SVG si nécessaire.

    :param svg_content: Contenu SVG sous forme de chaîne.
    :return: Contenu SVG modifié avec l'attribut xmlns ajouté si nécessaire.
    """
    soup = BeautifulSoup(svg_content, "html.parser")
    svg_tag = soup.find("svg")

    if svg_tag and 'xmlns' not in svg_tag.attrs:
        svg_tag.attrs['xmlns'] = "http://www.w3.org/2000/svg"

    return str(soup)                

def save_svg(svg_list, url, save_path):
    """
    Télécharge et enregistre les fichiers SVG ou extrait les SVG inline.
    
    :param svg_list: Liste des SVG (URL de fichiers ou code inline)
    :param url: URL de la page d'origine
    :param save_path: Dossier de sauvegarde des fichiers
    """
    os.makedirs(save_path, exist_ok=True)  # Crée le dossier si inexistant

    for svg, index in svg_list:
        if svg.startswith("<svg"):  # SVG inline détecté
            try:
                soup = BeautifulSoup(svg, "html.parser")
                svg_content = ensure_svg_namespace(soup.prettify())  # Nettoie le SVG
                
                file_name = os.path.join(save_path, f"{index}.svg")
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                print(f"SVG {file_name} \"Inline\"")
            except Exception as e:
                print(f"Erreur lors de l'enregistrement du SVG inline : {e}")

        elif svg.endswith(".svg"):  # Fichier SVG externe
            # Appel de la fonction save_files pour les SVG externes
            save_files([(svg, None)], url, save_path)
            
def help():
    """
    Affiche le message d'aide pour l'utilisation du script.
    """
    print("Usage: extract [-r <regex>] [-i] [-v] [-s] [-p <path>] <url>\n")
    print("Options:")
    print("  -r <regex>  Filtrer les ressources par une expression régulière sur leur nom")
    print("  -i          Exclure les éléments <img> de la liste")
    print("  -v          Exclure les éléments <video> de la liste")
    print("  -s          Exclure les éléments <svg> et .svg de la liste")
    print("  -p <path>   Copier les ressources img et/ou vidéo dans <path>")
    print("  -h          Afficher ce message d'aide et quitter\n")
    print("Auteurs: Yanis Boulogne - Karl-Antoine Plouffe")
    

def main():
    """
    Fonction principale du script.
    
    Analyse les arguments et exécute les actions appropriées.
    """
    import sys
    args = sys.argv[1:]
    if "-h" in args or len(args) == 0:
        help()
        return

    # Initialisation des variables
    url = None
    regex_filter = None
    save_path = None
    no_images = False
    no_videos = False
    no_svg = False
    
    # Analyse des arguments passés au script
    i = 0
    while i < len(args):
        if args[i] == "-r" and i + 1 < len(args):
            regex_filter = args[i + 1]  # Stocke le filtre regex
            i += 1
        elif args[i] == "-p" and i + 1 < len(args):
            save_path = args[i + 1]  # Définit le chemin de sauvegarde
            i += 1
        elif args[i] == "-i":
            no_images = True  # Désactive l'extraction des images
        elif args[i] == "-v":
            no_videos = True  # Désactive l'extraction des vidéos
        elif args[i] == "-s":
            no_svg = True  # Désactive l'extraction des SVGs
        else:
            if url is None:
                url = args[i]  # Récupère l'URL fournie
            else:
                print("Erreur: Une seule URL est autorisée.")
                return
        i += 1
    
    # Vérifie si une URL a été fournie
    if not url:
        print("Erreur: Aucun paramètre fourni.")
        return
    
    # Récupération du contenu de la page
    page_content = fetch_content(url)
    if not page_content:
        return
    
    soup = BeautifulSoup(page_content, "html.parser")
    
    print(f"PATH: {save_path if save_path is not None else url}")
    
    # Extraction des images si activé
    if not no_images:
        images = extract_images(soup, regex_filter)
        for src, alt in images:
            print(f"IMAGE {src} \"{alt}\"")
        if save_path:
            save_files(images, url, save_path)
    
    # Extraction des vidéos si activé
    if not no_videos:
        videos = extract_videos(soup, regex_filter)
        for src in videos:
            print(f"VIDEO {src}")
        if save_path:
            save_files(videos, url, save_path)
            
    # Extraction des svg si activé
    if not no_svg:
        svg = extract_svg(soup)
        for src, alt in svg:
            if not save_path or (save_path and src.endswith(".svg")):
                print(f"SVG {src} \"{alt}\"")            
        if save_path:
                save_svg(svg, url, save_path)                    


if __name__ == "__main__":
    main()

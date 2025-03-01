#Ajouter shebang pour déploiement au DIRO : !/usr/bin/python
import os
import re
import requests
from bs4 import BeautifulSoup

def fetch_content(url):
    """
    Récupère le contenu HTML d'une URL donnée.
    
    :param url: L'URL de la page à récupérer
    :return: Le contenu HTML sous forme de texte, ou None en cas d'erreur
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        return response.text
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de la page: {e}")
        return None

def extract_images(soup, regex_filter):
    """
    Extrait les images d'un objet BeautifulSoup.
    
    :param soup: L'objet BeautifulSoup analysant la page HTML
    :param regex_filter: Une expression régulière pour filtrer les images (facultatif)
    :return: Une liste de tuples contenant le chemin de l'image et son attribut alt
    """
    images = []
    for img in soup.find_all("img"):  # Recherche toutes les balises <img>
        src = img.get("src")[2:]  # Supprime le ./ du chemin de l'URL
        alt = img.get("alt", "")  # Récupère le texte alternatif si présent
        if src:
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
            src = source.get("src")[2:]  # Supprime le ./ du chemin de l'URL
            if src:
                if not regex_filter or re.search(regex_filter, src):
                    videos.append(src)  # Ajoute la vidéo à la liste
    return videos

def save_files(files, url, save_path):
    """
    Télécharge et enregistre les fichiers extraits (images ou vidéos).
    
    :param files: Liste des fichiers à télécharger
    :param url: URL de la page d'origine
    :param save_path: Dossier de sauvegarde des fichiers
    """
    os.makedirs(save_path, exist_ok=True)  # Crée le répertoire de destination si inexistant
    for file_url, _ in files:
        file_name = os.path.join(save_path, os.path.basename(file_url))  # Détermine le nom du fichier local
        file_url = url + file_url[1:] if file_url.startswith("./") else url + file_url  # Complète l'URL du fichier
        try:
            with requests.get(file_url, stream=True) as r:
                r.raise_for_status()  # Vérifie que le téléchargement a réussi
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):  # Écrit le fichier par morceaux
                        f.write(chunk)
        except requests.RequestException as e:
            print(f"Erreur lors du téléchargement de {file_url}: {e}")
            
def help():
    """
    Affiche le message d'aide pour l'utilisation du script.
    """
    print("Usage: extract [-r <regex>] [-i] [-v] [-p <path>] <url>\n")
    print("Options:")
    print("  -r <regex>  Filtrer les ressources par une expression régulière sur leur nom")
    print("  -i          Exclure les éléments <img> de la liste")
    print("  -v          Exclure les éléments <video> de la liste")
    print("  -p <path>   Copier les ressources img et/ou vidéo dans <path>")
    print("  -h          Afficher ce message d'aide et quitter\n")
    print("Auteurs: Yanis Boulogne - Karl-Antoine Plouffe")
    

def main():
    """
    Fonction principale du script. Analyse les arguments et exécute les actions appropriées.
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


if __name__ == "__main__":
    main()

import os
import re
import requests
from bs4 import BeautifulSoup

def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de la page: {e}")
        return None

def extract_images(soup, url, regex_filter):
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt", "")
        if src:
            if not regex_filter or re.search(regex_filter, src):
                images.append((src, alt))
    return images

def extract_videos(soup, url, regex_filter):
    videos = []
    for video in soup.find_all("video"):
        for source in video.find_all("source"):
            src = source.get("src")
            if src:
                if not regex_filter or re.search(regex_filter, src):
                    videos.append(src)
    return videos

def save_files(files, url, save_path):
    os.makedirs(save_path, exist_ok=True)
    for file_url in files:
        file_url = url + file_url[1:] if file_url.startswith("./") else url + file_url
        file_name = os.path.join(save_path, os.path.basename(file_url))
        try:
            with requests.get(file_url, stream=True) as r:
                r.raise_for_status()
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.RequestException as e:
            print(f"Erreur lors du téléchargement de {file_url}: {e}")

def main():
    import sys
    args = sys.argv[1:]
    if "-h" in args in args or len(args) == 0:
        print("Usage: extract [-r <regex>] [-i] [-v] [-p <path>] <url>")
        print("")
        print("Options:")
        print("  -r <regex>  Filtrer les ressources par une expression régulière sur leur nom")
        print("  -i          Exclure les éléments <img> de la liste")
        print("  -v          Exclure les éléments <video> de la liste")
        print("  -p <path>   Copier les ressources img et/ou vidéo dans <path>")
        print("  -h          Afficher ce message d'aide et quitter")
        print("")
        print("Auteurs: Yanis Boulogne - Karl-Antoine Plouffe")
        return
    
    url = None
    regex_filter = None
    save_path = None
    no_images = False
    no_videos = False
    
    i = 0
    while i < len(args):
        if args[i] == "-r" and i + 1 < len(args):
            regex_filter = args[i + 1]
            i += 1
        elif args[i] == "-p" and i + 1 < len(args):
            save_path = args[i + 1]
            i += 1
        elif args[i] == "-i":
            no_images = True
        elif args[i] == "-v":
            no_videos = True
        else:
            if url is None:
                url = args[i]
            else:
                print("Erreur: Une seule URL est autorisée.")
                return
        i += 1
    
    if not url:
        print("Erreur: Aucun paramètre fourni.")
        return
    
    page_content = fetch_content(url)
    if not page_content:
        return
    
    soup = BeautifulSoup(page_content, "html.parser")
    
    print(f"PATH: {save_path if save_path is not None else url}")
    
    if not no_images:
        images = extract_images(soup, url, regex_filter)
        for src, alt in images:
            print(f"IMAGE {src} \"{alt}\"")
        if save_path:
            save_files([src for src, _ in images], url, save_path)
    
    if not no_videos:
        videos = extract_videos(soup, url, regex_filter)
        for src in videos:
            print(f"VIDEO {src}")
        if save_path:
            save_files(videos, url, save_path)


if __name__ == "__main__":
    main()

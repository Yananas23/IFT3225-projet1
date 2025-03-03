#Ajouter shebang pour déploiement au DIRO : !/usr/bin/python
import sys
import re

def help():
    print("Usage: extract | genere >! fichier_sortie")
    print("Options:")
    print("  -h              Affiche ce message d'aide et les auteurs")
    print("fichier_sortie    Nom du fichier HTML généré (ex: mapage.html)")
    print("Auteurs: Yanis Boulogne - Karl-Antoine Plouffe")
    sys.exit(0)

def generer_html(images, videos):
    try:
        with open("template.html", "r", encoding="utf-8") as template_file:
            template = template_file.read()
    except FileNotFoundError:
        print("Erreur: Le fichier template.html est introuvable.")
        sys.exit(1)

    ressources_html = ""

    for src, alt in images:
        ressources_html += f"<tr><td>{src}</td><td>{alt}</td></tr>\n"

    for src in videos:
        ressources_html += f"<tr><td>{src}</td><td>Video</td></tr>\n"

    # Remplacement du contenu de <tbody> par les ressources
    template = re.sub(r'(<tbody>.*?</tbody>)', f"<tbody>{ressources_html}</tbody>", template, flags=re.S)

    return template


def main():
    args = sys.argv
    if "-h" in args or len(args) == 0:
        help()
        return

    images = []
    videos = []
    

    # Lecture de l'entrée standard
    for line in sys.stdin:
        line = line.strip()
        if line.startswith("IMAGE"):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                _, src, alt = parts
                images.append((src, alt.strip('"')))
        elif line.startswith("VIDEO"):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                _, src = parts
                videos.append(src)

    html_content = generer_html(images, videos)

    print(html_content)

if __name__ == "__main__":
    main()

"""Petit serveur local pour lancer l'application (Windows, macOS, Linux).

Utilisation :
    python serveur.py              → ouvre l'application dans ton navigateur
    python serveur.py --reseau     → accessible aussi depuis l'iPad sur le même Wi-Fi
    python serveur.py --port 8080  → choisir un autre port

Aucune installation n'est nécessaire : uniquement la bibliothèque standard de Python.
Arrêt : Ctrl + C dans la fenêtre du terminal.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socket
import sys
import webbrowser
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent

# Sous Windows, le registre peut annoncer de mauvais types de fichiers
# (ex. .js en text/plain), ce qui bloque les modules JavaScript.
# On impose donc les bons types ici.
TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".webmanifest": "application/manifest+json; charset=utf-8",
    ".py": "text/plain; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".wasm": "application/wasm",
    ".zip": "application/zip",
    ".whl": "application/zip",
    ".md": "text/plain; charset=utf-8",
}


class Gestionnaire(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, **TYPES}

    def end_headers(self):
        # Toujours servir la dernière version des fichiers de l'application.
        if "/vendor/" not in self.path:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, format, *args):  # noqa: A002 - signature imposée par http.server
        # Journal discret : seulement les erreurs.
        # (Une copie locale de Pyodide absente est normale : on ne l'affiche pas.)
        requete = str(args[0]) if args else ""
        if len(args) > 1 and str(args[1]).startswith(("4", "5")) and "favicon" not in requete \
                and "/vendor/" not in requete:
            sys.stderr.write(f"  [{args[1]}] {args[0]}\n")


def adresse_locale() -> str:
    """Adresse IP de l'ordinateur sur le réseau local (pour l'iPad)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def main() -> int:
    parser = argparse.ArgumentParser(description="Lance l'application Agent Python.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reseau", action="store_true", help="rendre l'application accessible aux autres appareils du Wi-Fi")
    parser.add_argument("--sans-navigateur", action="store_true", help="ne pas ouvrir le navigateur")
    options = parser.parse_args()

    hote = "0.0.0.0" if options.reseau else "127.0.0.1"
    gestionnaire = functools.partial(Gestionnaire, directory=str(DOSSIER))

    serveur = None
    for port in range(options.port, options.port + 20):
        try:
            serveur = http.server.ThreadingHTTPServer((hote, port), gestionnaire)
            break
        except OSError:
            continue
    if serveur is None:
        print("Impossible de trouver un port libre.")
        return 1

    port = serveur.server_address[1]
    url = f"http://localhost:{port}/"
    print("=" * 62)
    print("  AGENT PYTHON — centre de formation")
    print(f"  Application : {url}")
    if options.reseau:
        print(f"  Sur l'iPad (même Wi-Fi) : http://{adresse_locale()}:{port}/")
        print("  (le mode hors ligne complet de l'iPad nécessite https : voir README)")
    print("  Arrêter : Ctrl + C")
    print("=" * 62)
    if not options.sans_navigateur:
        webbrowser.open(url)
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté. À bientôt, agent.")
    finally:
        serveur.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

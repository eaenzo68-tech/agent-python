"""Télécharge une copie locale du moteur Python (Pyodide) dans vendor/pyodide/.

À lancer UNE fois, avec Internet :     python outils/telecharger_pyodide.py

Ensuite, l'application n'a plus jamais besoin d'Internet, même au tout premier
lancement (pratique pour une clé USB, ou pour l'héberger sur GitHub Pages).
Sans cette copie, Python est téléchargé au premier lancement puis gardé en cache.
"""

import sys
import urllib.request
from pathlib import Path

VERSION = "0.27.7"  # doit correspondre à worker/moteur_python.js
SOURCE = f"https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/"
FICHIERS = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]
DESTINATION = Path(__file__).resolve().parent.parent / "vendor" / "pyodide"


def main() -> int:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for nom in FICHIERS:
        cible = DESTINATION / nom
        print(f"Téléchargement de {nom}…", end=" ", flush=True)
        try:
            with urllib.request.urlopen(SOURCE + nom, timeout=120) as reponse:
                contenu = reponse.read()
        except OSError as erreur:
            print(f"ÉCHEC ({erreur})")
            print("Vérifie ta connexion Internet puis relance le script.")
            return 1
        cible.write_bytes(contenu)
        print(f"{len(contenu) / 1_000_000:.1f} Mo")
    print(f"\nCopie locale prête dans : {DESTINATION}")
    print("Relance l'application : Paramètres > Moteur Python indique « copie locale ».")
    return 0


if __name__ == "__main__":
    sys.exit(main())

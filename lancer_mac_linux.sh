#!/bin/sh
# Lance l'application sous macOS ou Linux :  sh lancer_mac_linux.sh
cd "$(dirname "$0")" || exit 1
exec python3 serveur.py "$@"

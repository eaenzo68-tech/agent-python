"""Vérifie les missions et génère les fichiers data/*.json.

Usage (depuis le dossier du projet) :

    python outils/construire_donnees.py

Vérifications pour chaque mission :
- tous les champs obligatoires sont présents ;
- il y a 3 indices et au moins 2 tests ;
- la SOLUTION réussit tous les tests ;
- le CODE DE DÉPART ne les réussit pas (sinon la mission serait déjà résolue).
"""

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "outils"))

from concepts_source import BADGES, CONCEPTS  # noqa: E402
from missions_source import MISSIONS  # noqa: E402

from core.test_engine import evaluer  # noqa: E402

CHAMPS_OBLIGATOIRES = ["id", "titre", "theme", "concepts", "niveau", "difficulte", "briefing", "objectif",
                       "enonce", "donnees", "resultat_attendu", "code_depart", "tests", "indices",
                       "solution", "explication", "bareme"]
THEMES = {"variables", "conditions", "boucles", "listes", "dictionnaires", "chaines", "fonctions", "exceptions"}


def verifier_mission(mission: dict, ids_concepts: set) -> list[str]:
    problemes = []
    nom = mission.get("id", "?")
    for champ in CHAMPS_OBLIGATOIRES:
        if champ not in mission:
            problemes.append(f"{nom} : champ manquant « {champ} »")
    if problemes:
        return problemes
    if len(mission["indices"]) != 3:
        problemes.append(f"{nom} : il faut exactement 3 indices")
    if len(mission["tests"]) < 2:
        problemes.append(f"{nom} : il faut au moins 2 tests")
    if mission["theme"] not in THEMES:
        problemes.append(f"{nom} : thème inconnu {mission['theme']}")
    for concept in mission["concepts"]:
        if concept not in ids_concepts:
            problemes.append(f"{nom} : concept inconnu {concept}")
    rapport = evaluer(mission, mission["solution"])
    if not rapport["reussi"]:
        echec = next(t for t in rapport["tests"] if not t["reussi"])
        problemes.append(f"{nom} : la solution échoue au test {echec['numero']} ({echec['message']})")
    if evaluer(mission, mission["code_depart"])["reussi"]:
        problemes.append(f"{nom} : le code de départ réussit déjà tous les tests")
    return problemes


def main() -> int:
    ids_concepts = {c["id"] for c in CONCEPTS}
    ids = [m["id"] for m in MISSIONS]
    problemes = [f"identifiant en double : {i}" for i in set(ids) if ids.count(i) > 1]
    for mission in MISSIONS:
        problemes += verifier_mission(mission, ids_concepts)

    if problemes:
        print("❌ Problèmes détectés :")
        for probleme in problemes:
            print("  -", probleme)
        return 1

    dossier = RACINE / "data"
    dossier.mkdir(exist_ok=True)
    missions = sorted(MISSIONS, key=lambda m: m["ordre"])
    (dossier / "missions.json").write_text(json.dumps(missions, ensure_ascii=False, indent=1), encoding="utf-8")
    (dossier / "concepts.json").write_text(json.dumps(CONCEPTS, ensure_ascii=False, indent=1), encoding="utf-8")
    (dossier / "badges.json").write_text(json.dumps(BADGES, ensure_ascii=False, indent=1), encoding="utf-8")
    par_theme = {}
    for mission in missions:
        par_theme[mission["theme"]] = par_theme.get(mission["theme"], 0) + 1
    print(f"✅ {len(missions)} missions vérifiées et écrites dans data/missions.json")
    print("   par thème :", ", ".join(f"{t} {n}" for t, n in sorted(par_theme.items())))
    print(f"✅ {len(CONCEPTS)} concepts, {len(BADGES)} badges")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Point d'entrée unique entre l'interface (JavaScript) et le moteur Python.

L'interface appelle toujours la même fonction :

    traiter(action, charge_json)  →  texte JSON

- action      : le nom du service demandé ("executer", "evaluer", ...) ;
- charge_json : les paramètres, sous forme de texte JSON.

Passer par du JSON (du texte) rend l'échange simple et sûr : aucune donnée
n'est jamais exécutée comme du code, et on peut tester ce module sans
navigateur (voir tests/test_core.py).
"""

from __future__ import annotations

import json
import sys
import traceback

from core.code_quality import analyser_qualite
from core.code_runner import (
    DELAI_PAR_DEFAUT,
    executer_programme,
    formater_erreur_console,
)
from core.error_explainer import expliquer_erreur
from core.mission_generator import analyser_notes, creer_mission_perso, generer_missions
from core.test_engine import evaluer

DELAI_MIN, DELAI_MAX = 1.0, 15.0


def _delai(charge: dict) -> float:
    try:
        valeur = float(charge.get("delai", DELAI_PAR_DEFAUT))
    except (TypeError, ValueError):
        valeur = DELAI_PAR_DEFAUT
    return max(DELAI_MIN, min(valeur, DELAI_MAX))


def action_executer(charge: dict) -> dict:
    """Bouton « Exécuter le code » : lance le programme et explique l'erreur éventuelle."""
    code = charge.get("code", "")
    resultat = executer_programme(code, charge.get("entrees") or [], _delai(charge))
    reponse = resultat.vers_dict()
    if resultat.erreur:
        reponse["console"] += ("\n" if reponse["console"] else "") + formater_erreur_console(resultat.erreur)
        reponse["diagnostic"] = expliquer_erreur(resultat.erreur, code)
    return reponse


def action_evaluer(charge: dict) -> dict:
    """Bouton « Envoyer la mission » : exécute tous les tests."""
    return evaluer(charge["mission"], charge.get("code", ""), _delai(charge),
                   bool(charge.get("reveler_donnees")))


def action_expliquer(charge: dict) -> dict:
    """Explique une erreur connue (ex. délai dépassé détecté côté navigateur)."""
    return expliquer_erreur(charge.get("erreur") or {}, charge.get("code", ""))


def action_qualite(charge: dict) -> dict:
    return analyser_qualite(charge.get("code", ""))


def action_generer(charge: dict) -> dict:
    missions = generer_missions(
        charge.get("concepts") or [],
        charge.get("nombre", 3),
        charge.get("difficulte", "facile"),
        charge.get("niveaux") or {},
        charge.get("graine"),
        bool(charge.get("mixte")),
    )
    return {"missions": missions}


def action_analyser_notes(charge: dict) -> dict:
    return {"concepts": analyser_notes(charge.get("texte", ""), charge.get("catalogue") or [])}


def action_creer_mission(charge: dict) -> dict:
    return creer_mission_perso(charge.get("formulaire") or {})


def action_info(_charge: dict) -> dict:
    return {"python": sys.version.split()[0], "plateforme": sys.platform}


ACTIONS = {
    "executer": action_executer,
    "evaluer": action_evaluer,
    "expliquer": action_expliquer,
    "qualite": action_qualite,
    "generer": action_generer,
    "analyser_notes": action_analyser_notes,
    "creer_mission": action_creer_mission,
    "info": action_info,
}


def traiter(action: str, charge_json: str) -> str:
    """Exécute l'action demandée et renvoie toujours un texte JSON (jamais d'exception)."""
    try:
        charge = json.loads(charge_json or "{}")
        fonction = ACTIONS.get(action)
        if fonction is None:
            return json.dumps({"erreur_interne": f"Action inconnue : {action}"})
        return json.dumps(fonction(charge), ensure_ascii=False, default=repr)
    except Exception as exc:  # noqa: BLE001 - l'interface doit toujours recevoir une réponse
        return json.dumps({
            "erreur_interne": f"{type(exc).__name__}: {exc}",
            "details": traceback.format_exc(limit=3),
        }, ensure_ascii=False)


def version_python() -> str:
    return sys.version.split()[0]

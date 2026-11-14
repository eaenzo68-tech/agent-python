"""Vérifie automatiquement une mission avec plusieurs tests.

Une mission contient une liste de tests. Quatre types existent :

- "appel"     : appelle une fonction de l'agent et compare la valeur renvoyée ;
                ex. {"type": "appel", "fonction": "doubler", "args": [4], "attendu": 8}
- "sortie"    : exécute tout le programme et compare ce qui est affiché ;
                ex. {"type": "sortie", "entrees": ["5"], "attendu": "Accès total\\n"}
- "variable"  : exécute le programme et vérifie la valeur d'une variable ;
                ex. {"type": "variable", "nom": "total", "attendu": 42}
- "structure" : vérifie que le code utilise (ou n'utilise pas) certains outils ;
                ex. {"type": "structure", "doit_utiliser": ["while"], "interdit": ["max"]}

Comme le format JSON ne connaît pas les tuples ni les ensembles, on les écrit
{"__tuple__": [1, 2]} ou {"__set__": [1, 2]}. Un dictionnaire dont les clés
ne sont pas des textes s'écrit {"__dict__": [[cle, valeur], ...]}.
"""

from __future__ import annotations

import ast
import copy

from core.code_quality import analyser_qualite
from core.code_runner import (
    DELAI_PAR_DEFAUT,
    ResultatExecution,
    appeler_fonction,
    executer_programme,
    formater_erreur_console,
    preparer_code,
)
from core.error_explainer import expliquer_erreur
from core.hint_engine import diagnostic_logique

ERREURS_DE_DEMARRAGE = {"SyntaxError", "IndentationError", "TabError"}


# ---------------------------------------------------------------------------
# Valeurs : décodage, affichage, comparaison
# ---------------------------------------------------------------------------

def decoder_valeur(valeur):
    """Transforme les écritures JSON spéciales en vrais objets Python."""
    if isinstance(valeur, list):
        return [decoder_valeur(v) for v in valeur]
    if isinstance(valeur, dict):
        if set(valeur) == {"__tuple__"}:
            return tuple(decoder_valeur(v) for v in valeur["__tuple__"])
        if set(valeur) == {"__set__"}:
            return {decoder_valeur(v) for v in valeur["__set__"]}
        if set(valeur) == {"__dict__"}:
            return {decoder_valeur(k): decoder_valeur(v) for k, v in valeur["__dict__"]}
        return {cle: decoder_valeur(v) for cle, v in valeur.items()}
    return valeur


def representer(valeur, limite: int = 300) -> str:
    """repr() raccourci pour l'affichage."""
    try:
        texte = repr(valeur)
    except Exception:  # noqa: BLE001 - un repr() défectueux ne doit pas tout bloquer
        texte = "<valeur impossible à afficher>"
    return texte if len(texte) <= limite else texte[: limite - 1] + "…"


def _est_nombre(valeur) -> bool:
    return isinstance(valeur, (int, float)) and not isinstance(valeur, bool)


def comparer_valeurs(obtenu, attendu, tolerance: float | None = None) -> tuple[bool, str | None]:
    """Compare deux valeurs et renvoie (identiques ?, nature de la différence)."""
    if isinstance(attendu, bool) or isinstance(obtenu, bool):
        if type(obtenu) is not type(attendu):
            return False, "type"
        return obtenu == attendu, None if obtenu == attendu else "valeur"

    if _est_nombre(obtenu) and _est_nombre(attendu):
        marge = tolerance if tolerance is not None else (1e-9 if isinstance(attendu, float) else 0)
        egal = abs(obtenu - attendu) <= marge
        return egal, None if egal else "valeur"

    if obtenu is None and attendu is not None:
        return False, "none"

    if type(obtenu) is not type(attendu):
        return False, "type"

    try:
        egal = obtenu == attendu
    except Exception:  # noqa: BLE001
        egal = False
    if egal:
        return True, None

    if isinstance(attendu, (list, tuple)):
        if len(obtenu) != len(attendu):
            return False, "longueur"
        if tolerance is not None and all(
            comparer_valeurs(o, a, tolerance)[0] for o, a in zip(obtenu, attendu)
        ):
            return True, None
        try:
            if sorted(obtenu, key=repr) == sorted(attendu, key=repr):
                return False, "ordre"
        except Exception:  # noqa: BLE001
            pass
        return False, "valeur"
    if isinstance(attendu, str):
        if obtenu.lower() == attendu.lower():
            return False, "casse"
        if " ".join(obtenu.split()) == " ".join(attendu.split()):
            return False, "espaces"
    return False, "valeur"


def normaliser_sortie(texte: str) -> list[str]:
    """Découpe une sortie en lignes, sans espaces inutiles en fin de ligne."""
    lignes = [ligne.rstrip() for ligne in texte.replace("\r\n", "\n").split("\n")]
    while lignes and lignes[-1] == "":
        lignes.pop()
    return lignes


# ---------------------------------------------------------------------------
# Tests de structure (le code utilise-t-il les bons outils ?)
# ---------------------------------------------------------------------------

_NOEUDS = {
    "for": ast.For, "while": ast.While, "if": ast.If, "return": ast.Return,
    "try": ast.Try, "def": ast.FunctionDef, "f-string": ast.JoinedStr,
    "dictionnaire": ast.Dict, "liste": ast.List,
}

_NOMS_LISIBLES = {
    "for": "une boucle for", "while": "une boucle while", "if": "une condition if",
    "return": "return", "try": "un bloc try / except", "def": "une fonction (def)",
    "f-string": "une f-string", "dictionnaire": "un dictionnaire", "liste": "une liste",
}


def _appels_utilises(arbre: ast.AST) -> set[str]:
    noms = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Call):
            if isinstance(noeud.func, ast.Name):
                noms.add(noeud.func.id)
            elif isinstance(noeud.func, ast.Attribute):
                noms.add(noeud.func.attr)
    return noms


def verifier_structure(code: str, test: dict) -> tuple[bool, str]:
    """Vérifie les consignes de structure d'une mission."""
    try:
        arbre = ast.parse(code)
    except SyntaxError:
        return False, "Le code contient une erreur de syntaxe."
    appels = _appels_utilises(arbre)
    for outil in test.get("doit_utiliser", []):
        if outil in _NOEUDS:
            present = any(isinstance(n, _NOEUDS[outil]) for n in ast.walk(arbre))
        else:
            present = outil in appels
        if not present:
            nom = _NOMS_LISIBLES.get(outil, f"{outil}()")
            return False, f"La mission demande d'utiliser {nom}."
    for outil in test.get("interdit", []):
        if outil in appels:
            return False, f"La mission interdit {outil}() : écris toi-même la logique avec une boucle."
    return True, "Consignes de structure respectées."


# ---------------------------------------------------------------------------
# Évaluation complète d'une mission
# ---------------------------------------------------------------------------

def _description_appel(test: dict, args: list) -> str:
    morceaux = [representer(a, 80) for a in args]
    morceaux += [f"{k}={representer(v, 80)}" for k, v in test.get("kwargs", {}).items()]
    return f"{test['fonction']}({', '.join(morceaux)})"


def _resultat_vide(numero: int, test: dict) -> dict:
    return {
        "numero": numero,
        "type": test["type"],
        "description": test.get("description", ""),
        "visible": test.get("visible", True),
        "reussi": False,
        "appel": "",
        "attendu": "",
        "obtenu": "",
        "sortie": "",
        "message": "",
        "nature": None,
        "erreur": None,
    }


def evaluer(mission: dict, code: str, delai: float = DELAI_PAR_DEFAUT,
            reveler_donnees: bool = False) -> dict:
    """Exécute tous les tests d'une mission et prépare le rapport."""
    code, avertissements = preparer_code(code)
    tests = mission.get("tests", [])
    executions: dict[tuple, ResultatExecution] = {}
    # Après une boucle infinie, les tests suivants reçoivent un délai très court :
    # inutile d'attendre plusieurs fois la même boucle.
    budget = {"delai": delai}

    def executer(entrees) -> ResultatExecution:
        cle = tuple(str(e) for e in (entrees or []))
        if cle not in executions:
            executions[cle] = executer_programme(code, list(cle), budget["delai"])
        return executions[cle]

    # 1. Première exécution du programme (définit les fonctions).
    entrees_initiales = next(
        (t.get("entrees", []) for t in tests if t["type"] in ("sortie", "variable")), []
    )
    initiale = executer(entrees_initiales)
    console = initiale.console
    if initiale.erreur:
        console += ("\n" if console else "") + formater_erreur_console(initiale.erreur)

    resultats = []
    if initiale.erreur and (initiale.erreur["type"] in ERREURS_DE_DEMARRAGE or not any(
        t["type"] in ("sortie", "variable") for t in tests
    )):
        # Le programme ne démarre pas (ou plante avant les tests de fonctions).
        diagnostic = expliquer_erreur(initiale.erreur, code)
        for numero, test in enumerate(tests, start=1):
            resultat = _resultat_vide(numero, test)
            resultat["message"] = "Non exécuté : le programme s'arrête sur une erreur."
            resultats.append(resultat)
        return _rapport(mission, code, resultats, diagnostic, console, avertissements,
                        [diagnostic["categorie"]])

    # 2. Chaque test, un par un.
    for numero, test in enumerate(tests, start=1):
        visible = test.get("visible", True) or reveler_donnees
        resultat = _resultat_vide(numero, test)
        if test["type"] == "appel":
            _tester_appel(test, resultat, initiale, code, budget["delai"], visible)
        elif test["type"] == "sortie":
            _tester_sortie(test, resultat, executer(test.get("entrees", [])), code, visible)
        elif test["type"] == "variable":
            _tester_variable(test, resultat, executer(test.get("entrees", [])), code, visible)
        elif test["type"] == "structure":
            reussi, message = verifier_structure(code, test)
            resultat["reussi"] = reussi
            resultat["message"] = message
            resultat["nature"] = None if reussi else "structure"
        if resultat["erreur"] and resultat["erreur"].get("categorie") == "boucle_infinie":
            budget["delai"] = min(delai, 0.5)
        resultats.append(resultat)

    # 3. Diagnostic du premier test échoué (pour le téléphone).
    diagnostic = None
    categories = []
    for resultat in resultats:
        if resultat["reussi"]:
            continue
        if resultat["erreur"]:
            fiche = resultat["erreur"]
        else:
            test = tests[resultat["numero"] - 1]
            fiche = diagnostic_logique(resultat, test, mission, code)
        categories.append(fiche["categorie"])
        if diagnostic is None:
            diagnostic = fiche
    return _rapport(mission, code, resultats, diagnostic, console, avertissements,
                    list(dict.fromkeys(categories)))


def _tester_appel(test, resultat, initiale, code, delai, visible):
    nom = test["fonction"]
    args = decoder_valeur(test.get("args", []))
    kwargs = decoder_valeur(test.get("kwargs", {}))
    attendu = decoder_valeur(test.get("attendu"))
    resultat["appel"] = _description_appel(test, args) if visible else f"{nom}(…)"
    resultat["attendu"] = representer(attendu) if visible else "(caché)"

    fonction = initiale.espace.get(nom)
    if not callable(fonction):
        resultat["nature"] = "fonction_absente"
        resultat["message"] = f"La fonction {nom}() est introuvable."
        return

    copie_args = copy.deepcopy(args)
    appel = appeler_fonction(initiale.espace, nom, copie_args, kwargs, code, delai)
    resultat["sortie"] = appel.sortie
    if not appel.ok:
        resultat["erreur"] = expliquer_erreur(appel.erreur, code)
        resultat["message"] = f"{appel.erreur['type']} : {appel.erreur['message']}"
        resultat["nature"] = "erreur"
        return

    resultat["obtenu"] = representer(appel.valeur) if visible else _type_lisible(appel.valeur)
    egal, nature = comparer_valeurs(appel.valeur, attendu, test.get("tolerance"))
    if egal and test.get("verifier_non_modifie") and copie_args != args:
        egal, nature = False, "modification"
    resultat["reussi"] = egal
    resultat["nature"] = nature
    resultat["valeur_obtenue"] = appel.valeur  # retiré avant l'envoi à l'interface
    resultat["valeur_attendue"] = attendu
    resultat["message"] = "Correct" if egal else "Résultat différent de celui attendu"


def _tester_sortie(test, resultat, execution, code, visible):
    attendu = test.get("attendu", "")
    resultat["appel"] = ("Entrées : " + ", ".join(test.get("entrees", []))) if test.get("entrees") else ""
    resultat["attendu"] = attendu if visible else "(caché)"
    resultat["obtenu"] = execution.sortie if visible else ""
    if execution.erreur:
        resultat["erreur"] = expliquer_erreur(execution.erreur, code)
        resultat["message"] = f"{execution.erreur['type']} : {execution.erreur['message']}"
        resultat["nature"] = "erreur"
        return
    lignes_obtenues = normaliser_sortie(execution.sortie)
    lignes_attendues = normaliser_sortie(attendu)
    resultat["reussi"] = lignes_obtenues == lignes_attendues
    resultat["nature"] = None if resultat["reussi"] else "sortie"
    resultat["lignes_obtenues"] = lignes_obtenues
    resultat["lignes_attendues"] = lignes_attendues
    resultat["message"] = "Correct" if resultat["reussi"] else "Affichage différent de celui attendu"


def _tester_variable(test, resultat, execution, code, visible):
    nom = test["nom"]
    attendu = decoder_valeur(test.get("attendu"))
    resultat["appel"] = f"variable {nom}"
    resultat["attendu"] = representer(attendu) if visible else "(caché)"
    if execution.erreur:
        resultat["erreur"] = expliquer_erreur(execution.erreur, code)
        resultat["message"] = f"{execution.erreur['type']} : {execution.erreur['message']}"
        resultat["nature"] = "erreur"
        return
    if nom not in execution.espace:
        resultat["nature"] = "variable_absente"
        resultat["message"] = f"La variable {nom} n'existe pas."
        return
    valeur = execution.espace[nom]
    resultat["obtenu"] = representer(valeur) if visible else _type_lisible(valeur)
    egal, nature = comparer_valeurs(valeur, attendu, test.get("tolerance"))
    resultat["reussi"] = egal
    resultat["nature"] = nature
    resultat["valeur_obtenue"] = valeur
    resultat["valeur_attendue"] = attendu
    resultat["message"] = "Correct" if egal else f"La variable {nom} n'a pas la bonne valeur"


def _type_lisible(valeur) -> str:
    return f"(valeur cachée de type {type(valeur).__name__})"


def _rapport(mission, code, resultats, diagnostic, console, avertissements, categories) -> dict:
    """Assemble le rapport final (uniquement des données simples, envoyables en JSON)."""
    for resultat in resultats:
        resultat.pop("valeur_obtenue", None)
        resultat.pop("valeur_attendue", None)
    nb_reussis = sum(1 for r in resultats if r["reussi"])
    reussi = bool(resultats) and nb_reussis == len(resultats)
    return {
        "reussi": reussi,
        "nb_reussis": nb_reussis,
        "nb_total": len(resultats),
        "tests": resultats,
        "diagnostic": None if reussi else diagnostic,
        "categories": [] if reussi else categories,
        "console": console,
        "avertissements": avertissements,
        "qualite": analyser_qualite(code, mission),
    }

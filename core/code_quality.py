"""Analyse simple de la qualité du code (règles inspirées de PEP 8).

Le but n'est PAS de sanctionner : un débutant reçoit au maximum trois
conseils, classés du plus utile au moins utile, et la note ne descend
jamais sous 40 pour un code analysable.

Vérifications :
- noms de variables (trop courts, peu parlants, camelCase, noms réservés) ;
- indentation (tabulations, multiples de 4) ;
- lisibilité (longueur des lignes, espaces autour de =, plusieurs instructions par ligne) ;
- répétitions de lignes identiques ;
- longueur des fonctions ;
- présence de commentaires utiles ;
- utilisation appropriée des structures Python (== True, range(len(...)), except nu…).

PEP 8 est le guide de style officiel de Python : https://peps.python.org/pep-0008/
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from collections import Counter

NOMS_COURTS_ACCEPTES = {"i", "j", "k", "n", "x", "y", "z", "_", "a", "b"}
NOMS_PEU_PARLANTS = {"toto", "tata", "truc", "machin", "bidule", "var", "variable",
                     "temp", "tmp", "data", "chose", "test", "foo", "bar", "lol"}
NOMS_RESERVES = {"list", "dict", "str", "int", "float", "sum", "max", "min", "input",
                 "print", "len", "type", "id", "set", "tuple", "range", "sorted",
                 "filter", "map", "open", "format", "round", "abs", "all", "any",
                 "next", "iter", "object", "bool", "zip", "file"}
LONGUEUR_LIGNE_MAX = 99
LONGUEUR_FONCTION_MAX = 25

# Points retirés selon la gravité : 1 = détail, 2 = à corriger, 3 = important
PENALITES = {1: 4, 2: 8, 3: 12}


def _remarque(code_regle, gravite, titre, detail, ligne=None) -> dict:
    return {"regle": code_regle, "gravite": gravite, "titre": titre, "detail": detail, "ligne": ligne}


# ---------------------------------------------------------------------------
# Règles
# ---------------------------------------------------------------------------

def _noms_crees(arbre: ast.AST) -> list[tuple[str, int, str]]:
    """Liste (nom, ligne, nature) de tout ce que l'agent nomme lui-même."""
    noms = []
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Name) and isinstance(noeud.ctx, ast.Store):
            noms.append((noeud.id, noeud.lineno, "variable"))
        elif isinstance(noeud, ast.FunctionDef):
            noms.append((noeud.name, noeud.lineno, "fonction"))
            for argument in noeud.args.args:
                noms.append((argument.arg, noeud.lineno, "paramètre"))
    return noms


def _regles_noms(arbre: ast.AST, variables_de_boucle: set[str]) -> list[dict]:
    remarques = []
    deja_vus = set()
    for nom, ligne, nature in _noms_crees(arbre):
        if nom in deja_vus:
            continue
        deja_vus.add(nom)
        if nom in NOMS_RESERVES:
            remarques.append(_remarque(
                "nom_reserve", 2, f"« {nom} » est déjà le nom d'une fonction Python",
                f"En nommant une {nature} « {nom} », tu caches la fonction intégrée {nom}(). "
                "Choisis un nom qui décrit le contenu, par exemple « resultats » ou « total_points ».",
                ligne))
        elif re.search(r"[a-z][A-Z]", nom):
            propose = re.sub(r"([a-z])([A-Z])", r"\1_\2", nom).lower()
            remarques.append(_remarque(
                "camel_case", 1, f"« {nom} » : utilise le style snake_case",
                "En Python, on écrit les noms en minuscules séparées par des tirets bas : "
                f"« {propose} ».", ligne))
        elif nom.lower() in NOMS_PEU_PARLANTS:
            remarques.append(_remarque(
                "nom_vague", 1, f"« {nom} » ne dit pas ce que contient la {nature}",
                "Un bon nom explique le contenu : « suspects_filtres », « total_points »…", ligne))
        elif (len(nom) == 1 and nom not in NOMS_COURTS_ACCEPTES
              and nom not in variables_de_boucle):
            remarques.append(_remarque(
                "nom_court", 1, f"« {nom} » est un nom très court",
                "Un nom d'une lettre est difficile à comprendre en relisant. "
                "Préfère un mot qui décrit la valeur (« age », « message »…).", ligne))
    return remarques


def _variables_de_boucle(arbre: ast.AST) -> set[str]:
    noms = set()
    for noeud in ast.walk(arbre):
        cibles = []
        if isinstance(noeud, ast.For):
            cibles.append(noeud.target)
        elif isinstance(noeud, ast.comprehension):
            cibles.append(noeud.target)
        for cible in cibles:
            for sous in ast.walk(cible):
                if isinstance(sous, ast.Name):
                    noms.add(sous.id)
    return noms


def _regles_lignes(code: str) -> list[dict]:
    remarques = []
    lignes = code.split("\n")
    tab_signalee = indent_signalee = longue_signalee = False
    for numero, ligne in enumerate(lignes, start=1):
        debut = ligne[: len(ligne) - len(ligne.lstrip())]
        if "\t" in debut and not tab_signalee:
            tab_signalee = True
            remarques.append(_remarque(
                "tabulation", 2, "Indentation avec des tabulations",
                "PEP 8 recommande 4 espaces par niveau d'indentation, sans tabulations.", numero))
        elif ligne.strip() and len(debut) % 4 != 0 and not indent_signalee:
            precedente = lignes[numero - 2].rstrip() if numero > 1 else ""
            # Une ligne qui continue une parenthèse ouverte peut être alignée librement.
            if not precedente.endswith((",", "(", "[", "{", "\\")):
                indent_signalee = True
                remarques.append(_remarque(
                    "indentation_4", 1, "Indentation irrégulière",
                    f"La ligne {numero} est décalée de {len(debut)} espaces. "
                    "Utilise des multiples de 4 (4, 8, 12…).", numero))
        if len(ligne) > LONGUEUR_LIGNE_MAX and not longue_signalee:
            longue_signalee = True
            remarques.append(_remarque(
                "ligne_longue", 1, "Ligne trop longue",
                f"La ligne {numero} fait {len(ligne)} caractères. Au-delà de ~80, "
                "le code devient difficile à lire : découpe-la ou crée une variable intermédiaire.", numero))
    return remarques


def _regles_espaces(code: str) -> list[dict]:
    """Espaces autour de = et après les virgules (au niveau 0 des parenthèses)."""
    remarques = []
    try:
        jetons = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return remarques
    profondeur = 0
    egal_signale = virgule_signalee = False
    for indice, jeton in enumerate(jetons):
        if jeton.type != tokenize.OP:
            continue
        if jeton.string in "([{":
            profondeur += 1
        elif jeton.string in ")]}":
            profondeur = max(0, profondeur - 1)
        elif jeton.string in ("=", "+=", "-=", "*=", "/=", "==", "!=", "<=", ">=") and \
                profondeur == 0 and not egal_signale:
            avant, apres = jetons[indice - 1], jetons[indice + 1]
            if avant.end == jeton.start or apres.start == jeton.end:
                egal_signale = True
                remarques.append(_remarque(
                    "espaces_operateur", 1, f"Ajoute des espaces autour de « {jeton.string} »",
                    f"Ligne {jeton.start[0]} : écris « total = 5 » plutôt que « total=5 ». "
                    "C'est plus aéré et plus lisible.", jeton.start[0]))
        elif jeton.string == "," and not virgule_signalee:
            apres = jetons[indice + 1]
            if apres.start == jeton.end and apres.type not in (tokenize.NL, tokenize.NEWLINE) \
                    and apres.string not in ")]}":
                virgule_signalee = True
                remarques.append(_remarque(
                    "espace_virgule", 1, "Ajoute un espace après les virgules",
                    f"Ligne {jeton.start[0]} : écris « f(a, b) » plutôt que « f(a,b) ».",
                    jeton.start[0]))
        elif jeton.string == ";":
            if not any(r["regle"] == "point_virgule" for r in remarques):
                remarques.append(_remarque(
                    "point_virgule", 1, "Une instruction par ligne",
                    f"Ligne {jeton.start[0]} : en Python, on évite « ; ». Écris chaque instruction sur sa propre ligne.",
                    jeton.start[0]))
    return remarques


def _regles_repetitions(code: str) -> list[dict]:
    lignes = [ligne.strip() for ligne in code.split("\n")]
    candidates = [ligne for ligne in lignes
                  if len(ligne) > 8 and not ligne.startswith(("#", "else", "return", "pass", "break"))]
    for ligne, nombre in Counter(candidates).most_common(1):
        if nombre >= 3:
            numero = lignes.index(ligne) + 1
            return [_remarque(
                "repetition", 2, "Code répété",
                f"La ligne « {ligne[:40]} » apparaît {nombre} fois. "
                "Quand on copie-colle, une boucle ou une fonction est souvent plus propre.", numero)]
    return []


def _regles_structures(arbre: ast.AST) -> list[dict]:
    remarques = []
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.FunctionDef):
            longueur = (noeud.end_lineno or noeud.lineno) - noeud.lineno + 1
            if longueur > LONGUEUR_FONCTION_MAX:
                remarques.append(_remarque(
                    "fonction_longue", 1, f"La fonction {noeud.name}() est longue ({longueur} lignes)",
                    "Une fonction courte fait une seule chose. Découpe-la en petites fonctions.",
                    noeud.lineno))
            remarques += _regle_if_return_booleen(noeud)
            remarques += _regle_code_mort(noeud)
        elif isinstance(noeud, ast.Compare):
            for comparateur, droite in zip(noeud.ops, noeud.comparators):
                if isinstance(comparateur, (ast.Eq, ast.NotEq)) and isinstance(droite, ast.Constant):
                    if droite.value is True or droite.value is False:
                        remarques.append(_remarque(
                            "compare_booleen", 1, f"Inutile d'écrire « == {droite.value} »",
                            "Écris simplement « if est_actif: » ou « if not est_actif: ».",
                            noeud.lineno))
                    elif droite.value is None:
                        remarques.append(_remarque(
                            "compare_none", 1, "Utilise « is None »",
                            "Pour tester None, PEP 8 recommande « if valeur is None: ».", noeud.lineno))
        elif isinstance(noeud, ast.ExceptHandler) and noeud.type is None:
            remarques.append(_remarque(
                "except_nu", 2, "« except: » attrape toutes les erreurs",
                "Précise l'erreur attendue (except ValueError:) pour ne pas cacher de vrais bugs.",
                noeud.lineno))
        elif isinstance(noeud, ast.Global):
            remarques.append(_remarque(
                "global", 2, "Évite « global »",
                "Passe plutôt les valeurs en paramètres et récupère le résultat avec return.",
                noeud.lineno))
        elif isinstance(noeud, ast.For):
            remarque = _regle_range_len(noeud)
            if remarque:
                remarques.append(remarque)
    return remarques


def _regle_range_len(boucle: ast.For) -> dict | None:
    """for i in range(len(liste)) alors que seul liste[i] est utilisé."""
    iterable = boucle.iter
    if not (isinstance(iterable, ast.Call) and isinstance(iterable.func, ast.Name)
            and iterable.func.id == "range" and len(iterable.args) == 1):
        return None
    interieur = iterable.args[0]
    if not (isinstance(interieur, ast.Call) and isinstance(interieur.func, ast.Name)
            and interieur.func.id == "len" and interieur.args
            and isinstance(interieur.args[0], ast.Name) and isinstance(boucle.target, ast.Name)):
        return None
    nom_liste, nom_indice = interieur.args[0].id, boucle.target.id
    for noeud in ast.walk(ast.Module(body=boucle.body, type_ignores=[])):
        if isinstance(noeud, ast.Name) and noeud.id == nom_indice:
            parent_ok = False
            for sous in ast.walk(ast.Module(body=boucle.body, type_ignores=[])):
                if (isinstance(sous, ast.Subscript) and isinstance(sous.value, ast.Name)
                        and sous.value.id == nom_liste and sous.slice is noeud):
                    parent_ok = True
            if not parent_ok:
                return None  # l'indice sert à autre chose : la boucle est justifiée
    return _remarque(
        "range_len", 1, "Parcours directement les éléments",
        f"Tu utilises seulement {nom_liste}[{nom_indice}] : écris plutôt "
        f"« for element in {nom_liste}: ». C'est plus court et plus clair.", boucle.lineno)


def _regle_if_return_booleen(fonction: ast.FunctionDef) -> list[dict]:
    for noeud in ast.walk(fonction):
        if (isinstance(noeud, ast.If) and len(noeud.body) == 1 and len(noeud.orelse) == 1
                and isinstance(noeud.body[0], ast.Return) and isinstance(noeud.orelse[0], ast.Return)):
            gauche, droite = noeud.body[0].value, noeud.orelse[0].value
            if (isinstance(gauche, ast.Constant) and isinstance(droite, ast.Constant)
                    and {gauche.value, droite.value} == {True, False}):
                return [_remarque(
                    "return_condition", 1, "Tu peux renvoyer la condition directement",
                    "« if condition: return True else: return False » s'écrit simplement "
                    "« return condition ». (Conseil avancé, pas obligatoire.)", noeud.lineno)]
    return []


def _regle_code_mort(fonction: ast.FunctionDef) -> list[dict]:
    for bloc in ast.walk(fonction):
        corps = getattr(bloc, "body", None)
        if not isinstance(corps, list):
            continue
        for position, instruction in enumerate(corps[:-1]):
            if isinstance(instruction, (ast.Return, ast.Break, ast.Continue)):
                suivante = corps[position + 1]
                return [_remarque(
                    "code_mort", 2, "Du code ne sera jamais exécuté",
                    f"La ligne {suivante.lineno} vient après un {type(instruction).__name__.lower()} : "
                    "Python n'y arrivera jamais.", suivante.lineno)]
    return []


def _regle_commentaires(code: str, arbre: ast.AST) -> list[dict]:
    lignes_utiles = [ligne for ligne in code.split("\n") if ligne.strip()]
    a_commentaire = any(ligne.strip().startswith("#") or " # " in ligne for ligne in lignes_utiles)
    a_docstring = any(
        isinstance(n, ast.FunctionDef) and ast.get_docstring(n) for n in ast.walk(arbre)
    )
    if len(lignes_utiles) >= 12 and not (a_commentaire or a_docstring):
        return [_remarque(
            "commentaires", 1, "Ajoute un commentaire ou une docstring",
            "Pour un programme de plus de 10 lignes, une courte phrase qui explique "
            "le rôle d'une fonction (docstring) aide beaucoup à la relecture.")]
    return []


# ---------------------------------------------------------------------------
# Points forts (pour encourager)
# ---------------------------------------------------------------------------

def _points_forts(code: str, arbre: ast.AST, remarques: list[dict]) -> list[str]:
    regles = {r["regle"] for r in remarques}
    forts = []
    if not regles & {"nom_reserve", "camel_case", "nom_vague", "nom_court"}:
        forts.append("Noms clairs et bien écrits")
    if not regles & {"tabulation", "indentation_4"}:
        forts.append("Indentation propre (4 espaces)")
    if any(isinstance(n, ast.FunctionDef) and ast.get_docstring(n) for n in ast.walk(arbre)):
        forts.append("Docstring présente : bravo !")
    elif any(ligne.strip().startswith("#") for ligne in code.split("\n")):
        forts.append("Commentaires présents")
    if "repetition" not in regles and "fonction_longue" not in regles:
        forts.append("Pas de répétition inutile")
    return forts[:3]


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def analyser_qualite(code: str, mission: dict | None = None) -> dict:
    """Analyse le code et renvoie une note, au maximum 3 conseils et des points forts."""
    try:
        arbre = ast.parse(code)
    except SyntaxError:
        return {"analysable": False, "score": 0, "niveau": "Non analysable",
                "conseils": [], "points_forts": [], "nb_remarques": 0}

    remarques = []
    remarques += _regle_commentaires(code, arbre)
    remarques += _regles_noms(arbre, _variables_de_boucle(arbre))
    remarques += _regles_lignes(code)
    remarques += _regles_espaces(code)
    remarques += _regles_repetitions(code)
    remarques += _regles_structures(arbre)

    # Une même règle ne compte qu'une fois (on ne punit pas deux fois la même habitude).
    uniques = {}
    for remarque in remarques:
        uniques.setdefault(remarque["regle"], remarque)
    remarques = list(uniques.values())

    penalite = sum(PENALITES[r["gravite"]] for r in remarques)
    score = max(40, 100 - penalite)
    if score >= 85:
        niveau = "Excellent"
    elif score >= 70:
        niveau = "Bon"
    else:
        niveau = "À améliorer"

    remarques.sort(key=lambda r: (-r["gravite"], r["ligne"] or 0))
    return {
        "analysable": True,
        "score": score,
        "niveau": niveau,
        "conseils": remarques[:3],
        "points_forts": _points_forts(code, arbre, remarques),
        "nb_remarques": len(remarques),
    }

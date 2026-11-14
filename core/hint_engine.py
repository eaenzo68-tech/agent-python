"""Indices ciblés pour les erreurs de logique.

Quand le programme fonctionne mais donne un mauvais résultat, Python ne
signale aucune erreur. Ce module compare alors le résultat obtenu au
résultat attendu pour proposer une piste précise, SANS donner la solution.

Exemple : « Ton programme renvoie 4 éléments alors que la mission en attend 3.
Vérifie la condition utilisée pour sélectionner les suspects. »
"""

from __future__ import annotations

import ast

from core.error_explainer import extrait_code


def _fiche(categorie, nom_categorie, concept, titre, description, pourquoi,
           question, rappel, exemple, indice, extrait=None) -> dict:
    return {
        "categorie": categorie,
        "nom_categorie": nom_categorie,
        "concept": concept,
        "titre": titre,
        "description": description,
        "pourquoi": pourquoi,
        "question": question,
        "rappel": rappel,
        "exemple": exemple,
        "indice": indice,
        "type": "Logique",
        "message_python": "",
        "ligne": None,
        "extrait": extrait or [],
    }


# ---------------------------------------------------------------------------
# Analyse du code de la fonction
# ---------------------------------------------------------------------------

def _trouver_fonction(code: str, nom: str) -> ast.FunctionDef | None:
    try:
        arbre = ast.parse(code)
    except SyntaxError:
        return None
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.FunctionDef) and noeud.name == nom:
            return noeud
    return None


def fonction_incomplete(fonction: ast.FunctionDef | None) -> bool:
    """Vrai si le corps de la fonction ne contient que pass, ... ou une docstring."""
    if fonction is None:
        return False
    for instruction in fonction.body:
        if isinstance(instruction, ast.Pass):
            continue
        if isinstance(instruction, ast.Expr) and isinstance(instruction.value, ast.Constant):
            continue  # docstring ou ...
        return False
    return True


def _premiere_ligne(fonction: ast.FunctionDef | None, types) -> int | None:
    if fonction is None:
        return None
    lignes = [n.lineno for n in ast.walk(fonction) if isinstance(n, types)]
    return min(lignes) if lignes else None


def _contient(fonction: ast.FunctionDef | None, types) -> bool:
    return fonction is not None and any(isinstance(n, types) for n in ast.walk(fonction))


def _appelle_print(fonction: ast.FunctionDef | None) -> int | None:
    if fonction is None:
        return None
    for noeud in ast.walk(fonction):
        if (isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Name)
                and noeud.func.id == "print"):
            return noeud.lineno
    return None


# ---------------------------------------------------------------------------
# Diagnostic principal
# ---------------------------------------------------------------------------

def diagnostic_logique(resultat: dict, test: dict, mission: dict, code: str) -> dict:
    """Construit une fiche diagnostic pour un test échoué sans erreur Python."""
    nature = resultat.get("nature")
    elements = mission.get("elements", "éléments")
    visible = resultat.get("attendu") != "(caché)"
    reference_test = (f"le test « {resultat['description']} »" if resultat.get("description")
                      else f"le test n°{resultat['numero']}")

    if test["type"] == "structure":
        return _fiche(
            "structure", "Consigne non respectée", (mission.get("concepts") or ["fonctions"])[0],
            "Le résultat compte, mais la méthode aussi",
            resultat["message"],
            "Cette mission entraîne un outil précis de Python. Le but est d'apprendre à l'utiliser.",
            "Relis l'énoncé : quel outil la mission te demande-t-elle d'utiliser ?",
            "Les consignes de structure t'aident à pratiquer le bon concept.",
            "",
            "Réécris ta solution en respectant la consigne indiquée.",
        )

    if test["type"] == "variable" and nature == "variable_absente":
        return _fiche(
            "variable_absente", "Variable manquante", "variables",
            f"La variable {test['nom']} n'existe pas",
            f"La mission vérifie une variable appelée « {test['nom']} », mais ton programme ne la crée pas.",
            "Le nom doit être écrit exactement comme dans l'énoncé (minuscules, tirets bas).",
            f"As-tu bien écrit « {test['nom']} = … » quelque part dans ton programme ?",
            "nom_variable = valeur",
            'code_secret = 4096\nprint(code_secret)',
            f"Crée la variable {test['nom']} avec exactement ce nom.",
        )

    if test["type"] == "sortie":
        return _diagnostic_sortie(resultat, reference_test, visible)

    nom = test.get("fonction") or ""
    fonction = _trouver_fonction(code, nom)

    if nature == "fonction_absente":
        return _fiche(
            "fonction_absente", "Fonction introuvable", "fonctions",
            f"La fonction {nom}() est introuvable",
            f"La mission appelle {nom}(), mais ton code ne définit pas de fonction avec ce nom.",
            "Le nom doit être identique à celui de l'énoncé, sinon les tests ne la trouvent pas.",
            f"As-tu écrit « def {nom}(…): » exactement avec ce nom ?",
            "def nom_de_la_fonction(parametres):\n    ...\n    return resultat",
            "def saluer(nom):\n    return \"Bonjour \" + nom",
            f"Vérifie l'orthographe du nom après def : il doit s'appeler {nom}.",
        )

    if fonction_incomplete(fonction):
        return _fiche(
            "fonction_incomplete", "Fonction incomplète", "fonctions",
            "Ta fonction est encore vide",
            f"La fonction {nom}() ne contient que « pass » ou « ... » : elle ne fait encore rien.",
            "pass est un emplacement réservé : il dit à Python « rien à faire ici pour l'instant ».",
            "Quelles étapes faut-il enchaîner pour obtenir le résultat demandé ?",
            "Avant de coder, écris les étapes en français sous forme de commentaires.",
            "def compter_positifs(nombres):\n    # 1. créer un compteur\n    # 2. parcourir les nombres\n    # 3. renvoyer le compteur\n    ...",
            "Remplace pass par ton code, étape par étape.",
            extrait_code(code, fonction.lineno, 2) if fonction else None,
        )

    obtenu = resultat.get("valeur_obtenue")
    attendu = resultat.get("valeur_attendue")

    if nature == "none":
        ligne_print = _appelle_print(fonction)
        if ligne_print or resultat.get("sortie"):
            return _fiche(
                "print_return", "print() au lieu de return", "print-return",
                "Ta fonction affiche le résultat au lieu de le renvoyer",
                f"{nom}() a affiché quelque chose avec print(), mais a renvoyé None.",
                "print() montre une valeur à l'écran, mais elle est ensuite perdue. "
                "return renvoie la valeur au programme qui a appelé la fonction : on peut la réutiliser.",
                "Le programme qui appelle ta fonction peut-il récupérer ce que tu affiches avec print() ?",
                "print(x)  → affiche, renvoie None\nreturn x  → renvoie x (sans rien afficher)",
                "def carre(n):\n    return n * n\n\nresultat = carre(4)   # resultat vaut 16",
                "Remplace le print(...) final de ta fonction par return ...",
                extrait_code(code, ligne_print, 1) if ligne_print else None,
            )
        a_un_return = _contient(fonction, ast.Return)
        return _fiche(
            "retour_none", "Fonction sans résultat (None)", "print-return",
            "Ta fonction ne renvoie rien (None)",
            f"{nom}() a renvoyé None pour {reference_test}.",
            ("Ton return se trouve peut-être dans un if qui n'est pas toujours exécuté, "
             "ou à l'intérieur de la boucle." if a_un_return
             else "Une fonction sans return renvoie automatiquement None."),
            "Que doit renvoyer ta fonction dans TOUS les cas, même quand aucune condition n'est vraie ?",
            "Chaque chemin possible dans la fonction doit se terminer par un return.",
            "def signe(n):\n    if n > 0:\n        return \"positif\"\n    return \"négatif ou nul\"   # cas restant",
            "Vérifie que ta fonction se termine par return, et qu'il est au bon niveau d'indentation.",
            extrait_code(code, fonction.lineno, 0) if fonction else None,
        )

    if nature == "modification":
        return _fiche(
            "modification_parametre", "Paramètre modifié", "listes",
            "Ta fonction modifie la liste qu'elle reçoit",
            "Le résultat est bon, mais la liste donnée en paramètre a été changée.",
            "Une liste passée à une fonction n'est pas copiée : la modifier dans la fonction "
            "modifie aussi l'originale (ex. avec sort(), remove(), pop()).",
            "Comment travailler sur une copie plutôt que sur l'original ?",
            "sorted(liste) crée une nouvelle liste ; liste.sort() modifie l'originale.",
            "notes = [12, 8, 15]\ntriees = sorted(notes)   # notes reste [12, 8, 15]",
            "Travaille sur une copie (liste.copy(), sorted(...), ou une nouvelle liste).",
        )

    if nature == "type":
        type_obtenu, type_attendu = type(obtenu).__name__, type(attendu).__name__
        return _fiche(
            "type_retour", "Mauvais type de résultat", "types",
            "Le résultat n'a pas le bon type",
            f"Pour {reference_test}, ta fonction renvoie une valeur de type {type_obtenu}, "
            f"alors que la mission attend le type {type_attendu}.",
            "Pour Python, 5 (int), \"5\" (str), [5] (list) et (5,) (tuple) sont des valeurs différentes.",
            f"À quel moment ta valeur devient-elle un {type_obtenu} ?",
            "int(), float(), str(), list(), tuple() convertissent une valeur.",
            "position = (3, 4)      # tuple\nliste = [3, 4]         # liste",
            f"Assure-toi de renvoyer un {type_attendu}.",
            _extrait_return(code, fonction),
        )

    return _diagnostic_valeur(nature, obtenu, attendu, fonction, code, elements,
                              reference_test, visible, mission)


def _extrait_return(code, fonction):
    ligne = _premiere_ligne(fonction, ast.Return)
    return extrait_code(code, ligne, 1) if ligne else None


def _return_dans_boucle(fonction: ast.FunctionDef | None) -> int | None:
    """Ligne d'un return placé à l'intérieur d'une boucle (erreur très fréquente)."""
    if fonction is None:
        return None
    for boucle in ast.walk(fonction):
        if isinstance(boucle, (ast.For, ast.While)):
            for noeud in ast.walk(boucle):
                if isinstance(noeud, ast.Return):
                    return noeud.lineno
    return None


def _diagnostic_valeur(nature, obtenu, attendu, fonction, code, elements,
                       reference_test, visible, mission) -> dict:
    """Mauvaise valeur retournée : on cherche la piste la plus utile."""
    a_condition = _contient(fonction, ast.If)
    a_boucle = _contient(fonction, (ast.For, ast.While))
    ligne_if = _premiere_ligne(fonction, ast.If)
    ligne_boucle = _premiere_ligne(fonction, (ast.For, ast.While))
    concept = (mission.get("concepts") or ["fonctions"])[0]

    description = f"Pour {reference_test}, le résultat n'est pas celui attendu."
    indice = "Teste ta fonction à la main avec l'exemple de l'énoncé, ligne par ligne."
    question = "Si tu exécutes ta fonction « à la main » sur l'exemple, qu'obtiens-tu à chaque étape ?"
    extrait = None

    ligne_return_boucle = _return_dans_boucle(fonction)
    if nature == "longueur":
        mot = elements if len(obtenu) > 1 else "élément"
        description = (f"Ton programme renvoie {len(obtenu)} {mot} alors que la mission "
                       f"en attend {len(attendu)} ({reference_test}).")
        if ligne_return_boucle and len(obtenu) < len(attendu):
            indice = ("Ton return est À L'INTÉRIEUR de la boucle : la fonction s'arrête dès le premier "
                      "passage. Quel niveau d'indentation devrait-il avoir ?")
            question = "Combien de tours de boucle sont réellement effectués avant le return ?"
            extrait = extrait_code(code, ligne_return_boucle, 2)
        elif a_condition:
            indice = f"Vérifie la condition utilisée pour sélectionner les {elements}."
            question = "Ta condition laisse-t-elle passer trop (ou pas assez) d'éléments ? Pense à < ou <=."
            extrait = extrait_code(code, ligne_if, 1)
        else:
            indice = "Vérifie quand tu ajoutes un élément au résultat (append) et combien de tours fait ta boucle."
            extrait = extrait_code(code, ligne_boucle, 1) if ligne_boucle else None
    elif nature == "ordre":
        description = f"Ton résultat contient les bons {elements}, mais pas dans le bon ordre ({reference_test})."
        indice = "Relis l'énoncé : dans quel ordre les éléments doivent-ils apparaître ?"
        question = "Ton code trie-t-il ou inverse-t-il quelque chose qu'il ne devrait pas ?"
    elif nature == "casse":
        description = f"Presque ! Ton texte est correct, seules les majuscules/minuscules diffèrent ({reference_test})."
        indice = "Regarde les méthodes upper(), lower(), capitalize() ou title()."
        question = "Quelles lettres doivent être en majuscules dans le résultat attendu ?"
    elif nature == "espaces":
        description = f"Presque ! Ton texte est correct, seuls les espaces diffèrent ({reference_test})."
        indice = "Compare les espaces caractère par caractère (début, fin, entre les mots)."
        question = "Y a-t-il un espace en trop ou en moins quelque part ?"
    elif isinstance(obtenu, (int, float)) and isinstance(attendu, (int, float)) and \
            not isinstance(obtenu, bool):
        ecart = obtenu - attendu
        if visible:
            description = f"Ton résultat est {obtenu!r} alors que la mission attend {attendu!r} ({reference_test})."
        if abs(ecart) == 1:
            indice = ("Il y a un écart de 1 : vérifie les bornes de range(), ou la différence entre < et <=.")
            question = "Ta boucle fait-elle un tour de trop ou un tour de moins ?"
            extrait = extrait_code(code, ligne_boucle or ligne_if, 1) if (ligne_boucle or ligne_if) else None
        elif attendu and obtenu and isinstance(attendu, (int, float)) and obtenu == attendu * 2:
            indice = "Ton résultat est exactement le double : compterais-tu certains éléments deux fois ?"
        elif obtenu == 0 and a_boucle:
            indice = "Ton résultat vaut 0 : la variable est-elle bien mise à jour DANS la boucle ?"
            extrait = extrait_code(code, ligne_boucle, 1)
        else:
            indice = "Affiche les valeurs intermédiaires avec print() pour voir où le calcul diverge."
    elif isinstance(attendu, bool):
        description = f"Ta fonction renvoie {obtenu!r} au lieu de {attendu!r} ({reference_test})."
        indice = "Vérifie chaque partie de ta condition (and / or, <, <=, ==)."
        question = "Dans ce cas précis, chaque partie de ta condition est-elle vraie ou fausse ?"
        extrait = extrait_code(code, ligne_if, 1) if ligne_if else None
    elif isinstance(attendu, dict) and isinstance(obtenu, dict):
        manquantes = [k for k in attendu if k not in obtenu]
        en_trop = [k for k in obtenu if k not in attendu]
        if manquantes:
            description = f"Il manque {len(manquantes)} clé(s) dans ton dictionnaire ({reference_test})."
            indice = "Vérifie que tu ajoutes une entrée pour chaque élément parcouru."
        elif en_trop:
            description = f"Ton dictionnaire contient {len(en_trop)} clé(s) en trop ({reference_test})."
            indice = "Vérifie la condition qui décide d'ajouter une clé."
        else:
            description = f"Les clés sont bonnes, mais certaines valeurs sont fausses ({reference_test})."
            indice = "Vérifie comment tu mets à jour la valeur associée à chaque clé (+= 1, append…)."
    elif visible:
        description = f"Ta fonction renvoie {obtenu!r} au lieu de {attendu!r} ({reference_test})."

    return _fiche(
        "logique_valeur", "Mauvaise valeur retournée", concept,
        "Le programme fonctionne, mais le résultat est faux",
        description,
        "Aucune erreur Python ici : c'est une erreur de LOGIQUE. "
        "Le programme fait exactement ce que tu as écrit… mais pas encore ce que la mission demande.",
        question,
        "Méthode d'agent : 1) prends un petit exemple ; 2) déroule ton code à la main ; "
        "3) compare avec le résultat attendu.",
        "",
        indice,
        extrait,
    )


def _diagnostic_sortie(resultat: dict, reference_test: str, visible: bool) -> dict:
    obtenues = resultat.get("lignes_obtenues", [])
    attendues = resultat.get("lignes_attendues", [])
    if not obtenues:
        description = "Ton programme n'affiche rien."
        indice = "Utilise print() pour afficher le résultat demandé."
    elif len(obtenues) != len(attendues):
        description = (f"Ton programme affiche {len(obtenues)} ligne(s) alors que la mission "
                       f"en attend {len(attendues)} ({reference_test}).")
        indice = "Compte tes print() et vérifie combien de fois ta boucle s'exécute."
    else:
        description = f"L'affichage diffère de celui attendu ({reference_test})."
        indice = "Compare ta sortie et la sortie attendue caractère par caractère."
        for numero, (a, b) in enumerate(zip(obtenues, attendues), start=1):
            if a != b:
                if visible:
                    description = f"Ligne {numero} : ton programme affiche « {a} » au lieu de « {b} »."
                else:
                    description = f"La ligne {numero} de ta sortie est différente ({reference_test})."
                if a.lower() == b.lower():
                    indice = "Seules les majuscules/minuscules diffèrent."
                elif " ".join(a.split()) == " ".join(b.split()):
                    indice = "Seuls les espaces diffèrent : attention à print(a, b) qui ajoute un espace."
                break
    return _fiche(
        "sortie_incorrecte", "Sortie incorrecte", "variables",
        "Ce que ton programme affiche n'est pas exactement ce qui est attendu",
        description,
        "Les tests comparent l'affichage mot pour mot : ponctuation, espaces et majuscules comptent.",
        "Ta sortie et la sortie attendue sont-elles identiques, caractère par caractère ?",
        "print(a, b) sépare par un espace ; print(f\"{a}-{b}\") donne un contrôle total.",
        'nom = "Lynx"\nprint(f"Agent {nom} prêt.")',
        indice,
    )

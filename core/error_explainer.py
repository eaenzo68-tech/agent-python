"""Explique les erreurs Python en français, avec des mots simples.

La fonction principale est `expliquer_erreur`. Elle reçoit la description
d'une erreur (produite par code_runner.decrire_exception) et renvoie une
« fiche diagnostic » affichée dans le téléphone de l'agent :

- categorie     : identifiant interne (sert aux statistiques et aux révisions) ;
- nom_categorie : nom lisible de la catégorie ;
- titre         : résumé en une phrase ;
- description   : ce qui s'est passé ;
- extrait       : les lignes de code concernées ;
- pourquoi      : pourquoi Python réagit ainsi ;
- question      : une question pour faire réfléchir (sans donner la réponse) ;
- rappel        : rappel du concept Python ;
- concept       : identifiant du concept (voir data/concepts.json) ;
- exemple       : un petit exemple DIFFÉRENT de la mission ;
- indice        : une piste pour corriger.
"""

from __future__ import annotations

import ast
import difflib
import keyword
import re

NOMS_INTEGRES = {
    "print", "input", "len", "range", "int", "float", "str", "bool", "list", "dict",
    "tuple", "set", "sum", "min", "max", "abs", "round", "sorted", "reversed",
    "enumerate", "zip", "type", "isinstance", "open", "map", "filter", "any", "all",
}


def _fiche(categorie, nom_categorie, concept, titre, description, pourquoi,
           question, rappel, exemple, indice) -> dict:
    """Assemble une fiche diagnostic (simple raccourci d'écriture)."""
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
    }


def extrait_code(code: str, ligne: int | None, contexte: int = 1) -> list[dict]:
    """Renvoie la ligne fautive et ses voisines, prêtes à être affichées."""
    if not code or not ligne:
        return []
    lignes = code.split("\n")
    debut = max(1, ligne - contexte)
    fin = min(len(lignes), ligne + contexte)
    return [
        {"numero": n, "texte": lignes[n - 1], "erreur": n == ligne}
        for n in range(debut, fin + 1)
    ]


def _noms_du_code(code: str) -> set[str]:
    """Tous les noms (variables, fonctions, paramètres) créés dans le code."""
    try:
        arbre = ast.parse(code)
    except SyntaxError:
        return set(re.findall(r"[A-Za-z_]\w*", code))
    noms = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Name) and isinstance(noeud.ctx, ast.Store):
            noms.add(noeud.id)
        elif isinstance(noeud, (ast.FunctionDef, ast.ClassDef)):
            noms.add(noeud.name)
        elif isinstance(noeud, ast.arg):
            noms.add(noeud.arg)
    return noms


def _noms_locaux_aux_fonctions(code: str) -> set[str]:
    """Noms créés uniquement à l'intérieur d'une fonction."""
    try:
        arbre = ast.parse(code)
    except SyntaxError:
        return set()
    locaux, globaux = set(), set()
    for noeud in arbre.body:
        if isinstance(noeud, ast.FunctionDef):
            for sous in ast.walk(noeud):
                if isinstance(sous, ast.Name) and isinstance(sous.ctx, ast.Store):
                    locaux.add(sous.id)
                elif isinstance(sous, ast.arg):
                    locaux.add(sous.arg)
        else:
            for sous in ast.walk(noeud):
                if isinstance(sous, ast.Name) and isinstance(sous.ctx, ast.Store):
                    globaux.add(sous.id)
    return locaux - globaux


# ---------------------------------------------------------------------------
# Erreurs de syntaxe
# ---------------------------------------------------------------------------

def _syntaxe(message: str, texte_ligne: str) -> dict:
    msg = message.lower()
    ligne = texte_ligne.strip()

    if "invalid character" in msg and ("u+201c" in msg or "u+201d" in msg
                                       or "u+2018" in msg or "u+2019" in msg):
        return _fiche(
            "guillemets_typographiques", "Guillemets typographiques", "chaines",
            "Des guillemets « courbes » se sont glissés dans ton code",
            "Ton code contient des guillemets “ ” ou ‘ ’. Python ne les reconnaît pas.",
            "Python accepte uniquement les guillemets droits \" et ' pour écrire du texte. "
            "Le clavier de l'iPad les transforme parfois automatiquement.",
            "Les guillemets autour de ton texte sont-ils bien droits ?",
            "Une chaîne de caractères s'écrit entre \" \" ou entre ' '.",
            'message = "Rendez-vous à minuit"\nprint(message)',
            "Retape les guillemets de la ligne indiquée. Sur iPad : Réglages > Général > "
            "Clavier > désactive « Ponctuation intelligente ».",
        )

    if "maybe you meant '==' or ':=' instead of '='" in msg or (
        re.match(r"^(if|elif|while)\b", ligne) and re.search(r"[^=!<>]=[^=]", ligne)
    ):
        return _fiche(
            "egalite_affectation", "Confusion entre = et ==", "conditions",
            "Tu as utilisé = dans une condition",
            "Dans une condition (if, elif, while), tu as écrit un seul signe =.",
            "En Python, = sert à RANGER une valeur dans une variable. "
            "Pour COMPARER deux valeurs, il faut ==.",
            "Ici, veux-tu ranger une valeur dans une variable, ou vérifier si deux valeurs sont égales ?",
            "=  : affectation (ranger)     ==  : comparaison (tester l'égalité)",
            'code = 7\nif code == 7:\n    print("Code reconnu")',
            "Dans la condition, remplace le = par ==.",
        )

    if "expected ':'" in msg:
        return _fiche(
            "deux_points", "Deux-points manquants", "conditions",
            "Il manque les deux-points « : »",
            "Une ligne qui ouvre un bloc (if, elif, else, for, while, def, try…) doit se terminer par « : ».",
            "Les deux-points annoncent à Python qu'un bloc indenté va suivre.",
            "Par quel caractère se termine la ligne indiquée ?",
            "if condition:\n    instruction   ← bloc décalé de 4 espaces",
            'for agent in ["Lynx", "Orion"]:\n    print(agent)',
            "Ajoute « : » à la fin de la ligne qui commence le bloc.",
        )

    if "was never closed" in msg or "unmatched" in msg or "does not match opening parenthesis" in msg:
        return _fiche(
            "parentheses", "Parenthèses ou crochets mal fermés", "variables",
            "Une parenthèse, un crochet ou une accolade n'est pas fermé correctement",
            "Python a trouvé un ( [ { sans son partenaire ) ] }, ou l'inverse.",
            "Chaque symbole ouvrant doit avoir exactement un symbole fermant du même type.",
            "Combien de parenthèses ouvrantes et fermantes comptes-tu sur cette ligne ?",
            "( ) pour les appels de fonctions, [ ] pour les listes, { } pour les dictionnaires.",
            'print(len([3, 1, 4]))   # 2 ( ouvertes, 2 ) fermées',
            "Compte les symboles ouvrants et fermants sur la ligne indiquée (et celle d'avant).",
        )

    if "unterminated string" in msg or "unterminated triple-quoted" in msg or "eol while scanning" in msg:
        return _fiche(
            "guillemets", "Texte mal fermé", "chaines",
            "Une chaîne de caractères n'est pas refermée",
            "Tu as ouvert des guillemets mais Python ne trouve pas les guillemets de fin.",
            "Le texte doit commencer et finir par le même type de guillemets.",
            "Où se termine ton texte sur cette ligne ?",
            "\"texte\" ou 'texte' : même guillemet au début et à la fin.",
            "phrase = \"L'agent arrive\"   # ' à l'intérieur de \" \" : aucun problème",
            "Ajoute les guillemets manquants à la fin du texte.",
        )

    if "missing parentheses in call to 'print'" in msg:
        return _fiche(
            "parentheses", "Parenthèses ou crochets mal fermés", "variables",
            "print a besoin de parenthèses",
            "En Python 3, print est une fonction : on l'appelle avec des parenthèses.",
            "Toutes les fonctions s'appellent avec des parenthèses, même print.",
            "Comment appelle-t-on une fonction en Python ?",
            "nom_fonction(arguments)",
            'print("Mission lancée")',
            "Écris print(...) avec des parenthèses.",
        )

    if "forgot a comma" in msg:
        return _fiche(
            "syntaxe", "Erreur de syntaxe", "listes",
            "Il manque probablement une virgule",
            "Deux valeurs se suivent sans virgule pour les séparer.",
            "Dans une liste, un tuple ou les arguments d'une fonction, chaque valeur est séparée par une virgule.",
            "Entre quels éléments de la ligne manque-t-il une séparation ?",
            "[valeur1, valeur2, valeur3]",
            'villes = ["Berne", "Genève", "Neuchâtel"]',
            "Ajoute une virgule entre les éléments de la ligne indiquée.",
        )

    if "cannot assign to" in msg:
        return _fiche(
            "syntaxe", "Erreur de syntaxe", "variables",
            "Ce qui est à gauche de = ne peut pas recevoir de valeur",
            "À gauche du signe =, il doit y avoir un nom de variable.",
            "Python range la valeur de droite dans la variable de gauche. "
            "Il ne peut pas ranger une valeur dans un nombre, un texte ou un appel de fonction.",
            "Ce qui est à gauche du = est-il bien un nom de variable ?",
            "nom_variable = valeur",
            "total = 5 + 3   # et non : 5 + 3 = total",
            "Mets le nom de la variable à gauche du = et la valeur à droite.",
        )

    if "invalid decimal literal" in msg:
        return _fiche(
            "syntaxe", "Erreur de syntaxe", "variables",
            "Un nom commence par un chiffre ou un nombre est mal écrit",
            "Python a trouvé un nombre collé à des lettres.",
            "Un nom de variable ne peut pas commencer par un chiffre.",
            "Le nom utilisé sur cette ligne commence-t-il par un chiffre ?",
            "Noms valides : agent_2, code_secret. Invalides : 2agent, code-secret.",
            "agent_1 = \"Lynx\"",
            "Renomme la variable pour qu'elle commence par une lettre.",
        )

    if "'return' outside function" in msg:
        return _fiche(
            "syntaxe", "Erreur de syntaxe", "fonctions",
            "return est utilisé en dehors d'une fonction",
            "return ne peut apparaître qu'à l'intérieur d'une fonction (après def).",
            "return sert à renvoyer le résultat d'une fonction. Hors d'une fonction, il n'a pas de sens.",
            "La ligne avec return est-elle bien décalée (indentée) sous le def ?",
            "def double(x):\n    return x * 2   ← indenté sous def",
            "def saluer(nom):\n    return \"Bonjour \" + nom",
            "Vérifie l'indentation : le return doit être dans le bloc de la fonction.",
        )

    if "outside loop" in msg:
        return _fiche(
            "syntaxe", "Erreur de syntaxe", "boucle-for",
            "break ou continue est utilisé en dehors d'une boucle",
            "break et continue ne fonctionnent que dans une boucle for ou while.",
            "Ces mots-clés contrôlent une boucle : sans boucle, Python ne sait pas quoi arrêter.",
            "La ligne est-elle bien indentée à l'intérieur de la boucle ?",
            "for x in valeurs:\n    if x < 0:\n        break",
            "for code in [3, 8, 0, 5]:\n    if code == 0:\n        break\n    print(code)",
            "Vérifie l'indentation de la ligne indiquée.",
        )

    mots = [m for m in re.findall(r"[A-Za-z_]+", ligne) if keyword.iskeyword(m)]
    complement = f" (la ligne contient le mot-clé « {mots[0]} »)" if mots else ""
    return _fiche(
        "syntaxe", "Erreur de syntaxe", "variables",
        "Python ne comprend pas l'écriture de cette ligne",
        "Le code ne respecte pas la grammaire de Python" + complement + ".",
        "Avant d'exécuter, Python lit tout le programme. S'il trouve une phrase mal construite, il refuse de commencer.",
        "Compare la ligne indiquée avec un exemple qui fonctionne : qu'est-ce qui diffère ?",
        "Vérifie : deux-points, parenthèses, guillemets, virgules, opérateurs.",
        'if age >= 18:\n    print("Majeur")',
        "Regarde aussi la ligne juste AVANT : l'erreur vient souvent de là (parenthèse non fermée…).",
    )


def _indentation(type_erreur: str, message: str) -> dict:
    msg = message.lower()
    if "expected an indented block" in msg:
        description = "Après une ligne qui se termine par « : », Python attend un bloc décalé vers la droite."
        question = "La ligne qui suit les deux-points est-elle bien décalée de 4 espaces ?"
    elif "unexpected indent" in msg:
        description = "Une ligne est décalée vers la droite alors que rien ne l'exige."
        question = "Pourquoi cette ligne est-elle plus à droite que celle du dessus ?"
    elif "unindent does not match" in msg:
        description = "Une ligne revient vers la gauche, mais pas exactement au niveau d'un bloc précédent."
        question = "Avec quelle ligne du dessus cette ligne devrait-elle être alignée ?"
    elif type_erreur == "TabError" or "tabs and spaces" in msg:
        description = "Ton code mélange des tabulations et des espaces pour l'indentation."
        question = "As-tu utilisé la touche Tab à certains endroits et la barre d'espace ailleurs ?"
    else:
        description = "L'indentation (le décalage en début de ligne) n'est pas cohérente."
        question = "Les lignes d'un même bloc commencent-elles toutes au même niveau ?"
    return _fiche(
        "indentation", "Indentation", "conditions",
        "Problème d'indentation (décalage des lignes)",
        description,
        "En Python, l'indentation n'est pas décorative : elle indique quelles lignes font partie "
        "d'un bloc (if, for, def…). Toutes les lignes d'un bloc doivent être alignées.",
        question,
        "Convention : 4 espaces par niveau. Une ligne qui finit par « : » ouvre un bloc.",
        'for agent in equipe:\n    print(agent)      # dans la boucle\nprint("Fin")          # après la boucle',
        "Aligne la ligne indiquée avec les autres lignes du même bloc (multiples de 4 espaces).",
    )


# ---------------------------------------------------------------------------
# Erreurs pendant l'exécution
# ---------------------------------------------------------------------------

def _nom_inconnu(erreur: dict, code: str, ligne_erreur: int | None) -> dict:
    nom = erreur.get("nom") or ""
    if not nom:
        trouve = re.search(r"name '(\w+)' is not defined", erreur.get("message", ""))
        nom = trouve.group(1) if trouve else "?"
    connus = _noms_du_code(code) | NOMS_INTEGRES
    proches = difflib.get_close_matches(nom, sorted(connus - {nom}), n=1, cutoff=0.75)
    locaux = _noms_locaux_aux_fonctions(code)

    if proches:
        pourquoi = (f"Python ne connaît pas « {nom} », mais il connaît « {proches[0]} ». "
                    "Une seule lettre différente (ou une majuscule) suffit pour que ce soit un autre nom.")
        indice = f"Compare l'orthographe de « {nom} » avec « {proches[0]} »."
    elif nom in locaux:
        pourquoi = (f"« {nom} » existe seulement À L'INTÉRIEUR d'une fonction. "
                    "En dehors de la fonction, ce nom n'existe pas.")
        indice = "Récupère la valeur avec return, puis range-la dans une variable : resultat = ma_fonction(...)."
    elif _utilise_avant_creation(code, nom, ligne_erreur):
        pourquoi = f"« {nom} » est créé plus bas dans le code, mais Python lit le programme de haut en bas."
        indice = f"Crée « {nom} » (avec =) AVANT la ligne qui l'utilise."
    else:
        pourquoi = (f"Python ne trouve aucune variable ni fonction appelée « {nom} ». "
                    "Si tu voulais écrire du texte, il faut des guillemets.")
        indice = f"Crée « {nom} » avec = avant de l'utiliser, ou mets-le entre guillemets si c'est du texte."
    return _fiche(
        "nom_inconnu", "Nom inconnu (NameError)", "variables",
        f"Le nom « {nom} » est inconnu",
        f"Ton programme utilise « {nom} », mais ce nom n'a jamais été créé à cet endroit.",
        pourquoi,
        f"Où as-tu créé « {nom} » ? Est-il écrit exactement pareil partout (majuscules comprises) ?",
        "Une variable doit être créée (nom = valeur) avant d'être utilisée. Python distingue majuscules et minuscules.",
        'agent = "Orion"\nprint(agent)     # fonctionne\nprint(Agent)     # NameError : A majuscule',
        indice,
    )


def _utilise_avant_creation(code: str, nom: str, ligne_erreur: int | None) -> bool:
    if not ligne_erreur:
        return False
    for numero, texte in enumerate(code.split("\n"), start=1):
        if numero > ligne_erreur and re.match(rf"^\s*{re.escape(nom)}\s*=[^=]", texte):
            return True
    return False


def _erreur_type(message: str) -> dict:
    msg = message.lower()

    if "nonetype" in msg:
        return _fiche(
            "retour_none", "Valeur None inattendue", "print-return",
            "Tu utilises une valeur qui vaut None (rien)",
            "Une de tes valeurs vaut None. C'est souvent le résultat d'une fonction sans return.",
            "Une fonction sans return renvoie automatiquement None. De même, liste.sort() ou "
            "liste.append() modifient la liste mais renvoient None.",
            "La fonction utilisée sur cette ligne renvoie-t-elle vraiment une valeur avec return ?",
            "print() AFFICHE une valeur ; return la RENVOIE pour qu'on puisse la réutiliser.",
            "def triple(x):\n    return x * 3      # avec return, on récupère 15\n\nresultat = triple(5)",
            "Vérifie que la fonction contient un return, et que tu n'écris pas liste = liste.sort().",
        )

    if (
        "can only concatenate" in msg
        or ("unsupported operand" in msg and "'str'" in msg)
        or ("not supported between instances of" in msg and "'str'" in msg)
    ):
        return _fiche(
            "conversion_type", "Mélange de types (texte et nombre)", "types",
            "Tu mélanges du texte et un nombre",
            "Python ne sait pas additionner ou comparer directement un texte (str) et un nombre (int/float).",
            "Pour Python, \"5\" (texte) et 5 (nombre) sont deux choses différentes. "
            "Il faut convertir l'une des deux valeurs.",
            "Quel est le type de chaque valeur sur cette ligne ? Utilise type(valeur) pour vérifier.",
            "int(\"5\") → 5     str(5) → \"5\"     input() renvoie toujours un texte.",
            'age = int("17")\nprint("Âge : " + str(age))\nprint(f"Âge : {age}")   # f-string : plus simple',
            "Convertis avec int(), float() ou str(), ou utilise une f-string pour afficher.",
        )

    if ("required positional argument" in msg) or ("positional argument" in msg and "given" in msg):
        return _fiche(
            "arguments", "Mauvais nombre d'arguments", "fonctions",
            "La fonction ne reçoit pas le bon nombre d'arguments",
            "Tu appelles une fonction avec plus ou moins de valeurs que ce qu'elle attend.",
            "Chaque paramètre écrit dans le def doit recevoir une valeur lors de l'appel.",
            "Combien de paramètres la fonction a-t-elle dans son def ? Combien de valeurs lui donnes-tu ?",
            "def f(a, b):  →  appel : f(1, 2)",
            "def distance(depart, arrivee):\n    return arrivee - depart\n\nprint(distance(3, 10))",
            "Compare l'appel de la fonction avec sa définition (le def).",
        )

    if "object is not callable" in msg:
        return _fiche(
            "type", "Type incorrect (TypeError)", "fonctions",
            "Tu utilises des parenthèses sur quelque chose qui n'est pas une fonction",
            "Python essaie d'« appeler » une valeur (nombre, texte, liste…) comme si c'était une fonction.",
            "Cela arrive souvent quand une variable porte le même nom qu'une fonction (ex. sum = 0 puis sum(...)), "
            "ou quand il manque un * entre un nombre et une parenthèse.",
            "As-tu créé une variable qui porte le nom d'une fonction intégrée (sum, max, list, str…) ?",
            "N'utilise jamais sum, max, list, str… comme nom de variable.",
            "total = 0          # et non : sum = 0\ntotal = sum([1, 2, 3])",
            "Renomme la variable qui cache la fonction, ou ajoute l'opérateur manquant (2 * (3 + 4)).",
        )

    if "does not support item assignment" in msg:
        return _fiche(
            "type", "Type incorrect (TypeError)", "chaines",
            "Tu essaies de modifier une valeur qui ne peut pas être modifiée",
            "Les chaînes de caractères et les tuples sont « immuables » : on ne peut pas changer un élément.",
            "texte[0] = \"A\" est interdit : il faut créer une NOUVELLE chaîne.",
            "Comment pourrais-tu construire une nouvelle valeur au lieu de modifier l'ancienne ?",
            "Les listes sont modifiables, les str et les tuples ne le sont pas.",
            'mot = "lynx"\nmot = "L" + mot[1:]   # nouvelle chaîne : "Lynx"',
            "Construis une nouvelle chaîne (concaténation, replace, join…) ou utilise une liste.",
        )

    if "is not iterable" in msg:
        return _fiche(
            "type", "Type incorrect (TypeError)", "boucle-for",
            "Tu essaies de parcourir quelque chose qui ne se parcourt pas",
            "for … in … a besoin d'une collection (liste, texte, range…). Un nombre seul ne se parcourt pas.",
            "Pour répéter n fois, il faut range(n), pas n directement.",
            "Que veux-tu parcourir : les éléments d'une liste, ou les nombres de 0 à n ?",
            "for i in range(5):  → 0, 1, 2, 3, 4",
            "for i in range(3):\n    print(\"Tentative\", i + 1)",
            "Utilise range(nombre) ou parcours directement la liste.",
        )

    if "indices must be integers" in msg:
        return _fiche(
            "type", "Type incorrect (TypeError)", "listes",
            "L'indice utilisé n'est pas un nombre entier",
            "Pour accéder à un élément d'une liste ou d'un texte, l'indice doit être un entier (0, 1, 2…).",
            "Tu utilises peut-être un texte ou un nombre à virgule comme position. "
            "Dans « for x in liste », x est déjà l'élément, pas sa position.",
            "Ta variable contient-elle une position (entier) ou un élément de la liste ?",
            "liste[0] → premier élément ; liste[1.0] et liste[\"0\"] sont interdits.",
            "codes = [12, 45, 78]\nfor code in codes:\n    print(code)          # code est déjà l'élément",
            "Utilise directement l'élément, ou convertis la position avec int() (ou // au lieu de /).",
        )

    if "has no len()" in msg:
        return _fiche(
            "type", "Type incorrect (TypeError)", "types",
            "len() ne fonctionne pas sur ce type de valeur",
            "len() mesure la longueur d'une collection (liste, texte, dictionnaire…), pas d'un nombre.",
            "Un nombre n'a pas de « longueur ». Pour compter ses chiffres, il faut d'abord le convertir en texte.",
            "Quel est le type de la valeur donnée à len() ?",
            "len(\"agent\") → 5     len([1, 2]) → 2     len(42) → erreur",
            "code = 4096\nprint(len(str(code)))   # 4 chiffres",
            "Vérifie le type de la valeur avec type(), ou convertis-la avec str().",
        )

    if "unhashable type" in msg:
        return _fiche(
            "type", "Type incorrect (TypeError)", "dictionnaires",
            "Cette valeur ne peut pas être une clé de dictionnaire",
            "Une liste (ou un dictionnaire) ne peut pas servir de clé de dictionnaire ni être mise dans un set.",
            "Les clés doivent être des valeurs qui ne changent pas : str, int, tuple…",
            "Quelle valeur utilises-tu comme clé ?",
            "Clés valides : \"Lynx\", 42, (3, 4). Clé invalide : [3, 4].",
            "positions = {(3, 4): \"Base Alpha\"}   # un tuple comme clé",
            "Utilise un texte, un nombre ou un tuple comme clé.",
        )

    return _fiche(
        "type", "Type incorrect (TypeError)", "types",
        "Une opération est utilisée avec un type de valeur incompatible",
        "Python ne peut pas faire cette opération avec ce type de données.",
        "Chaque type (int, str, list…) accepte certaines opérations seulement.",
        "Quel est le type de chaque valeur sur la ligne indiquée ?",
        "type(valeur) affiche le type d'une valeur.",
        'print(type(3), type("3"), type([3]))',
        "Affiche le type des valeurs avec print(type(...)) juste avant la ligne fautive.",
    )


def _erreur_valeur(message: str) -> dict:
    msg = message.lower()
    if "invalid literal for int()" in msg or "could not convert string to float" in msg:
        return _fiche(
            "conversion_texte", "Conversion impossible (ValueError)", "exceptions",
            "Ce texte ne peut pas être converti en nombre",
            f"Python a essayé de transformer un texte en nombre, mais le texte ne contient pas un nombre valide ({message}).",
            "int(\"42\") fonctionne, mais int(\"quarante\") ou int(\"4.5\") échouent.",
            "Que contient exactement le texte que tu essaies de convertir ? Y a-t-il des espaces ou des lettres ?",
            "Pour gérer un texte invalide, on utilise try / except ValueError.",
            'try:\n    code = int("7A")\nexcept ValueError:\n    code = None',
            "Vérifie la valeur à convertir ou protège la conversion avec try / except ValueError.",
        )
    if "values to unpack" in msg:
        return _fiche(
            "valeur", "Valeur incorrecte (ValueError)", "tuples",
            "Le nombre de variables ne correspond pas au nombre de valeurs",
            "Tu répartis des valeurs dans plusieurs variables (a, b = …), mais les quantités diffèrent.",
            "Pour écrire a, b = valeurs, il faut exactement 2 valeurs.",
            "Combien de valeurs contient l'élément que tu « déballes » ?",
            "x, y = (3, 4)   → x = 3, y = 4",
            "nom, ville = (\"Lynx\", \"Berne\")",
            "Vérifie le nombre de variables à gauche du = et le nombre de valeurs à droite.",
        )
    if "not in list" in msg:
        return _fiche(
            "valeur", "Valeur incorrecte (ValueError)", "listes",
            "La valeur recherchée n'est pas dans la liste",
            "liste.index(x) ou liste.remove(x) échouent quand x n'est pas dans la liste.",
            "Ces méthodes supposent que l'élément existe.",
            "Comment vérifier qu'un élément est présent avant de le chercher ?",
            "if x in liste:  → vérifie la présence",
            'agents = ["Lynx", "Orion"]\nif "Vega" in agents:\n    agents.remove("Vega")',
            "Teste la présence avec « in » avant d'utiliser index() ou remove().",
        )
    return _fiche(
        "valeur", "Valeur incorrecte (ValueError)", "types",
        "La valeur a le bon type, mais elle n'est pas acceptable",
        f"Une fonction a reçu une valeur qu'elle ne peut pas traiter ({message}).",
        "Le type est correct, mais le contenu ne convient pas (ex. racine carrée d'un nombre négatif).",
        "Quelle valeur reçoit la fonction sur la ligne indiquée ?",
        "On peut vérifier une valeur avec if avant de l'utiliser, ou utiliser try / except.",
        "import math\nnombre = 16\nif nombre >= 0:\n    print(math.sqrt(nombre))",
        "Affiche la valeur juste avant la ligne fautive pour voir ce qu'elle contient.",
    )


def _erreur_index(message: str) -> dict:
    vide = "pop from empty" in message.lower()
    return _fiche(
        "index", "Indice hors limites (IndexError)", "listes",
        "Tu essaies de lire une case qui n'existe pas" if not vide else "Tu retires un élément d'une liste vide",
        "La position demandée est en dehors de la liste (ou du texte)." if not vide
        else "pop() a été appelé sur une liste qui ne contient plus rien.",
        "Les positions commencent à 0. Une liste de 3 éléments a les indices 0, 1 et 2 : l'indice 3 n'existe pas.",
        "Combien d'éléments contient la liste à ce moment-là ? Quel indice demandes-tu ?",
        "Indices valides : de 0 à len(liste) - 1. Le dernier élément : liste[-1].",
        'agents = ["Lynx", "Orion", "Vega"]\nprint(agents[2])     # "Vega" (3e élément)\nprint(agents[-1])    # "Vega" aussi',
        "Vérifie les bornes de ton range() (range(len(liste)) s'arrête juste avant len) et le cas de la liste vide.",
    )


def _erreur_cle(erreur: dict) -> dict:
    cle = erreur.get("cle") or erreur.get("message", "?")
    return _fiche(
        "cle", "Clé absente (KeyError)", "dictionnaires",
        f"La clé {cle} n'existe pas dans le dictionnaire",
        f"Tu demandes la valeur associée à {cle}, mais cette clé n'est pas dans le dictionnaire.",
        "dico[cle] suppose que la clé existe. Attention aussi aux majuscules et aux espaces.",
        "Quelles clés contient vraiment ton dictionnaire ? Affiche-les avec print(dico.keys()).",
        "dico.get(cle, valeur_par_defaut) renvoie une valeur par défaut si la clé manque.",
        'bases = {"Lynx": "Berne"}\nprint(bases.get("Orion", "inconnue"))   # pas d\'erreur\nif "Orion" in bases:\n    print(bases["Orion"])',
        "Vérifie l'orthographe de la clé, ou utilise .get() / « if cle in dico ».",
    )


def _division_zero() -> dict:
    return _fiche(
        "division_zero", "Division par zéro", "exceptions",
        "Ton programme divise par zéro",
        "Une division (/, // ou %) a été faite avec un diviseur égal à 0.",
        "La division par zéro n'a pas de sens en mathématiques : Python refuse de la calculer.",
        "Dans quel cas le diviseur peut-il valoir 0 ? (liste vide, compteur pas encore augmenté…)",
        "Avant de diviser, on vérifie le diviseur avec if, ou on utilise try / except ZeroDivisionError.",
        "notes = []\nif len(notes) > 0:\n    moyenne = sum(notes) / len(notes)\nelse:\n    moyenne = 0",
        "Prévois le cas où le diviseur vaut 0 (souvent : une liste vide).",
    )


def _erreur_attribut(erreur: dict) -> dict:
    message = erreur.get("message", "")
    if "nonetype" in message.lower():
        return _erreur_type(message)
    suggestions = {
        "push": "append", "add": "append (pour une liste)", "length": "len(...)",
        "size": "len(...)", "lenght": "len(...)", "uppercase": "upper", "lowercase": "lower",
        "contains": "le mot-clé in", "trim": "strip", "toupper": "upper", "tolower": "lower",
    }
    attribut = erreur.get("attribut") or ""
    piste = suggestions.get(attribut.lower())
    indice = (f"La méthode « {attribut} » n'existe pas. Pense plutôt à « {piste} »." if piste
              else "Vérifie le type de ta valeur, puis cherche la bonne méthode dans la Bibliothèque des concepts.")
    return _fiche(
        "attribut", "Méthode inconnue (AttributeError)", "types",
        "Cette valeur n'a pas la méthode demandée",
        f"Tu utilises .{attribut or '…'} sur une valeur qui ne possède pas cette méthode.",
        "Chaque type a ses propres méthodes : les listes ont append, les textes ont upper, etc.",
        "Quel est le type de la valeur avant le point ? Cette méthode existe-t-elle pour ce type ?",
        "liste.append(x)   texte.upper()   dico.get(cle)",
        'agents = ["Lynx"]\nagents.append("Orion")\nprint("vega".upper())',
        indice,
    )


def _boucle_infinie(erreur: dict) -> dict:
    repetitions = erreur.get("repetitions")
    detail = f" La ligne {erreur.get('ligne')} a été exécutée {repetitions:,} fois.".replace(",", " ") \
        if repetitions else ""
    return _fiche(
        "boucle_infinie", "Boucle infinie ou trop longue", "boucle-while",
        "Ton programme ne s'arrête pas (boucle infinie probable)",
        "Le programme a dépassé la limite de temps et a été arrêté." + detail,
        "Une boucle while s'arrête seulement quand sa condition devient fausse. "
        "Si rien ne modifie les variables de la condition, elle tourne pour toujours.",
        "Quelle ligne, à l'intérieur de la boucle, rapproche la condition de « fausse » ?",
        "Dans une boucle while, il faut modifier la variable testée (ex. compteur += 1).",
        "compteur = 0\nwhile compteur < 3:\n    print(compteur)\n    compteur += 1   # sans cette ligne : boucle infinie",
        "Vérifie que la variable de la condition change à chaque tour, dans le bon sens.",
    )


def _entree_manquante() -> dict:
    return _fiche(
        "entree_manquante", "Entrée manquante (input)", "types",
        "input() attend une valeur qui n'a pas été fournie",
        "Le programme appelle input(), mais la zone « Entrées » est vide (ou contient trop peu de lignes).",
        "Dans l'application, on ne tape pas les réponses en direct : on les prépare dans la zone « Entrées ».",
        "Combien de fois ton programme appelle-t-il input() ?",
        "Une ligne dans la zone « Entrées » = une réponse à un input().",
        'nom = input("Nom de code ? ")\nprint("Bienvenue", nom)',
        "Ouvre la zone « Entrées » sous l'éditeur et écris une valeur par ligne.",
    )


def _recursion() -> dict:
    return _fiche(
        "recursion", "Récursion infinie", "fonctions",
        "Une fonction s'appelle elle-même sans fin",
        "La fonction se rappelle elle-même trop de fois (plus de 1000 appels imbriqués).",
        "Une fonction qui s'appelle elle-même doit avoir un « cas de base » qui arrête les appels.",
        "Dans quel cas ta fonction devrait-elle s'arrêter sans se rappeler ?",
        "Toute fonction récursive : 1) cas de base ; 2) appel sur un problème plus petit.",
        "def compte_a_rebours(n):\n    if n == 0:          # cas de base\n        return\n    print(n)\n    compte_a_rebours(n - 1)",
        "Ajoute (ou corrige) la condition d'arrêt de ta fonction.",
    )


def _variable_locale(message: str) -> dict:
    return _fiche(
        "variable_locale", "Variable locale non définie", "fonctions",
        "Une variable est utilisée dans une fonction avant d'y recevoir une valeur",
        "Dans ta fonction, une variable est lue avant d'être créée (" + message + ").",
        "Si une fonction modifie une variable (avec =), Python la considère comme locale à la fonction. "
        "Elle n'existe donc pas encore au moment où tu la lis.",
        "Cette variable devrait-elle plutôt être un paramètre de la fonction ?",
        "Passe les valeurs à une fonction par ses paramètres, et récupère le résultat avec return.",
        "def ajouter_point(score):\n    score = score + 1\n    return score",
        "Initialise la variable au début de la fonction, ou passe-la en paramètre.",
    )


def _module_interdit(message: str) -> dict:
    return _fiche(
        "import_interdit", "Module non autorisé", "fonctions",
        "Ce module n'est pas disponible pendant les missions",
        message,
        "Pour ta sécurité, seuls quelques modules utiles à l'apprentissage peuvent être importés.",
        "Peux-tu résoudre la mission avec les outils de base de Python ?",
        "Modules autorisés : math, random, string, collections, statistics, datetime…",
        "import math\nprint(math.floor(3.7))",
        "Retire cet import : la mission peut être résolue sans lui.",
    )


def _fonction_desactivee(message: str) -> dict:
    return _fiche(
        "fonction_desactivee", "Fonction désactivée", "fonctions",
        "Cette fonction est désactivée dans les missions",
        message,
        "Certaines fonctions sont dangereuses ou inutiles ici (eval, exec, exit…).",
        "Quelle autre façon de faire existe en Python ?",
        "On peut presque toujours remplacer eval() par int(), float() ou une structure de données.",
        'texte = "42"\nnombre = int(texte)   # au lieu de eval(texte)',
        "Remplace cette fonction par une solution plus simple.",
    )


def _generique(type_erreur: str, message: str) -> dict:
    return _fiche(
        "autre", f"Autre erreur ({type_erreur})", "variables",
        f"Python a signalé une erreur {type_erreur}",
        f"Message de Python : {message}",
        "Python s'arrête dès qu'il rencontre une situation qu'il ne sait pas gérer.",
        "Que contiennent tes variables juste avant la ligne indiquée ?",
        "Ajouter des print() temporaires aide à comprendre ce qui se passe.",
        'valeur = 10\nprint("DEBUG valeur =", valeur)',
        "Ajoute un print() juste avant la ligne fautive pour observer les valeurs.",
    )


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def expliquer_erreur(erreur: dict, code: str = "") -> dict:
    """Construit la fiche diagnostic complète pour une erreur Python."""
    type_erreur = erreur.get("type", "Erreur")
    message = erreur.get("message", "")
    ligne = erreur.get("ligne")
    texte_ligne = erreur.get("texte_ligne", "")

    if type_erreur in ("IndentationError", "TabError"):
        fiche = _indentation(type_erreur, message)
    elif type_erreur == "SyntaxError":
        fiche = _syntaxe(message, texte_ligne)
    elif type_erreur == "NameError":
        fiche = _nom_inconnu(erreur, code, ligne)
    elif type_erreur == "UnboundLocalError":
        fiche = _variable_locale(message)
    elif type_erreur == "TypeError":
        fiche = _erreur_type(message)
    elif type_erreur == "ValueError":
        fiche = _erreur_valeur(message)
    elif type_erreur == "IndexError":
        fiche = _erreur_index(message)
    elif type_erreur == "KeyError":
        fiche = _erreur_cle(erreur)
    elif type_erreur == "ZeroDivisionError":
        fiche = _division_zero()
    elif type_erreur == "AttributeError":
        fiche = _erreur_attribut(erreur)
    elif type_erreur in ("BoucleInfinie", "DelaiDepasse"):
        fiche = _boucle_infinie(erreur)
    elif type_erreur == "EOFError":
        fiche = _entree_manquante()
    elif type_erreur == "RecursionError":
        fiche = _recursion()
    elif type_erreur in ("ImportError", "ModuleNotFoundError"):
        fiche = _module_interdit(message)
    elif type_erreur == "FonctionDesactivee":
        fiche = _fonction_desactivee(message)
    else:
        fiche = _generique(type_erreur, message)

    fiche.update({
        "type": type_erreur,
        "message_python": message,
        "ligne": ligne,
        "extrait": extrait_code(code, ligne),
    })
    return fiche

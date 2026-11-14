"""Source des 37 missions de départ (format Python, plus facile à lire et à modifier).

Pour ajouter ou modifier une mission :
1. modifie ce fichier ;
2. lance :  python outils/construire_donnees.py
   Le script vérifie que chaque solution réussit tous ses tests, que le code
   de départ ne les réussit PAS, puis écrit data/missions.json.

Niveaux (progression recommandée) :
1 compléter une ligne · 2 écrire quelques lignes · 3 compléter une fonction ·
4 écrire une fonction entière · 5 combiner plusieurs concepts ·
6 résoudre une petite situation réelle · 7 corriger un programme existant.
"""

from textwrap import dedent

BAREME = {"points": 100, "penalite_indice": 10, "penalite_tentative": 5,
          "penalite_solution": 50, "bonus_qualite": 10}


def c(texte):
    """Code écrit entre triple guillemets → texte propre."""
    return dedent(texte).strip("\n") + "\n"


def t(texte):
    """Texte sur plusieurs lignes → un seul paragraphe."""
    return " ".join(dedent(texte).split())


def appel(fonction, args, attendu, description, visible=False, **options):
    test = {"type": "appel", "fonction": fonction, "args": args, "attendu": attendu,
            "description": description, "visible": visible}
    test.update(options)
    return test


def sortie(attendu, description, entrees=None, visible=False):
    return {"type": "sortie", "attendu": attendu, "description": description,
            "entrees": entrees or [], "visible": visible}


def variable(nom, attendu, description, visible=True):
    return {"type": "variable", "nom": nom, "attendu": attendu, "description": description,
            "visible": visible}


def structure(description, doit_utiliser=(), interdit=()):
    return {"type": "structure", "doit_utiliser": list(doit_utiliser), "interdit": list(interdit),
            "description": description, "visible": True}


def tup(*valeurs):
    """Écriture JSON d'un tuple."""
    return {"__tuple__": list(valeurs)}


MISSIONS = []


def mission(**champs):
    champs.setdefault("bareme", BAREME)
    champs.setdefault("elements", "éléments")
    champs.setdefault("origine", "banque")
    MISSIONS.append(champs)


# ===========================================================================
# VARIABLES ET TYPES
# ===========================================================================

mission(
    id="VAR-01", ordre=1, theme="variables", concepts=["variables", "chaines"], niveau=1,
    difficulte="facile", titre="Opération Premier Contact",
    briefing=t("""Bienvenue à l'Agence, recrue. Avant toute chose, le terminal sécurisé doit
        enregistrer ton nom de code. Une seule ligne te sépare de ton premier rapport."""),
    objectif="Créer une variable contenant du texte et l'utiliser dans print().",
    enonce=t("""Remplace les « ... » pour que la variable nom_code contienne le texte "Faucon".
        Ne modifie pas la ligne print."""),
    donnees='Nom de code attribué : "Faucon"',
    resultat_attendu="Agent Faucon au rapport",
    code_depart=c('''
        # Ton nom de code est "Faucon".
        nom_code = ...   # ← remplace ... par le texte "Faucon"
        print("Agent", nom_code, "au rapport")
    '''),
    tests=[
        variable("nom_code", "Faucon", "valeur de nom_code"),
        sortie("Agent Faucon au rapport\n", "affichage du rapport", visible=True),
    ],
    indices=[
        "Un texte en Python s'écrit entre guillemets. Que faut-il mettre à droite du signe = ?",
        "Le signe = range la valeur de droite dans la variable de gauche. Un texte (str) s'écrit \"comme ceci\".",
        "Exemple similaire :\nville = \"Berne\"\nprint(\"Base de\", ville)",
    ],
    solution=c('''
        # Ton nom de code est "Faucon".
        nom_code = "Faucon"
        print("Agent", nom_code, "au rapport")
    '''),
    explication=t("""Une variable est une étiquette posée sur une valeur. nom_code = "Faucon" crée
        l'étiquette nom_code et y range le texte "Faucon". Ensuite, print() remplace le nom de la
        variable par sa valeur, et sépare chaque élément par un espace."""),
)

mission(
    id="VAR-02", ordre=2, theme="variables", concepts=["types", "variables"], niveau=2,
    difficulte="facile", titre="Opération Fréquence Radio", revision_pour=["conversion_type"],
    briefing=t("""La radio a capté la fréquence de l'équipe Alpha. Problème : la radio transmet tout
        sous forme de TEXTE. Il faut calculer la fréquence de secours, 25 unités plus haut."""),
    objectif="Convertir un texte en nombre entier avec int() avant de calculer.",
    enonce=t("""1) Crée la variable frequence : la conversion en nombre entier de frequence_texte.
        2) Crée frequence_secours = frequence + 25.
        3) Affiche exactement : Fréquence de secours : 1475"""),
    donnees='frequence_texte = "1450"',
    resultat_attendu="Fréquence de secours : 1475",
    code_depart=c('''
        frequence_texte = "1450"   # reçu par radio : c'est du TEXTE (str)

        # 1. Convertis frequence_texte en nombre entier dans la variable frequence

        # 2. Calcule frequence_secours

        # 3. Affiche le résultat
    '''),
    tests=[
        variable("frequence", 1450, "frequence est un nombre entier"),
        variable("frequence_secours", 1475, "frequence_secours"),
        sortie("Fréquence de secours : 1475\n", "affichage", visible=True),
    ],
    indices=[
        "Que donne \"1450\" + 25 en Python ? Le texte \"1450\" et le nombre 1450 sont-ils la même chose ?",
        "int(texte) transforme un texte comme \"42\" en nombre 42. Ensuite, tu peux additionner.",
        "Exemple :\nage_texte = \"17\"\nage = int(age_texte)\nage_l_an_prochain = age + 1\n"
        "print(f\"Âge : {age_l_an_prochain}\")",
    ],
    solution=c('''
        frequence_texte = "1450"   # reçu par radio : c'est du TEXTE (str)

        frequence = int(frequence_texte)
        frequence_secours = frequence + 25
        print(f"Fréquence de secours : {frequence_secours}")
    '''),
    explication=t("""Chaque valeur a un type : str pour le texte, int pour les entiers, float pour les
        nombres à virgule. Python refuse d'additionner un str et un int : il faut convertir avec int(),
        float() ou str(). La f-string f"... {variable}" insère une valeur dans un texte, sans
        conversion manuelle."""),
)

mission(
    id="VAR-03", ordre=7, theme="variables", concepts=["variables", "fonctions", "tuples"], niveau=3,
    difficulte="facile", titre="Opération Horloge",
    briefing=t("""Les rapports indiquent les durées de surveillance en minutes. Le commandement veut
        des heures et des minutes : 135 minutes, c'est 2 h 15."""),
    objectif="Utiliser la division entière // et le reste %.",
    enonce=t("""Complète convertir_minutes(total_minutes) pour qu'elle renvoie le tuple
        (heures, minutes). Utilise // (division entière) et % (reste)."""),
    donnees="convertir_minutes(135)",
    resultat_attendu="(2, 15)",
    code_depart=c('''
        def convertir_minutes(total_minutes):
            """Convertit une durée en minutes en (heures, minutes)."""
            heures = ...     # combien de fois 60 dans total_minutes ?
            minutes = ...    # combien reste-t-il ?
            return (heures, minutes)
    '''),
    tests=[
        appel("convertir_minutes", [135], tup(2, 15), "135 minutes", True),
        appel("convertir_minutes", [60], tup(1, 0), "pile une heure"),
        appel("convertir_minutes", [59], tup(0, 59), "moins d'une heure"),
        appel("convertir_minutes", [0], tup(0, 0), "zéro"),
        appel("convertir_minutes", [601], tup(10, 1), "longue mission"),
    ],
    indices=[
        "Dans 135 minutes, combien de « paquets » de 60 minutes entiers y a-t-il ? Et combien de minutes restent ?",
        "a // b donne le quotient entier (135 // 60 = 2). a % b donne le reste (135 % 60 = 15).",
        "Exemple : convertir des secondes en minutes :\nminutes = 150 // 60   # 2\nsecondes = 150 % 60   # 30",
    ],
    solution=c('''
        def convertir_minutes(total_minutes):
            """Convertit une durée en minutes en (heures, minutes)."""
            heures = total_minutes // 60
            minutes = total_minutes % 60
            return (heures, minutes)
    '''),
    explication=t("""// et % forment un duo : 135 = 60 × 2 + 15. On les utilise dès qu'il faut découper
        une quantité (heures/minutes, mètres/centimètres, pages/lignes…). Le tuple (heures, minutes)
        permet de renvoyer deux valeurs à la fois."""),
)

mission(
    id="VAR-04", ordre=15, theme="variables", concepts=["types", "chaines", "fonctions"], niveau=4,
    difficulte="intermediaire", titre="Opération Badge d'Identité",
    briefing=t("""Chaque agent reçoit un badge au format NOM-NUMÉRO, en majuscules, avec un numéro
        toujours écrit sur 3 chiffres : LYNX-007."""),
    objectif="Combiner conversion de types, méthodes de chaînes et f-string.",
    enonce=t("""Écris creer_badge(nom, numero) qui renvoie le nom en majuscules, un tiret, puis le
        numéro complété avec des zéros à gauche pour avoir 3 chiffres."""),
    donnees='creer_badge("lynx", 7)',
    resultat_attendu='"LYNX-007"',
    code_depart="def creer_badge(nom, numero):\n    pass\n",
    tests=[
        appel("creer_badge", ["lynx", 7], "LYNX-007", "exemple", True),
        appel("creer_badge", ["Orion", 42], "ORION-042", "deux chiffres"),
        appel("creer_badge", ["vega", 123], "VEGA-123", "trois chiffres"),
        appel("creer_badge", ["Écho", 0], "ÉCHO-000", "numéro zéro"),
    ],
    indices=[
        "Il y a deux transformations : une sur le nom, une sur le numéro. Lesquelles ?",
        "texte.upper() met en majuscules. str(nombre).zfill(3) complète avec des zéros à gauche "
        "(\"7\" → \"007\"). Dans une f-string, {numero:03d} fait la même chose.",
        "Exemple :\ncode = 5\nprint(\"ZONE\" + \"-\" + str(code).zfill(2))   # ZONE-05\nprint(f\"ZONE-{code:02d}\")             # ZONE-05",
    ],
    solution=c('''
        def creer_badge(nom, numero):
            """Renvoie le badge au format NOM-NNN."""
            return f"{nom.upper()}-{numero:03d}"
    '''),
    explication=t("""La f-string permet de formater un nombre : {numero:03d} signifie « entier (d) sur
        3 caractères, complété par des 0 ». La version str(numero).zfill(3) est équivalente et tout aussi
        correcte."""),
)

# ===========================================================================
# CONDITIONS
# ===========================================================================

mission(
    id="CON-01", ordre=3, theme="conditions", concepts=["conditions", "types"], niveau=2,
    difficulte="facile", titre="Opération Habilitation",
    briefing=t("""À l'entrée du QG, le terminal lit le niveau d'habilitation de chaque visiteur et
        affiche la décision."""),
    objectif="Écrire une suite de conditions if / elif / else.",
    enonce=t("""Le niveau est lu avec input(). Affiche « ACCÈS TOTAL » si le niveau est au moins 5,
        « ACCÈS LIMITÉ » s'il est au moins 3, sinon « ACCÈS REFUSÉ »."""),
    donnees="Entrée : 4",
    resultat_attendu="ACCÈS LIMITÉ",
    code_depart=c('''
        niveau = int(input())   # le niveau lu par le terminal

        # Écris les conditions ici
    '''),
    tests=[
        sortie("ACCÈS LIMITÉ\n", "niveau 4", ["4"], visible=True),
        sortie("ACCÈS TOTAL\n", "niveau 5", ["5"]),
        sortie("ACCÈS TOTAL\n", "niveau 9", ["9"]),
        sortie("ACCÈS LIMITÉ\n", "niveau 3", ["3"]),
        sortie("ACCÈS REFUSÉ\n", "niveau 2", ["2"]),
        sortie("ACCÈS REFUSÉ\n", "niveau 0", ["0"]),
    ],
    indices=[
        "Combien de cas différents y a-t-il ? Dans quel ordre faut-il les tester ?",
        "« au moins 5 » s'écrit niveau >= 5. if teste le premier cas, elif les suivants, else le reste.",
        "Exemple :\ntemperature = 25\nif temperature >= 30:\n    print(\"Chaud\")\nelif temperature >= 15:\n"
        "    print(\"Doux\")\nelse:\n    print(\"Froid\")",
    ],
    solution=c('''
        niveau = int(input())   # le niveau lu par le terminal

        if niveau >= 5:
            print("ACCÈS TOTAL")
        elif niveau >= 3:
            print("ACCÈS LIMITÉ")
        else:
            print("ACCÈS REFUSÉ")
    '''),
    explication=t("""Python teste les conditions de haut en bas et exécute seulement le PREMIER bloc dont
        la condition est vraie. C'est pourquoi on teste d'abord le cas le plus exigeant (>= 5). Pour
        tester ce programme dans l'application, écris une valeur dans la zone « Entrées »."""),
)

mission(
    id="CON-02", ordre=8, theme="conditions", concepts=["conditions", "fonctions"], niveau=3,
    difficulte="facile", titre="Opération Contrôle d'Accès", revision_pour=["egalite_affectation"],
    briefing=t("""Le sas du laboratoire s'ouvre seulement si le badge est « ALPHA » ET si le code vaut
        7351. Un stagiaire a commencé la fonction… et Python refuse de la lancer."""),
    objectif="Différencier = (ranger) et == (comparer), et combiner deux conditions avec and.",
    enonce=t("""Complète verifier_acces(badge, code) : elle renvoie True si badge vaut "ALPHA" et code
        vaut 7351, sinon False. Attention : Python distingue majuscules et minuscules."""),
    donnees='verifier_acces("ALPHA", 7351)',
    resultat_attendu="True",
    code_depart=c('''
        def verifier_acces(badge, code):
            """Renvoie True si le badge est "ALPHA" ET le code vaut 7351."""
            if badge = "ALPHA":   # ← Python refuse cette ligne. Pourquoi ?
                ...
            return False
    '''),
    tests=[
        appel("verifier_acces", ["ALPHA", 7351], True, "bon badge, bon code", True),
        appel("verifier_acces", ["ALPHA", 1234], False, "mauvais code", True),
        appel("verifier_acces", ["BETA", 7351], False, "mauvais badge"),
        appel("verifier_acces", ["alpha", 7351], False, "badge en minuscules"),
    ],
    indices=[
        "Dans une condition, veux-tu RANGER une valeur ou COMPARER deux valeurs ?",
        "== compare deux valeurs. and combine deux conditions : les deux doivent être vraies.",
        "Exemple :\nif ville == \"Berne\" and jour == 3:\n    return True\nreturn False",
    ],
    solution=c('''
        def verifier_acces(badge, code):
            """Renvoie True si le badge est "ALPHA" ET le code vaut 7351."""
            if badge == "ALPHA" and code == 7351:
                return True
            return False
    '''),
    explication=t("""= range une valeur dans une variable ; == pose une question (« est-ce égal ? ») et
        donne True ou False. Avec and, les deux conditions doivent être vraies. On peut même écrire
        directement : return badge == "ALPHA" and code == 7351."""),
)

mission(
    id="CON-03", ordre=16, theme="conditions", concepts=["conditions", "fonctions"], niveau=4,
    difficulte="intermediaire", titre="Opération Météo de Mission",
    briefing=t("""Avant chaque saut en parachute, le centre calcule un niveau d'alerte selon le vent
        (km/h) et la visibilité (mètres)."""),
    objectif="Combiner plusieurs conditions avec or dans une chaîne if / elif / else.",
    enonce=t("""Écris niveau_alerte(vent, visibilite) qui renvoie "rouge" si vent > 80 ou
        visibilite < 100 ; "orange" si vent > 50 ou visibilite < 500 ; sinon "vert"."""),
    donnees="niveau_alerte(60, 1000)",
    resultat_attendu='"orange"',
    code_depart="def niveau_alerte(vent, visibilite):\n    pass\n",
    tests=[
        appel("niveau_alerte", [60, 1000], "orange", "vent moyen", True),
        appel("niveau_alerte", [20, 2000], "vert", "beau temps", True),
        appel("niveau_alerte", [90, 2000], "rouge", "tempête"),
        appel("niveau_alerte", [10, 50], "rouge", "brouillard épais"),
        appel("niveau_alerte", [80, 500], "orange", "limites exactes (80 et 500)"),
        appel("niveau_alerte", [50, 499], "orange", "visibilité réduite"),
        appel("niveau_alerte", [50, 500], "vert", "pile aux limites orange"),
    ],
    indices=[
        "Quel niveau faut-il tester en premier : le plus grave ou le moins grave ? Pourquoi ?",
        "or : il suffit qu'UNE des deux conditions soit vraie. Teste « rouge » d'abord, puis « orange ».",
        "Exemple :\nif pluie > 50 or vent > 70:\n    return \"annulé\"\nelif pluie > 10:\n    return \"prudence\"\n"
        "return \"ok\"\nVérifie bien > ou >= selon l'énoncé.",
    ],
    solution=c('''
        def niveau_alerte(vent, visibilite):
            """Renvoie le niveau d'alerte : "rouge", "orange" ou "vert"."""
            if vent > 80 or visibilite < 100:
                return "rouge"
            elif vent > 50 or visibilite < 500:
                return "orange"
            else:
                return "vert"
    '''),
    explication=t("""On teste du plus grave au moins grave : une situation « rouge » vérifie aussi les
        conditions « orange », donc l'ordre compte. Les tests « limites exactes » vérifient la différence
        entre > et >=, source d'erreurs très fréquente."""),
)

mission(
    id="CON-04", ordre=26, theme="conditions", concepts=["conditions", "fonctions"], niveau=4,
    difficulte="intermediaire", titre="Opération Calendrier",
    briefing=t("""Le chiffrement du jour dépend du calendrier : les années bissextiles utilisent une
        clé différente. Il faut les reconnaître sans erreur."""),
    objectif="Traduire une règle en conditions avec le modulo %.",
    enonce=t("""Écris est_bissextile(annee). Une année est bissextile si elle est divisible par 4,
        SAUF si elle est divisible par 100 ; mais elle l'est quand même si elle est divisible par 400."""),
    donnees="est_bissextile(2024)",
    resultat_attendu="True",
    code_depart="def est_bissextile(annee):\n    pass\n",
    tests=[
        appel("est_bissextile", [2024], True, "2024", True),
        appel("est_bissextile", [2023], False, "2023", True),
        appel("est_bissextile", [1900], False, "1900 (divisible par 100)"),
        appel("est_bissextile", [2000], True, "2000 (divisible par 400)"),
        appel("est_bissextile", [2100], False, "2100"),
        appel("est_bissextile", [1996], True, "1996"),
    ],
    indices=[
        "Comment savoir si un nombre est divisible par 4 ? Que vaut le reste de la division ?",
        "annee % 4 == 0 signifie « divisible par 4 ». Commence par tester le cas le plus particulier (400).",
        "Structure possible :\nif annee % 400 == 0:\n    return True\nif annee % 100 == 0:\n    return ...\n"
        "return annee % 4 == 0",
    ],
    solution=c('''
        def est_bissextile(annee):
            """Renvoie True si l'année est bissextile."""
            if annee % 400 == 0:
                return True
            if annee % 100 == 0:
                return False
            return annee % 4 == 0
    '''),
    explication=t("""Quand une règle a des exceptions, on traite d'abord le cas le plus particulier
        (400), puis l'exception (100), puis la règle générale (4). Chaque return arrête la fonction :
        les tests suivants ne sont faits que si nécessaire."""),
)

# ===========================================================================
# BOUCLES
# ===========================================================================

mission(
    id="BOU-01", ordre=4, theme="boucles", concepts=["boucle-for"], niveau=2,
    difficulte="facile", titre="Opération Compte à Rebours",
    briefing="Le lanceur du drone attend le signal. Affiche le compte à rebours réglementaire.",
    objectif="Répéter une instruction avec une boucle for et range().",
    enonce=t("""Affiche les nombres 5, 4, 3, 2, 1 (un par ligne) puis « Mise à feu ! ».
        Utilise une boucle plutôt que cinq print()."""),
    donnees="Aucune donnée",
    resultat_attendu="5\n4\n3\n2\n1\nMise à feu !",
    code_depart="# Utilise une boucle for avec range()\n",
    tests=[
        sortie("5\n4\n3\n2\n1\nMise à feu !\n", "compte à rebours", visible=True),
        structure("utilise une boucle", doit_utiliser=["for"]),
    ],
    indices=[
        "range(début, fin, pas) peut-il compter à l'envers ?",
        "range(5, 0, -1) donne 5, 4, 3, 2, 1 : la fin (0) est EXCLUE. Le dernier print se place APRÈS la boucle.",
        "Exemple (de 3 à 1) :\nfor i in range(3, 0, -1):\n    print(i)\nprint(\"Fin\")   # pas indenté : hors de la boucle",
    ],
    solution=c('''
        for seconde in range(5, 0, -1):
            print(seconde)
        print("Mise à feu !")
    '''),
    explication=t("""range(5, 0, -1) part de 5, descend de 1 à chaque tour et s'arrête AVANT 0.
        L'indentation décide de ce qui est répété : le print final n'est pas indenté, il s'exécute une
        seule fois après la boucle."""),
)

mission(
    id="BOU-02", ordre=9, theme="boucles", concepts=["boucle-for", "listes"], niveau=3,
    difficulte="facile", titre="Opération Inventaire",
    briefing=t("""L'armurerie a reçu plusieurs caisses. Le registre doit indiquer le nombre total
        d'objets, calculé caisse par caisse."""),
    objectif="Utiliser un accumulateur dans une boucle for.",
    enonce=t("""Complète somme_codes(codes) pour qu'elle renvoie la somme des nombres de la liste.
        Utilise une boucle (sum() est interdit pour cette mission)."""),
    donnees="somme_codes([3, 8, 12])",
    resultat_attendu="23",
    code_depart=c('''
        def somme_codes(codes):
            """Renvoie la somme des nombres de la liste."""
            total = 0
            for code in codes:
                ...   # ajoute code au total
            return total
    '''),
    tests=[
        appel("somme_codes", [[3, 8, 12]], 23, "exemple", True),
        appel("somme_codes", [[]], 0, "liste vide"),
        appel("somme_codes", [[-5, 5]], 0, "positifs et négatifs"),
        appel("somme_codes", [[100]], 100, "une seule caisse"),
        structure("sans sum()", interdit=["sum"]),
    ],
    indices=[
        "À chaque tour de boucle, que doit devenir total ?",
        "total = total + code (ou total += code) ajoute la valeur courante au total.",
        "Exemple (compter des éléments) :\nnombre = 0\nfor x in liste:\n    nombre += 1",
    ],
    solution=c('''
        def somme_codes(codes):
            """Renvoie la somme des nombres de la liste."""
            total = 0
            for code in codes:
                total += code
            return total
    '''),
    explication=t("""C'est le schéma de l'accumulateur : une variable initialisée AVANT la boucle,
        mise à jour PENDANT, utilisée APRÈS. Il sert à sommer, compter, concaténer…"""),
)

mission(
    id="BOU-03", ordre=19, theme="boucles", concepts=["boucle-for", "conditions", "fonctions"], niveau=4,
    difficulte="intermediaire", titre="Opération Coffre-Fort",
    briefing=t("""Le coffre ennemi se bloque après un certain nombre d'essais. Notre robot teste des
        codes dans l'ordre : réussira-t-il avant le blocage ?"""),
    objectif="Parcourir une liste et s'arrêter dès qu'une condition est remplie.",
    enonce=t("""Écris ouvrir_coffre(essais, code_correct, max_essais) qui renvoie "OUVERT" si le code
        correct apparaît parmi les max_essais premiers essais, sinon "BLOQUÉ"."""),
    donnees="ouvrir_coffre([1111, 2580, 7351], 2580, 2)",
    resultat_attendu='"OUVERT"',
    code_depart="def ouvrir_coffre(essais, code_correct, max_essais):\n    pass\n",
    tests=[
        appel("ouvrir_coffre", [[1111, 2580, 7351], 2580, 2], "OUVERT", "trouvé au 2e essai", True),
        appel("ouvrir_coffre", [[1111, 2580, 7351], 7351, 2], "BLOQUÉ", "trouvé trop tard", True),
        appel("ouvrir_coffre", [[4242], 4242, 1], "OUVERT", "premier essai"),
        appel("ouvrir_coffre", [[], 1234, 3], "BLOQUÉ", "aucun essai"),
        appel("ouvrir_coffre", [[1, 2], 9, 5], "BLOQUÉ", "max_essais plus grand que la liste"),
    ],
    indices=[
        "Combien d'essais faut-il réellement regarder ? Attention si la liste est plus courte que max_essais.",
        "essais[:max_essais] donne les max_essais premiers éléments (sans erreur si la liste est plus courte). "
        "Un return dans la boucle arrête tout dès que le code est trouvé.",
        "Exemple :\nfor mot in mots[:3]:\n    if mot == \"stop\":\n        return \"trouvé\"\nreturn \"absent\"",
    ],
    solution=c('''
        def ouvrir_coffre(essais, code_correct, max_essais):
            """Renvoie "OUVERT" si le code est trouvé avant le blocage, sinon "BLOQUÉ"."""
            for essai in essais[:max_essais]:
                if essai == code_correct:
                    return "OUVERT"
            return "BLOQUÉ"
    '''),
    explication=t("""Le découpage essais[:max_essais] limite la boucle sans risque d'IndexError. Le
        return "OUVERT" à l'intérieur de la boucle arrête la recherche ; le return "BLOQUÉ" n'est atteint
        que si la boucle s'est terminée sans succès."""),
)

mission(
    id="BOU-04", ordre=32, theme="boucles", concepts=["boucle-for", "listes", "variables"], niveau=5,
    difficulte="difficile", titre="Opération Fibonacci",
    briefing=t("""La clé de chiffrement de cette semaine suit la suite de Fibonacci : chaque nombre est
        la somme des deux précédents (0, 1, 1, 2, 3, 5, 8…)."""),
    objectif="Faire évoluer plusieurs variables à chaque tour de boucle.",
    enonce=t("""Écris cle_fibonacci(n) qui renvoie la liste des n premiers nombres de la suite,
        en commençant par 0 et 1. Pour n = 0, renvoie une liste vide."""),
    donnees="cle_fibonacci(7)",
    resultat_attendu="[0, 1, 1, 2, 3, 5, 8]",
    code_depart="def cle_fibonacci(n):\n    pass\n",
    tests=[
        appel("cle_fibonacci", [7], [0, 1, 1, 2, 3, 5, 8], "7 nombres", True),
        appel("cle_fibonacci", [0], [], "n = 0"),
        appel("cle_fibonacci", [1], [0], "n = 1"),
        appel("cle_fibonacci", [2], [0, 1], "n = 2"),
        appel("cle_fibonacci", [12], [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89], "12 nombres"),
    ],
    indices=[
        "De quelles informations as-tu besoin pour calculer le nombre suivant ?",
        "Garde deux variables a et b (les deux derniers nombres). À chaque tour : ajoute a au résultat, "
        "puis avance : a, b = b, a + b.",
        "Squelette :\nresultat = []\na, b = 0, 1\nfor _ in range(n):\n    resultat.append(a)\n    a, b = b, a + b\nreturn resultat",
    ],
    solution=c('''
        def cle_fibonacci(n):
            """Renvoie les n premiers nombres de la suite de Fibonacci."""
            suite = []
            precedent, actuel = 0, 1
            for _ in range(n):
                suite.append(precedent)
                precedent, actuel = actuel, precedent + actuel
            return suite
    '''),
    explication=t("""L'affectation multiple a, b = b, a + b calcule d'abord toute la partie droite,
        puis range les résultats : elle évite une variable temporaire. Le nom _ indique qu'on n'utilise
        pas le compteur de la boucle."""),
)

mission(
    id="BOU-05", ordre=18, theme="boucles", concepts=["boucle-while", "variables"], niveau=4,
    difficulte="intermediaire", titre="Opération Patrouille",
    briefing=t("""Le véhicule de patrouille consomme du carburant chaque jour. Combien de jours
        complets peut-il rouler avant de devoir rentrer ?"""),
    objectif="Utiliser une boucle while dont la condition change à chaque tour.",
    enonce=t("""Écris jours_de_patrouille(carburant, consommation) qui renvoie le nombre de jours
        complets possibles : tant qu'il reste assez de carburant pour une journée, on roule.
        Utilise une boucle while."""),
    donnees="jours_de_patrouille(100, 30)",
    resultat_attendu="3",
    code_depart="def jours_de_patrouille(carburant, consommation):\n    pass\n",
    tests=[
        appel("jours_de_patrouille", [100, 30], 3, "exemple", True),
        appel("jours_de_patrouille", [90, 30], 3, "pile assez"),
        appel("jours_de_patrouille", [10, 30], 0, "pas assez pour un jour"),
        appel("jours_de_patrouille", [0, 5], 0, "réservoir vide"),
        structure("utilise une boucle while", doit_utiliser=["while"]),
    ],
    indices=[
        "Quelle condition doit être vraie pour rouler un jour de plus ?",
        "while carburant >= consommation: … À l'intérieur, enlève la consommation et compte un jour. "
        "Si la condition ne change jamais, la boucle est infinie.",
        "Exemple :\nsolde = 50\nachats = 0\nwhile solde >= 20:\n    solde -= 20\n    achats += 1",
    ],
    solution=c('''
        def jours_de_patrouille(carburant, consommation):
            """Renvoie le nombre de jours complets possibles."""
            jours = 0
            while carburant >= consommation:
                carburant -= consommation
                jours += 1
            return jours
    '''),
    explication=t("""while répète tant que la condition est vraie. On ne connaît pas à l'avance le
        nombre de tours : c'est le cas typique du while. La ligne carburant -= consommation garantit
        que la boucle finira par s'arrêter."""),
)

# ===========================================================================
# LISTES
# ===========================================================================

mission(
    id="LIS-01", ordre=10, theme="listes", concepts=["listes", "conditions"], niveau=3,
    difficulte="facile", titre="Opération Dernier Contact", revision_pour=["index"],
    briefing=t("""Le journal des contacts est une liste. Le chef veut toujours le DERNIER contact
        enregistré… mais le journal est parfois vide."""),
    objectif="Comprendre les indices d'une liste (le premier est 0, le dernier est len - 1 ou -1).",
    enonce=t("""Corrige et complète dernier_element(liste) : elle renvoie le dernier élément de la liste,
        ou None si la liste est vide."""),
    donnees='dernier_element(["Lynx", "Orion", "Vega"])',
    resultat_attendu='"Vega"',
    code_depart=c('''
        def dernier_element(liste):
            """Renvoie le dernier élément, ou None si la liste est vide."""
            return liste[len(liste)]
    '''),
    tests=[
        appel("dernier_element", [["Lynx", "Orion", "Vega"]], "Vega", "trois contacts", True),
        appel("dernier_element", [["Sphinx"]], "Sphinx", "un seul contact"),
        appel("dernier_element", [[]], None, "journal vide"),
        appel("dernier_element", [[4, 8, 15, 16]], 16, "nombres"),
    ],
    indices=[
        "Une liste de 3 éléments : quels sont ses indices valides ?",
        "Les indices vont de 0 à len(liste) - 1. liste[-1] donne aussi le dernier élément. "
        "Une liste vide n'a AUCUN élément : il faut la traiter à part.",
        "Exemple :\nif len(villes) == 0:\n    return None\nreturn villes[-1]",
    ],
    solution=c('''
        def dernier_element(liste):
            """Renvoie le dernier élément, ou None si la liste est vide."""
            if not liste:
                return None
            return liste[-1]
    '''),
    explication=t("""Dans une liste de longueur n, les indices vont de 0 à n - 1 : liste[len(liste)]
        est toujours hors limites (IndexError). L'indice -1 désigne le dernier élément. « if not liste »
        est vrai quand la liste est vide."""),
)

mission(
    id="LIS-02", ordre=17, theme="listes", concepts=["listes", "boucle-for", "conditions"], niveau=4,
    difficulte="intermediaire", titre="Opération Liste Noire", demo=True, elements="noms",
    briefing=t("""Une liste de noms a été interceptée. Certains noms apparaissent plusieurs fois.
        L'agence a besoin d'une liste nettoyée contenant chaque nom une seule fois."""),
    objectif=t("""Créer une fonction supprimer_doublons(noms) qui renvoie une liste sans doublons tout en
        conservant l'ordre initial."""),
    enonce=t("""Écris supprimer_doublons(noms) qui renvoie une NOUVELLE liste sans doublons, dans l'ordre
        de première apparition. La liste d'origine ne doit pas être modifiée."""),
    donnees='noms = ["Ivanov", "Smith", "Ivanov", "Dupont", "Smith", "Mori"]',
    resultat_attendu='["Ivanov", "Smith", "Dupont", "Mori"]',
    code_depart=c('''
        def supprimer_doublons(noms):
            """Renvoie la liste des noms sans doublons, dans l'ordre d'origine."""
            # 1. Crée une liste vide pour le résultat
            # 2. Parcours les noms
            # 3. Ajoute un nom seulement s'il n'est pas déjà dans le résultat
            # 4. Renvoie le résultat
            pass
    '''),
    tests=[
        appel("supprimer_doublons", [["Ivanov", "Smith", "Ivanov", "Dupont", "Smith", "Mori"]],
              ["Ivanov", "Smith", "Dupont", "Mori"], "liste interceptée", True, verifier_non_modifie=True),
        appel("supprimer_doublons", [[]], [], "liste vide"),
        appel("supprimer_doublons", [["Kane", "Kane", "Kane"]], ["Kane"], "toujours le même nom"),
        appel("supprimer_doublons", [["A", "B", "C"]], ["A", "B", "C"], "aucun doublon"),
        appel("supprimer_doublons", [["Lynx", "lynx", "Lynx"]], ["Lynx", "lynx"], "majuscules différentes"),
        appel("supprimer_doublons", [["Z", "A", "Z", "B", "A"]], ["Z", "A", "B"], "ordre d'origine conservé",
              verifier_non_modifie=True),
    ],
    indices=[
        "Comment savoir si un nom a DÉJÀ été ajouté au résultat ?",
        "Le mot-clé in teste la présence : « if nom not in resultat: ». set() supprime aussi les doublons, "
        "mais il ne garde pas l'ordre : ici, ce n'est pas la bonne piste.",
        "Exemple (garder les nombres pairs) :\nresultat = []\nfor n in nombres:\n    if n % 2 == 0:\n"
        "        resultat.append(n)\nreturn resultat\nIci, la condition porte sur la présence dans le résultat.",
    ],
    solution=c('''
        def supprimer_doublons(noms):
            """Renvoie la liste des noms sans doublons, dans l'ordre d'origine."""
            uniques = []
            for nom in noms:
                if nom not in uniques:
                    uniques.append(nom)
            return uniques
    '''),
    explication=t("""On construit une nouvelle liste et on n'y ajoute un nom que s'il n'y est pas encore
        (not in). L'ordre est conservé car on parcourt la liste d'origine du début à la fin. list(set(noms))
        semble plus court, mais un set ne garde pas l'ordre : les tests l'auraient détecté."""),
)

mission(
    id="LIS-03", ordre=28, theme="listes", concepts=["listes", "conditions", "boucle-for"], niveau=5,
    difficulte="intermediaire", titre="Opération Suspects Majeurs", elements="suspects",
    briefing=t("""Le témoin décrit un suspect « entre 25 et 40 ans ». Filtre la base de données pour ne
        garder que les suspects correspondant à cette tranche d'âge."""),
    objectif="Parcourir une liste de listes et combiner deux conditions.",
    enonce=t("""Écris suspects_dans_tranche(suspects, age_min, age_max). Chaque suspect est une liste
        [nom, age]. Renvoie la liste des noms dont l'âge est compris entre age_min et age_max
        (bornes incluses), dans l'ordre d'origine."""),
    donnees='suspects = [["Ivan", 34], ["Lea", 22], ["Marc", 40], ["Ana", 41], ["Tom", 25]]',
    resultat_attendu='["Ivan", "Marc", "Tom"]',
    code_depart="def suspects_dans_tranche(suspects, age_min, age_max):\n    pass\n",
    tests=[
        appel("suspects_dans_tranche",
              [[["Ivan", 34], ["Lea", 22], ["Marc", 40], ["Ana", 41], ["Tom", 25]], 25, 40],
              ["Ivan", "Marc", "Tom"], "exemple", True),
        appel("suspects_dans_tranche", [[], 20, 30], [], "base vide"),
        appel("suspects_dans_tranche", [[["Zoe", 19], ["Max", 60]], 20, 30], [], "personne dans la tranche"),
        appel("suspects_dans_tranche", [[["Kim", 30], ["Raj", 30]], 30, 30], ["Kim", "Raj"], "tranche d'un an"),
    ],
    indices=[
        "Pour chaque suspect, quelles sont les DEUX conditions à vérifier ?",
        "suspect[0] est le nom, suspect[1] l'âge. « Bornes incluses » : utilise <= et >=. "
        "Python accepte aussi age_min <= age <= age_max.",
        "Exemple :\nfor produit in stock:\n    prix = produit[1]\n    if 10 <= prix <= 20:\n        selection.append(produit[0])",
    ],
    solution=c('''
        def suspects_dans_tranche(suspects, age_min, age_max):
            """Renvoie les noms des suspects dont l'âge est dans la tranche (bornes incluses)."""
            selection = []
            for nom, age in suspects:
                if age_min <= age <= age_max:
                    selection.append(nom)
            return selection
    '''),
    explication=t("""« for nom, age in suspects » déballe directement chaque petite liste en deux
        variables. La comparaison chaînée age_min <= age <= age_max équivaut à
        age >= age_min and age <= age_max."""),
)

mission(
    id="LIS-04", ordre=29, theme="listes", concepts=["listes", "tuples", "fonctions"], niveau=5,
    difficulte="intermediaire", titre="Opération Coordonnées de la Cible",
    briefing=t("""Plusieurs drones ont repéré la cible à des positions légèrement différentes. Pour
        viser juste, on prend le centre : la moyenne des x et la moyenne des y."""),
    objectif="Parcourir une liste de tuples et calculer deux moyennes.",
    enonce=t("""Écris centre_cible(points) : points est une liste de tuples (x, y). Renvoie le tuple
        (moyenne des x, moyenne des y), chaque valeur arrondie à 2 décimales avec round(valeur, 2).
        La liste contient toujours au moins un point."""),
    donnees="points = [(2, 4), (4, 8), (6, 3)]",
    resultat_attendu="(4.0, 5.0)",
    code_depart="def centre_cible(points):\n    pass\n",
    tests=[
        appel("centre_cible", [[tup(2, 4), tup(4, 8), tup(6, 3)]], tup(4.0, 5.0), "trois drones", True,
              tolerance=0.01),
        appel("centre_cible", [[tup(1.5, 2.5)]], tup(1.5, 2.5), "un seul drone", tolerance=0.01),
        appel("centre_cible", [[tup(0, 0), tup(1, 0), tup(0, 1)]], tup(0.33, 0.33), "arrondi", tolerance=0.01),
        appel("centre_cible", [[tup(-3, 7), tup(3, -7)]], tup(0.0, 0.0), "valeurs négatives", tolerance=0.01),
    ],
    indices=[
        "Une moyenne = somme ÷ nombre. Combien de sommes dois-tu calculer ?",
        "Deux accumulateurs : somme_x et somme_y. Dans la boucle, « for x, y in points: » donne directement "
        "les deux coordonnées.",
        "Exemple :\ntotal_a = 0\ntotal_b = 0\nfor a, b in paires:\n    total_a += a\n    total_b += b\n"
        "return (round(total_a / len(paires), 2), round(total_b / len(paires), 2))",
    ],
    solution=c('''
        def centre_cible(points):
            """Renvoie (moyenne des x, moyenne des y), arrondies à 2 décimales."""
            somme_x = 0
            somme_y = 0
            for x, y in points:
                somme_x += x
                somme_y += y
            nombre = len(points)
            return (round(somme_x / nombre, 2), round(somme_y / nombre, 2))
    '''),
    explication=t("""Un tuple regroupe des valeurs qui vont ensemble (ici x et y). On peut le
        « déballer » dans la boucle : for x, y in points. Renvoyer un tuple permet de renvoyer les deux
        moyennes en une seule fois."""),
)

mission(
    id="LIS-05", ordre=35, theme="listes", concepts=["listes", "fonctions"], niveau=6,
    difficulte="difficile", titre="Opération Top Menaces", elements="scores",
    briefing=t("""Le rapport du matin ne doit contenir que les n menaces les plus élevées, de la plus
        forte à la plus faible. Attention : la liste originale sert à d'autres services, elle ne doit
        surtout pas être modifiée."""),
    objectif="Trier sans modifier l'original et découper une liste.",
    enonce=t("""Écris top_menaces(scores, n) qui renvoie une nouvelle liste contenant les n plus grands
        scores, triés du plus grand au plus petit. Si n dépasse la taille de la liste, renvoie tous les
        scores triés. La liste scores ne doit pas être modifiée."""),
    donnees="top_menaces([40, 95, 12, 77, 60], 3)",
    resultat_attendu="[95, 77, 60]",
    code_depart="def top_menaces(scores, n):\n    pass\n",
    tests=[
        appel("top_menaces", [[40, 95, 12, 77, 60], 3], [95, 77, 60], "top 3", True, verifier_non_modifie=True),
        appel("top_menaces", [[5, 1, 9], 10], [9, 5, 1], "n plus grand que la liste", verifier_non_modifie=True),
        appel("top_menaces", [[8, 3], 0], [], "n = 0"),
        appel("top_menaces", [[], 2], [], "aucune menace"),
        appel("top_menaces", [[50, 50, 20], 2], [50, 50], "égalités", verifier_non_modifie=True),
    ],
    indices=[
        "Quelle est la différence entre liste.sort() et sorted(liste) ?",
        "sorted(scores, reverse=True) renvoie une NOUVELLE liste triée du plus grand au plus petit. "
        "Le découpage liste[:n] garde les n premiers éléments (sans erreur si n est trop grand).",
        "Exemple :\nnotes = [12, 18, 9]\nmeilleures = sorted(notes, reverse=True)[:2]   # [18, 12]\n# notes vaut toujours [12, 18, 9]",
    ],
    solution=c('''
        def top_menaces(scores, n):
            """Renvoie les n plus grands scores, du plus grand au plus petit."""
            tries = sorted(scores, reverse=True)
            return tries[:n]
    '''),
    explication=t("""scores.sort() trie la liste ORIGINALE (et renvoie None) ; sorted(scores) crée une
        copie triée. Le découpage [:n] est tolérant : si n dépasse la longueur, il renvoie toute la liste,
        sans IndexError."""),
)

# ===========================================================================
# DICTIONNAIRES
# ===========================================================================

mission(
    id="DIC-01", ordre=6, theme="dictionnaires", concepts=["dictionnaires", "variables"], niveau=2,
    difficulte="facile", titre="Opération Annuaire des Bases",
    briefing=t("""Le registre des bases associe chaque agent à sa ville. Deux mises à jour viennent
        d'arriver du QG."""),
    objectif="Ajouter, modifier et lire une entrée d'un dictionnaire.",
    enonce=t("""1) Ajoute l'agent "Orion" basé à "Neuchâtel". 2) "Lynx" a déménagé : sa base devient
        "Zurich". 3) Affiche la base d'Orion en lisant le dictionnaire."""),
    donnees='bases = {"Faucon": "Genève", "Lynx": "Berne"}',
    resultat_attendu="Neuchâtel",
    code_depart=c('''
        bases = {"Faucon": "Genève", "Lynx": "Berne"}

        # 1. Ajoute Orion

        # 2. Modifie la base de Lynx

        # 3. Affiche la base d'Orion
    '''),
    tests=[
        variable("bases", {"Faucon": "Genève", "Lynx": "Zurich", "Orion": "Neuchâtel"}, "contenu du registre"),
        sortie("Neuchâtel\n", "affichage", visible=True),
    ],
    indices=[
        "Comment accède-t-on à la valeur associée à une clé dans un dictionnaire ?",
        "dico[cle] = valeur ajoute une clé (ou modifie sa valeur si elle existe déjà). dico[cle] seul lit la valeur.",
        "Exemple :\nscores = {\"Iris\": 10}\nscores[\"Nova\"] = 7     # ajout\nscores[\"Iris\"] = 12    # modification\nprint(scores[\"Nova\"])",
    ],
    solution=c('''
        bases = {"Faucon": "Genève", "Lynx": "Berne"}

        bases["Orion"] = "Neuchâtel"
        bases["Lynx"] = "Zurich"
        print(bases["Orion"])
    '''),
    explication=t("""Un dictionnaire associe des clés à des valeurs. La même écriture dico[cle] = valeur
        sert à ajouter ou à modifier : si la clé existe déjà, l'ancienne valeur est remplacée."""),
)

mission(
    id="DIC-02", ordre=12, theme="dictionnaires", concepts=["dictionnaires", "conditions"], niveau=3,
    difficulte="facile", titre="Opération Base Introuvable", revision_pour=["cle"],
    briefing=t("""Le système de localisation plante dès qu'on cherche un agent absent du registre.
        Inacceptable en pleine opération."""),
    objectif="Lire un dictionnaire sans provoquer de KeyError.",
    enonce=t("""Corrige ville_agent(annuaire, nom) : elle renvoie la ville de l'agent, ou "INCONNU"
        si l'agent n'est pas dans l'annuaire."""),
    donnees='annuaire = {"Faucon": "Genève", "Lynx": "Berne"}',
    resultat_attendu='ville_agent(annuaire, "Cobra") → "INCONNU"',
    code_depart=c('''
        def ville_agent(annuaire, nom):
            """Renvoie la ville de l'agent, ou "INCONNU"."""
            return annuaire[nom]
    '''),
    tests=[
        appel("ville_agent", [{"Faucon": "Genève", "Lynx": "Berne"}, "Lynx"], "Berne", "agent connu", True),
        appel("ville_agent", [{"Faucon": "Genève", "Lynx": "Berne"}, "Cobra"], "INCONNU", "agent absent", True),
        appel("ville_agent", [{}, "Lynx"], "INCONNU", "annuaire vide"),
        appel("ville_agent", [{"Faucon": "Genève"}, "faucon"], "INCONNU", "minuscule"),
    ],
    indices=[
        "Que fait Python quand on demande une clé qui n'existe pas ?",
        "« if nom in annuaire: » vérifie la présence d'une clé. La méthode get() le fait en une ligne.",
        "Exemple :\nstock = {\"pommes\": 3}\nprint(stock.get(\"poires\", 0))   # 0, sans erreur",
    ],
    solution=c('''
        def ville_agent(annuaire, nom):
            """Renvoie la ville de l'agent, ou "INCONNU"."""
            if nom in annuaire:
                return annuaire[nom]
            return "INCONNU"
    '''),
    explication=t("""annuaire[nom] lève KeyError si la clé manque. Deux solutions propres : tester avec
        « in » avant de lire, ou utiliser annuaire.get(nom, "INCONNU") qui renvoie la valeur par
        défaut."""),
)

mission(
    id="DIC-03", ordre=21, theme="dictionnaires", concepts=["dictionnaires", "chaines", "boucle-for"], niveau=4,
    difficulte="intermediaire", titre="Opération Mots-Clés",
    briefing=t("""Les analystes cherchent les mots qui reviennent le plus dans les messages interceptés.
        Il faut compter chaque mot."""),
    objectif="Compter des occurrences avec un dictionnaire.",
    enonce=t("""Écris compter_mots(texte) qui renvoie un dictionnaire {mot: nombre d'apparitions}.
        Les mots sont séparés par des espaces et doivent être comptés en minuscules."""),
    donnees='compter_mots("Le colis le colis arrive")',
    resultat_attendu='{"le": 2, "colis": 2, "arrive": 1}',
    code_depart="def compter_mots(texte):\n    pass\n",
    tests=[
        appel("compter_mots", ["Le colis le colis arrive"], {"le": 2, "colis": 2, "arrive": 1}, "exemple", True),
        appel("compter_mots", [""], {}, "texte vide"),
        appel("compter_mots", ["ALERTE alerte Alerte"], {"alerte": 3}, "majuscules"),
        appel("compter_mots", ["un  deux"], {"un": 1, "deux": 1}, "double espace"),
    ],
    indices=[
        "Comment transformer le texte en liste de mots ? Que faire la première fois qu'on voit un mot ?",
        "texte.lower().split() découpe en mots (en ignorant les espaces multiples). "
        "compteur[mot] = compteur.get(mot, 0) + 1 crée ou augmente le compte.",
        "Exemple :\nfruits = [\"pomme\", \"kiwi\", \"pomme\"]\ncompte = {}\nfor f in fruits:\n    compte[f] = compte.get(f, 0) + 1",
    ],
    solution=c('''
        def compter_mots(texte):
            """Renvoie le nombre d'apparitions de chaque mot (en minuscules)."""
            compteur = {}
            for mot in texte.lower().split():
                compteur[mot] = compteur.get(mot, 0) + 1
            return compteur
    '''),
    explication=t("""split() sans argument découpe sur n'importe quelle suite d'espaces : le test
        « double espace » le vérifie (split(" ") aurait produit un mot vide). Le motif
        dico.get(cle, 0) + 1 est LA méthode classique pour compter."""),
)

mission(
    id="DIC-04", ordre=30, theme="dictionnaires", concepts=["dictionnaires", "listes", "boucle-for"], niveau=5,
    difficulte="intermediaire", titre="Opération Répartition",
    briefing=t("""Le QG veut savoir quels agents sont présents dans chaque ville pour organiser les
        rendez-vous."""),
    objectif="Construire un dictionnaire dont les valeurs sont des listes.",
    enonce=t("""Écris agents_par_ville(agents) : agents est une liste de dictionnaires
        {"nom": ..., "ville": ...}. Renvoie un dictionnaire {ville: [noms des agents]} en gardant
        l'ordre d'apparition."""),
    donnees=('agents = [{"nom": "Lynx", "ville": "Berne"}, {"nom": "Vega", "ville": "Genève"}, '
             '{"nom": "Orion", "ville": "Berne"}]'),
    resultat_attendu='{"Berne": ["Lynx", "Orion"], "Genève": ["Vega"]}',
    code_depart="def agents_par_ville(agents):\n    pass\n",
    tests=[
        appel("agents_par_ville", [[{"nom": "Lynx", "ville": "Berne"}, {"nom": "Vega", "ville": "Genève"},
                                    {"nom": "Orion", "ville": "Berne"}]],
              {"Berne": ["Lynx", "Orion"], "Genève": ["Vega"]}, "exemple", True),
        appel("agents_par_ville", [[]], {}, "aucun agent"),
        appel("agents_par_ville", [[{"nom": "Iris", "ville": "Oslo"}]], {"Oslo": ["Iris"]}, "un agent"),
    ],
    indices=[
        "Que faut-il faire la première fois qu'une ville apparaît ? Et les fois suivantes ?",
        "agent[\"ville\"] et agent[\"nom\"] lisent les informations. Si la ville n'est pas encore une clé, "
        "crée-la avec une liste vide, puis ajoute le nom avec append().",
        "Exemple :\ngroupes = {}\nfor eleve in eleves:\n    classe = eleve[\"classe\"]\n    if classe not in groupes:\n"
        "        groupes[classe] = []\n    groupes[classe].append(eleve[\"nom\"])",
    ],
    solution=c('''
        def agents_par_ville(agents):
            """Regroupe les noms des agents par ville."""
            repartition = {}
            for agent in agents:
                ville = agent["ville"]
                if ville not in repartition:
                    repartition[ville] = []
                repartition[ville].append(agent["nom"])
            return repartition
    '''),
    explication=t("""C'est le motif « regrouper » : une clé par catégorie, une liste de valeurs par clé.
        On crée la liste vide la première fois, puis on y ajoute les éléments. (Plus tard, tu
        découvriras dico.setdefault(ville, []) qui fait les deux en une ligne.)"""),
)

# ===========================================================================
# CHAÎNES DE CARACTÈRES
# ===========================================================================

mission(
    id="STR-01", ordre=5, theme="chaines", concepts=["chaines", "variables"], niveau=2,
    difficulte="facile", titre="Opération Miroir",
    briefing=t("""Le message a été écrit à l'envers pour tromper les curieux. Retourne-le pour le
        lire."""),
    objectif="Utiliser le découpage (slicing) d'une chaîne.",
    enonce=t("""Crée la variable message_decode contenant message à l'envers, puis affiche-la."""),
    donnees='message = "tiunim a erag al"',
    resultat_attendu="la gare a minuit",
    code_depart='message = "tiunim a erag al"\n\n# Crée message_decode, puis affiche-la\n',
    tests=[
        variable("message_decode", "la gare a minuit", "message décodé"),
        sortie("la gare a minuit\n", "affichage", visible=True),
    ],
    indices=[
        "Une chaîne se découpe comme une liste avec [début:fin:pas]. Que donnerait un pas négatif ?",
        "texte[::-1] parcourt le texte de la fin vers le début.",
        "Exemple :\nmot = \"radar\"\nprint(mot[::-1])\nprint(\"Python\"[::-1])   # nohtyP",
    ],
    solution='message = "tiunim a erag al"\n\nmessage_decode = message[::-1]\nprint(message_decode)\n',
    explication=t("""Le découpage [début:fin:pas] fonctionne sur les chaînes, les listes et les tuples.
        Sans début ni fin, et avec un pas de -1, on obtient une copie inversée. Les chaînes étant
        immuables, message n'est pas modifié : on crée une nouvelle chaîne."""),
)

mission(
    id="STR-02", ordre=13, theme="chaines", concepts=["chaines", "boucle-for", "listes"], niveau=3,
    difficulte="facile", titre="Opération Initiales",
    briefing=t("""Dans les rapports, les vrais noms sont remplacés par des initiales. Automatise la
        transformation."""),
    objectif="Découper une chaîne avec split() et construire un nouveau texte.",
    enonce=t("""Complète initiales(nom_complet) : elle renvoie la première lettre de chaque mot, en
        majuscule, suivie d'un point. "James Bond" → "J.B." """),
    donnees='initiales("James Bond")',
    resultat_attendu='"J.B."',
    code_depart=c('''
        def initiales(nom_complet):
            """Renvoie les initiales : "James Bond" → "J.B." """
            resultat = ""
            for mot in nom_complet.split():
                ...   # ajoute la première lettre en majuscule et un point
            return resultat
    '''),
    tests=[
        appel("initiales", ["James Bond"], "J.B.", "exemple", True),
        appel("initiales", ["ada lovelace"], "A.L.", "minuscules"),
        appel("initiales", ["Grace Brewster Hopper"], "G.B.H.", "trois mots"),
        appel("initiales", ["Mata"], "M.", "un seul mot"),
    ],
    indices=[
        "Comment obtenir la première lettre d'un mot ? Et la mettre en majuscule ?",
        "mot[0] est la première lettre ; mot[0].upper() la met en majuscule. On ajoute à resultat avec +=.",
        "Exemple :\nresultat = \"\"\nfor mot in [\"chat\", \"rat\"]:\n    resultat += mot[-1]   # dernières lettres\n# resultat vaut \"tt\"",
    ],
    solution=c('''
        def initiales(nom_complet):
            """Renvoie les initiales : "James Bond" → "J.B." """
            resultat = ""
            for mot in nom_complet.split():
                resultat += mot[0].upper() + "."
            return resultat
    '''),
    explication=t("""split() découpe un texte en liste de mots. On construit ensuite une nouvelle
        chaîne morceau par morceau avec +=. mot[0] fonctionne car chaque mot contient au moins une
        lettre (split() ne produit pas de mots vides)."""),
)

mission(
    id="STR-03", ordre=20, theme="chaines", concepts=["chaines", "conditions"], niveau=4,
    difficulte="intermediaire", titre="Opération Palindrome",
    briefing=t("""Les mots de passe de l'ennemi sont toujours des palindromes : des phrases qui se lisent
        pareil dans les deux sens (« Kayak »). Écris un détecteur."""),
    objectif="Nettoyer une chaîne puis la comparer à son inverse.",
    enonce=t("""Écris est_palindrome(phrase) qui renvoie True si la phrase se lit de la même façon dans
        les deux sens, en ignorant les espaces et les majuscules."""),
    donnees='est_palindrome("Esope reste ici et se repose")',
    resultat_attendu="True",
    code_depart="def est_palindrome(phrase):\n    pass\n",
    tests=[
        appel("est_palindrome", ["Kayak"], True, "Kayak", True),
        appel("est_palindrome", ["Esope reste ici et se repose"], True, "phrase avec espaces", True),
        appel("est_palindrome", ["agent"], False, "pas un palindrome"),
        appel("est_palindrome", [""], True, "phrase vide"),
        appel("est_palindrome", ["Radar  "], True, "espaces à la fin"),
    ],
    indices=[
        "Avant de comparer, quelles différences faut-il faire disparaître ?",
        "lower() met tout en minuscules ; replace(\" \", \"\") supprime les espaces. Ensuite, compare le texte "
        "avec son inverse texte[::-1].",
        "Exemple :\nmot = \"Elle\".lower()       # \"elle\"\nprint(mot == mot[::-1])   # True",
    ],
    solution=c('''
        def est_palindrome(phrase):
            """Renvoie True si la phrase est un palindrome (espaces et majuscules ignorés)."""
            nettoyee = phrase.lower().replace(" ", "")
            return nettoyee == nettoyee[::-1]
    '''),
    explication=t("""On découpe le problème en deux étapes : 1) normaliser (minuscules, sans espaces) ;
        2) comparer avec l'inverse. Une comparaison avec == donne déjà True ou False : inutile
        d'écrire if … return True else return False."""),
)

mission(
    id="STR-04", ordre=31, theme="chaines", concepts=["chaines", "boucle-for", "conditions"], niveau=5,
    difficulte="intermediaire", titre="Opération César",
    briefing=t("""Jules César décalait chaque lettre de 3 rangs dans l'alphabet. L'agence utilise encore
        cette méthode pour les messages de faible importance."""),
    objectif="Parcourir une chaîne et transformer chaque lettre avec sa position dans l'alphabet.",
    enonce=t("""Écris chiffrer_cesar(message, decalage) : chaque lettre minuscule avance de « decalage »
        rangs (après z, on revient à a). Les autres caractères (espaces, ponctuation…) ne changent pas."""),
    donnees='chiffrer_cesar("attaque a l aube", 3)',
    resultat_attendu='"dwwdtxh d o dxeh"',
    code_depart=c('''
        ALPHABET = "abcdefghijklmnopqrstuvwxyz"


        def chiffrer_cesar(message, decalage):
            pass
    '''),
    tests=[
        appel("chiffrer_cesar", ["attaque a l aube", 3], "dwwdtxh d o dxeh", "exemple", True),
        appel("chiffrer_cesar", ["xyz", 3], "abc", "retour au début"),
        appel("chiffrer_cesar", ["code: 42!", 1], "dpef: 42!", "ponctuation et chiffres"),
        appel("chiffrer_cesar", ["", 5], "", "message vide"),
        appel("chiffrer_cesar", ["abc", 26], "abc", "tour complet"),
    ],
    indices=[
        "Pour une lettre donnée, comment trouver sa position, puis la lettre décalée ?",
        "ALPHABET.index(lettre) donne la position (a → 0). (position + decalage) % 26 revient au début "
        "après z. Les caractères qui ne sont pas dans ALPHABET sont recopiés tels quels.",
        "Exemple (lettre suivante) :\nposition = ALPHABET.index(\"c\")          # 2\nsuivante = ALPHABET[(position + 1) % 26]  # \"d\"",
    ],
    solution=c('''
        ALPHABET = "abcdefghijklmnopqrstuvwxyz"


        def chiffrer_cesar(message, decalage):
            """Chiffre le message avec le code César."""
            resultat = ""
            for caractere in message:
                if caractere in ALPHABET:
                    position = (ALPHABET.index(caractere) + decalage) % len(ALPHABET)
                    resultat += ALPHABET[position]
                else:
                    resultat += caractere
            return resultat
    '''),
    explication=t("""Le modulo % fait « tourner » les positions : (25 + 3) % 26 = 2, donc z devient c.
        La constante ALPHABET, écrite en majuscules, indique une valeur qui ne change jamais : c'est
        une convention PEP 8."""),
)

# ===========================================================================
# FONCTIONS
# ===========================================================================

mission(
    id="FON-01", ordre=11, theme="fonctions", concepts=["print-return", "fonctions"], niveau=3,
    difficulte="facile", titre="Opération Print ou Return ?", revision_pour=["print_return", "retour_none"],
    briefing=t("""Le système automatique de l'agence appelle ta fonction et utilise le résultat pour
        ouvrir un sas. Il ne « voit » pas l'écran : une valeur seulement affichée est perdue pour lui."""),
    objectif="Comprendre la différence entre print() (afficher) et return (renvoyer).",
    enonce=t("""Corrige double_code(code) pour qu'elle RENVOIE le double du code au lieu de l'afficher.
        La fonction ne doit rien afficher."""),
    donnees="double_code(21)",
    resultat_attendu="42",
    code_depart=c('''
        def double_code(code):
            print(code * 2)   # ← le système ne peut pas récupérer cette valeur


        resultat = double_code(21)
        print("Le système a reçu :", resultat)
    '''),
    tests=[
        appel("double_code", [21], 42, "code 21", True),
        appel("double_code", [0], 0, "code 0"),
        appel("double_code", [-7], -14, "code négatif"),
        structure("utilise return", doit_utiliser=["return"]),
    ],
    indices=[
        "Exécute le code de départ : que reçoit le système dans la variable resultat ?",
        "print() montre une valeur à l'écran puis l'oublie. return la renvoie à celui qui a appelé la "
        "fonction. Une fonction sans return renvoie None.",
        "Exemple :\ndef carre(n):\n    return n * n\n\nx = carre(5)   # x vaut 25\nprint(x)       # on affiche APRÈS, si on veut",
    ],
    solution=c('''
        def double_code(code):
            """Renvoie le double du code."""
            return code * 2


        resultat = double_code(21)
        print("Le système a reçu :", resultat)
    '''),
    explication=t("""C'est LA confusion la plus fréquente chez les débutants. print() est destiné à
        l'humain qui regarde l'écran ; return est destiné au programme. Une bonne fonction calcule et
        renvoie ; c'est le code qui l'appelle qui décide d'afficher, de stocker ou de comparer."""),
)

mission(
    id="FON-02", ordre=22, theme="fonctions", concepts=["fonctions", "variables"], niveau=4,
    difficulte="intermediaire", titre="Opération Distance",
    briefing=t("""Deux agents donnent leurs coordonnées. À quelle distance sont-ils l'un de l'autre,
        à vol d'oiseau ?"""),
    objectif="Écrire une fonction de calcul avec plusieurs paramètres.",
    enonce=t("""Écris distance(x1, y1, x2, y2) qui renvoie la distance entre les points (x1, y1) et
        (x2, y2), arrondie à 2 décimales. Formule : racine carrée de (x2 - x1)² + (y2 - y1)²."""),
    donnees="distance(0, 0, 3, 4)",
    resultat_attendu="5.0",
    code_depart="def distance(x1, y1, x2, y2):\n    pass\n",
    tests=[
        appel("distance", [0, 0, 3, 4], 5.0, "triangle 3-4-5", True, tolerance=0.01),
        appel("distance", [1, 1, 1, 1], 0.0, "même point", tolerance=0.01),
        appel("distance", [-2, 3, 4, -5], 10.0, "coordonnées négatives", tolerance=0.01),
        appel("distance", [0, 0, 1, 1], 1.41, "diagonale", tolerance=0.01),
    ],
    indices=[
        "Quelles sont les étapes du calcul ? Écris-les en commentaires avant de coder.",
        "x ** 2 met au carré. La racine carrée s'obtient avec math.sqrt(x) (après import math) ou x ** 0.5.",
        "Exemple :\nimport math\n\ndef hypotenuse(a, b):\n    return round(math.sqrt(a ** 2 + b ** 2), 2)",
    ],
    solution=c('''
        import math


        def distance(x1, y1, x2, y2):
            """Renvoie la distance entre deux points, arrondie à 2 décimales."""
            ecart_x = x2 - x1
            ecart_y = y2 - y1
            return round(math.sqrt(ecart_x ** 2 + ecart_y ** 2), 2)
    '''),
    explication=t("""Des variables intermédiaires (ecart_x, ecart_y) rendent la formule lisible. Les
        imports se placent tout en haut du fichier. math.sqrt et ** 0.5 donnent le même résultat."""),
)

mission(
    id="FON-03", ordre=23, theme="fonctions", concepts=["fonctions", "chaines"], niveau=4,
    difficulte="intermediaire", titre="Opération Matricule",
    briefing=t("""Chaque agent reçoit un matricule : un préfixe, un tiret, puis les 3 premières lettres de
        son nom en majuscules. Le préfixe est « AG » sauf indication contraire."""),
    objectif="Utiliser un paramètre avec une valeur par défaut.",
    enonce=t("""Écris generer_matricule(nom, prefixe="AG") qui renvoie par exemple "AG-LYN" pour
        "Lynx". Si on donne un autre préfixe, il remplace « AG »."""),
    donnees='generer_matricule("Lynx")  et  generer_matricule("orion", "SP")',
    resultat_attendu='"AG-LYN"  et  "SP-ORI"',
    code_depart="def generer_matricule(nom, prefixe=...):\n    pass\n",
    tests=[
        appel("generer_matricule", ["Lynx"], "AG-LYN", "préfixe par défaut", True),
        appel("generer_matricule", ["orion", "SP"], "SP-ORI", "préfixe donné", True),
        appel("generer_matricule", ["vega"], "AG-VEG", "minuscules"),
        appel("generer_matricule", ["Nova"], "X-NOV", "préfixe nommé", kwargs={"prefixe": "X"}),
    ],
    indices=[
        "Comment donner une valeur par défaut à un paramètre dans la ligne def ?",
        "def f(a, b=10): signifie que b vaut 10 si on ne le précise pas. nom[:3] donne les 3 premières lettres.",
        "Exemple :\ndef saluer(nom, formule=\"Bonjour\"):\n    return f\"{formule} {nom}\"\n\nsaluer(\"Iris\")          # \"Bonjour Iris\"\nsaluer(\"Iris\", \"Salut\") # \"Salut Iris\"",
    ],
    solution=c('''
        def generer_matricule(nom, prefixe="AG"):
            """Renvoie le matricule : PREFIXE-ABC."""
            return f"{prefixe}-{nom[:3].upper()}"
    '''),
    explication=t("""Un paramètre par défaut rend un argument facultatif. On peut aussi le nommer à
        l'appel : generer_matricule("Nova", prefixe="X"), ce qui rend le code plus clair."""),
)

mission(
    id="FON-04", ordre=36, theme="fonctions", concepts=["fonctions", "dictionnaires", "boucle-for", "chaines"],
    niveau=6, difficulte="difficile", titre="Opération Rapport de Mission",
    briefing=t("""Le directeur veut, chaque soir, un résumé en une ligne des missions de la journée."""),
    objectif="Combiner boucle, dictionnaires, calcul et f-string dans une fonction réaliste.",
    enonce=t("""Écris rapport(missions) : missions est une liste de dictionnaires {"nom": ...,
        "statut": "réussie" ou "échouée"}. Renvoie le texte
        "<r> réussie(s), <e> échouée(s), taux de réussite : <t>%" où t est le pourcentage de réussite
        arrondi à l'entier (round). S'il n'y a aucune mission, renvoie "Aucune mission"."""),
    donnees=('[{"nom": "Onyx", "statut": "réussie"}, {"nom": "Brume", "statut": "échouée"}, '
             '{"nom": "Zénith", "statut": "réussie"}]'),
    resultat_attendu='"2 réussie(s), 1 échouée(s), taux de réussite : 67%"',
    code_depart="def rapport(missions):\n    pass\n",
    tests=[
        appel("rapport", [[{"nom": "Onyx", "statut": "réussie"}, {"nom": "Brume", "statut": "échouée"},
                           {"nom": "Zénith", "statut": "réussie"}]],
              "2 réussie(s), 1 échouée(s), taux de réussite : 67%", "exemple", True),
        appel("rapport", [[]], "Aucune mission", "journée calme", True),
        appel("rapport", [[{"nom": "A", "statut": "échouée"}]], "0 réussie(s), 1 échouée(s), taux de réussite : 0%",
              "tout échoue"),
        appel("rapport", [[{"nom": "A", "statut": "réussie"}] * 4],
              "4 réussie(s), 0 échouée(s), taux de réussite : 100%", "sans faute"),
    ],
    indices=[
        "Découpe le problème : 1) cas vide ; 2) compter ; 3) calculer le taux ; 4) construire le texte.",
        "Deux compteurs dans une boucle (if mission[\"statut\"] == \"réussie\"). Taux = réussies / total × 100, "
        "puis round(). Une f-string assemble le texte final.",
        "Exemple :\nvrais = 0\nfor reponse in reponses:\n    if reponse[\"ok\"]:\n        vrais += 1\n"
        "pourcentage = round(vrais / len(reponses) * 100)\nreturn f\"{vrais} bonnes réponses ({pourcentage}%)\"",
    ],
    solution=c('''
        def rapport(missions):
            """Résume une liste de missions en une ligne."""
            if not missions:
                return "Aucune mission"
            reussies = 0
            for mission in missions:
                if mission["statut"] == "réussie":
                    reussies += 1
            echouees = len(missions) - reussies
            taux = round(reussies / len(missions) * 100)
            return f"{reussies} réussie(s), {echouees} échouée(s), taux de réussite : {taux}%"
    '''),
    explication=t("""Un problème « réel » se résout en petites étapes, dans l'ordre : cas particulier
        d'abord, puis comptage, calcul et mise en forme. Calculer les échecs par soustraction évite un
        deuxième compteur."""),
)

# ===========================================================================
# GESTION DES ERREURS
# ===========================================================================

mission(
    id="EXC-01", ordre=24, theme="exceptions", concepts=["exceptions", "types"], niveau=4,
    difficulte="intermediaire", titre="Opération Conversion Sécurisée", revision_pour=["conversion_texte"],
    briefing=t("""Les codes tapés à la main sur le clavier de terrain contiennent parfois des fautes de
        frappe. Le programme ne doit jamais planter pour autant."""),
    objectif="Utiliser try / except ValueError.",
    enonce=t("""Écris convertir_code(texte) qui renvoie le nombre entier correspondant, ou None si le
        texte n'est pas un nombre entier valide. Utilise try / except."""),
    donnees='convertir_code("42") et convertir_code("4A")',
    resultat_attendu="42 et None",
    code_depart="def convertir_code(texte):\n    pass\n",
    tests=[
        appel("convertir_code", ["42"], 42, "code valide", True),
        appel("convertir_code", ["4A"], None, "faute de frappe", True),
        appel("convertir_code", [""], None, "texte vide"),
        appel("convertir_code", ["-17"], -17, "nombre négatif"),
        appel("convertir_code", ["3.5"], None, "nombre à virgule"),
        structure("utilise try / except", doit_utiliser=["try"]),
    ],
    indices=[
        "Que se passe-t-il exactement quand on exécute int(\"4A\") ? Quel est le nom de l'erreur ?",
        "try: contient l'instruction risquée. except ValueError: contient le plan B (ici : renvoyer None).",
        "Exemple :\ntry:\n    prix = float(saisie)\nexcept ValueError:\n    prix = 0.0",
    ],
    solution=c('''
        def convertir_code(texte):
            """Renvoie le code en entier, ou None s'il est invalide."""
            try:
                return int(texte)
            except ValueError:
                return None
    '''),
    explication=t("""Une exception n'est pas forcément un bug : c'est un signal. try / except permet
        d'y répondre proprement. On précise ValueError pour ne pas masquer d'autres erreurs
        inattendues."""),
)

mission(
    id="EXC-02", ordre=25, theme="exceptions", concepts=["exceptions", "fonctions"], niveau=4,
    difficulte="intermediaire", titre="Opération Partage des Ressources", revision_pour=["division_zero"],
    briefing=t("""Les rations doivent être partagées équitablement entre les agents présents. Parfois,
        personne n'est présent… et le programme plante."""),
    objectif="Attraper une ZeroDivisionError.",
    enonce=t("""Écris partager(ressources, agents) qui renvoie ressources // agents. S'il n'y a aucun
        agent (division par zéro), renvoie 0. Utilise try / except ZeroDivisionError."""),
    donnees="partager(17, 5)",
    resultat_attendu="3",
    code_depart="def partager(ressources, agents):\n    return ressources // agents\n",
    tests=[
        appel("partager", [17, 5], 3, "exemple", True),
        appel("partager", [10, 0], 0, "aucun agent", True),
        appel("partager", [0, 3], 0, "aucune ressource"),
        appel("partager", [100, 10], 10, "partage exact"),
        structure("utilise try / except", doit_utiliser=["try"]),
    ],
    indices=[
        "Exécute partager(10, 0) avec le code de départ : quelle erreur obtiens-tu ?",
        "Place la division dans un bloc try, et le cas de secours dans except ZeroDivisionError.",
        "Exemple :\ntry:\n    vitesse = distance / temps\nexcept ZeroDivisionError:\n    vitesse = 0",
    ],
    solution=c('''
        def partager(ressources, agents):
            """Partage les ressources entre les agents (0 s'il n'y a personne)."""
            try:
                return ressources // agents
            except ZeroDivisionError:
                return 0
    '''),
    explication=t("""On aurait pu écrire « if agents == 0: return 0 ». Les deux approches sont
        correctes : tester avant (if) ou demander pardon après (try/except). Ici, l'objectif était de
        pratiquer try / except."""),
)

mission(
    id="EXC-03", ordre=33, theme="exceptions", concepts=["exceptions", "dictionnaires"], niveau=5,
    difficulte="difficile", titre="Opération Fiche Incomplète",
    briefing=t("""Les fiches d'agents arrivent parfois incomplètes, voire totalement absentes (None).
        Le lecteur de fiches doit gérer tous ces cas."""),
    objectif="Gérer plusieurs types d'exceptions différents.",
    enonce=t("""Écris lire_fiche(fiche, champ) qui renvoie fiche[champ]. Si le champ n'existe pas
        (KeyError), renvoie "CHAMP MANQUANT". Si la fiche vaut None (TypeError), renvoie
        "FICHE INVALIDE"."""),
    donnees='fiche = {"nom": "Lynx", "grade": "Analyste"}',
    resultat_attendu='lire_fiche(fiche, "grade") → "Analyste"',
    code_depart="def lire_fiche(fiche, champ):\n    pass\n",
    tests=[
        appel("lire_fiche", [{"nom": "Lynx", "grade": "Analyste"}, "grade"], "Analyste", "champ présent", True),
        appel("lire_fiche", [{"nom": "Lynx"}, "base"], "CHAMP MANQUANT", "champ absent", True),
        appel("lire_fiche", [None, "nom"], "FICHE INVALIDE", "fiche absente"),
        appel("lire_fiche", [{}, "nom"], "CHAMP MANQUANT", "fiche vide"),
        structure("utilise try / except", doit_utiliser=["try"]),
    ],
    indices=[
        "Quelles erreurs Python lève-t-il pour dico[\"x\"] avec x absent ? Et pour None[\"x\"] ?",
        "Un try peut avoir plusieurs except, un par type d'erreur : except KeyError: … except TypeError: …",
        "Exemple :\ntry:\n    valeur = donnees[cle]\nexcept KeyError:\n    valeur = \"absent\"\nexcept TypeError:\n    valeur = \"illisible\"",
    ],
    solution=c('''
        def lire_fiche(fiche, champ):
            """Lit un champ d'une fiche en gérant les fiches incomplètes ou absentes."""
            try:
                return fiche[champ]
            except KeyError:
                return "CHAMP MANQUANT"
            except TypeError:
                return "FICHE INVALIDE"
    '''),
    explication=t("""Chaque except traite un problème précis avec une réponse adaptée. C'est bien plus
        sûr qu'un « except: » général, qui cacherait aussi les vraies erreurs de programmation."""),
)

# ===========================================================================
# CORRECTION DE PROGRAMMES (niveau 7)
# ===========================================================================

mission(
    id="COR-01", ordre=34, theme="listes", concepts=["listes", "boucle-for", "exceptions"], niveau=7,
    difficulte="intermediaire", titre="Opération Programme Saboté",
    briefing=t("""Un agent double a modifié le calcul de moyenne du centre d'entraînement. Les notes des
        recrues sont fausses… et le programme plante parfois. Trouve et corrige TOUS les sabotages."""),
    objectif="Lire un programme existant, repérer les erreurs de logique et les corriger.",
    enonce=t("""Corrige moyenne_notes(notes) : elle doit renvoyer la moyenne de la liste, ou 0 si la
        liste est vide. Il y a trois sabotages."""),
    donnees="moyenne_notes([12, 8, 16])",
    resultat_attendu="12.0",
    code_depart=c('''
        def moyenne_notes(notes):
            """Renvoie la moyenne des notes, ou 0 si la liste est vide."""
            total = 0
            for i in range(1, len(notes)):
                total = notes[i]
            return total / len(notes)
    '''),
    tests=[
        appel("moyenne_notes", [[12, 8, 16]], 12.0, "trois notes", True, tolerance=0.001),
        appel("moyenne_notes", [[10]], 10.0, "une note", tolerance=0.001),
        appel("moyenne_notes", [[]], 0, "aucune note"),
        appel("moyenne_notes", [[5, 6, 7, 8]], 6.5, "quatre notes", tolerance=0.001),
    ],
    indices=[
        "Déroule la boucle à la main avec [12, 8, 16] : quelles valeurs prend i ? Que vaut total à chaque tour ?",
        "range(1, len(notes)) commence à 1 (la première note est oubliée). total = … remplace au lieu "
        "d'ajouter. Et si notes est vide ?",
        "Rappel :\nfor note in notes:      # parcourt TOUTES les notes\n    total += note       # += ajoute\n"
        "if not notes:          # cas de la liste vide\n    return 0",
    ],
    solution=c('''
        def moyenne_notes(notes):
            """Renvoie la moyenne des notes, ou 0 si la liste est vide."""
            if not notes:
                return 0
            total = 0
            for note in notes:
                total += note
            return total / len(notes)
    '''),
    explication=t("""Les trois sabotages : 1) range(1, …) ignorait la première note ; 2) total = remplaçait
        la valeur au lieu de l'ajouter ; 3) la liste vide provoquait une division par zéro. Lire du code
        existant en le « déroulant » à la main est une compétence essentielle."""),
)

mission(
    id="COR-02", ordre=37, theme="fonctions", concepts=["fonctions", "dictionnaires", "print-return"], niveau=7,
    difficulte="difficile", titre="Opération Filtre Défectueux",
    briefing=t("""Le filtre des agents actifs a été écrit en urgence pendant une alerte. Il ne fonctionne
        pas du tout. Remets-le en état de marche."""),
    objectif="Corriger des erreurs de syntaxe ET de logique dans un même programme.",
    enonce=t("""Corrige agents_actifs(agents) : agents est une liste de dictionnaires {"nom": ...,
        "statut": ...}. La fonction renvoie la liste des noms des agents dont le statut est "actif"."""),
    donnees='[{"nom": "Lynx", "statut": "actif"}, {"nom": "Cobra", "statut": "retraité"}]',
    resultat_attendu='["Lynx"]',
    code_depart=c('''
        def agents_actifs(agents)
            actifs = []
            for agent in agents:
                if agent["statut"] = "actif":
                    actifs.append(agent["nom"])
                print(actifs)
    '''),
    tests=[
        appel("agents_actifs", [[{"nom": "Lynx", "statut": "actif"}, {"nom": "Cobra", "statut": "retraité"}]],
              ["Lynx"], "exemple", True),
        appel("agents_actifs", [[]], [], "aucun agent"),
        appel("agents_actifs", [[{"nom": "A", "statut": "actif"}, {"nom": "B", "statut": "actif"}]],
              ["A", "B"], "tous actifs"),
        appel("agents_actifs", [[{"nom": "C", "statut": "en mission"}]], [], "aucun actif"),
    ],
    indices=[
        "Exécute le code : Python t'indique une première erreur. Corrige-la, puis recommence. Combien en trouves-tu ?",
        "Il manque « : » après le def. Dans un if, on compare avec ==. Une fonction doit renvoyer son résultat "
        "avec return… et pas à chaque tour de boucle.",
        "Rappel de structure :\ndef filtre(elements):\n    resultat = []\n    for e in elements:\n        if e[\"cle\"] == \"valeur\":\n"
        "            resultat.append(e[\"nom\"])\n    return resultat   # aligné avec le for, pas dedans",
    ],
    solution=c('''
        def agents_actifs(agents):
            """Renvoie les noms des agents actifs."""
            actifs = []
            for agent in agents:
                if agent["statut"] == "actif":
                    actifs.append(agent["nom"])
            return actifs
    '''),
    explication=t("""Quatre problèmes : les deux-points manquants après def, = au lieu de == dans le if,
        print au lieu de return, et l'indentation du print qui le plaçait dans la boucle. Python ne
        signale que la PREMIÈRE erreur de syntaxe à la fois : corrige, relance, recommence."""),
)

mission(
    id="COR-03", ordre=27, theme="boucles", concepts=["boucle-while", "listes"], niveau=7,
    difficulte="intermediaire", titre="Opération Boucle Sans Fin", revision_pour=["boucle_infinie"],
    briefing=t("""Le générateur de numéros de badge tourne depuis trois jours sans s'arrêter. Le serveur
        chauffe. Trouve pourquoi."""),
    objectif="Repérer et corriger une boucle infinie.",
    enonce=t("""Corrige compter_jusqua(limite) : elle doit renvoyer la liste [1, 2, …, limite]
        (liste vide si limite vaut 0)."""),
    donnees="compter_jusqua(4)",
    resultat_attendu="[1, 2, 3, 4]",
    code_depart=c('''
        def compter_jusqua(limite):
            """Renvoie la liste [1, 2, ..., limite]."""
            nombres = []
            compteur = 1
            while compteur <= limite:
                nombres.append(compteur)
            return nombres
    '''),
    tests=[
        appel("compter_jusqua", [4], [1, 2, 3, 4], "jusqu'à 4", True),
        appel("compter_jusqua", [0], [], "limite 0"),
        appel("compter_jusqua", [1], [1], "limite 1"),
        appel("compter_jusqua", [10], list(range(1, 11)), "jusqu'à 10"),
    ],
    indices=[
        "À chaque tour, la condition compteur <= limite change-t-elle ?",
        "Une boucle while s'arrête quand sa condition devient fausse. Il faut donc qu'une ligne DANS la "
        "boucle modifie compteur.",
        "Exemple :\ni = 0\nwhile i < 3:\n    print(i)\n    i += 1   # sans cette ligne, i reste 0 pour toujours",
    ],
    solution=c('''
        def compter_jusqua(limite):
            """Renvoie la liste [1, 2, ..., limite]."""
            nombres = []
            compteur = 1
            while compteur <= limite:
                nombres.append(compteur)
                compteur += 1
            return nombres
    '''),
    explication=t("""Le compteur n'augmentait jamais : la condition restait vraie pour toujours.
        L'application a arrêté le programme après quelques secondes grâce à sa limite de temps.
        Réflexe d'agent : pour chaque while, demande-toi « quelle ligne rapproche la fin ? »."""),
)

mission(
    id="COR-04", ordre=14, theme="conditions", concepts=["conditions", "fonctions"], niveau=7,
    difficulte="facile", titre="Opération Alignement", revision_pour=["indentation"],
    briefing=t("""Un fichier a été transmis par un canal brouillé : les espaces en début de ligne ont été
        mélangés. Python refuse de l'exécuter."""),
    objectif="Comprendre que l'indentation définit les blocs en Python.",
    enonce=t("""Corrige l'indentation de classer_agent(points) : elle renvoie "Élite" si points >= 100,
        "Confirmé" si points >= 50, sinon "Recrue". Utilise 4 espaces par niveau."""),
    donnees="classer_agent(75)",
    resultat_attendu='"Confirmé"',
    code_depart=c('''
        def classer_agent(points):
          if points >= 100:
                return "Élite"
          elif points >= 50:
          return "Confirmé"
          else:
              return "Recrue"
    '''),
    tests=[
        appel("classer_agent", [75], "Confirmé", "75 points", True),
        appel("classer_agent", [100], "Élite", "100 points"),
        appel("classer_agent", [12], "Recrue", "12 points"),
        appel("classer_agent", [50], "Confirmé", "50 points"),
    ],
    indices=[
        "Quelles lignes appartiennent au bloc de la fonction ? Et au bloc de chaque if / elif / else ?",
        "Niveau 1 (dans la fonction) : 4 espaces. Niveau 2 (dans un if) : 8 espaces. "
        "if, elif et else doivent être alignés entre eux.",
        "Exemple :\ndef signe(n):\n    if n > 0:\n        return \"+\"\n    else:\n        return \"-\"",
    ],
    solution=c('''
        def classer_agent(points):
            """Renvoie le grade correspondant aux points."""
            if points >= 100:
                return "Élite"
            elif points >= 50:
                return "Confirmé"
            else:
                return "Recrue"
    '''),
    explication=t("""En Python, l'indentation n'est pas décorative : c'est elle qui indique quelles
        lignes appartiennent à quel bloc. La convention PEP 8 est de 4 espaces par niveau. Dans
        l'éditeur, la touche Tab insère automatiquement 4 espaces."""),
)

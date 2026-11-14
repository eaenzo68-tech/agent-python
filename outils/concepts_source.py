"""Fiches récapitulatives de la Bibliothèque des concepts.

Chaque concept contient :
- id, nom, categorie        : identification ;
- resume                    : l'idée en quelques phrases simples ;
- syntaxe                   : la forme générale ;
- exemple                   : un exemple commenté ;
- pieges                    : les erreurs fréquentes des débutants ;
- conseil                   : une habitude de code propre ;
- mots_cles                 : mots repérés dans tes notes de cours
                              (sert à « Analyser mes notes »).
"""

from textwrap import dedent


def c(texte):
    return dedent(texte).strip("\n") + "\n"


CONCEPTS = [
    {
        "id": "variables", "nom": "Variables et affectation", "categorie": "Bases",
        "resume": "Une variable est une étiquette posée sur une valeur. Le signe = range la valeur de droite "
                  "dans la variable de gauche. On peut ensuite réutiliser ou modifier cette valeur.",
        "syntaxe": c('''
            nom_variable = valeur
            nom_variable = nom_variable + 1   # on peut écrire : nom_variable += 1
        '''),
        "exemple": c('''
            agents_presents = 4
            agents_presents += 2          # 6
            nom_code = "Lynx"
            print(nom_code, agents_presents)
        '''),
        "pieges": ["Utiliser une variable avant de l'avoir créée (NameError).",
                   "Confondre = (ranger) et == (comparer).",
                   "Oublier que Python distingue majuscules et minuscules : Total ≠ total."],
        "conseil": "Choisis des noms qui disent ce que contient la variable, en snake_case : total_points, nom_agent.",
        "mots_cles": ["variable", "variables", "affectation", "assignation", "identifiant", "constante"],
    },
    {
        "id": "types", "nom": "Types de données et conversions", "categorie": "Bases",
        "resume": "Chaque valeur a un type : int (entier), float (nombre à virgule), str (texte), bool (True/False). "
                  "Le type décide des opérations possibles. On convertit avec int(), float(), str().",
        "syntaxe": c('''
            type(valeur)        # affiche le type
            int("42")           # texte → entier
            float("3.5")        # texte → nombre à virgule
            str(42)             # nombre → texte
        '''),
        "exemple": c('''
            age_texte = input("Âge ? ")   # input() renvoie TOUJOURS un str
            age = int(age_texte)
            print(f"Dans un an : {age + 1}")
        '''),
        "pieges": ["Additionner un texte et un nombre : \"5\" + 3 → TypeError.",
                   "Oublier que input() renvoie un texte.",
                   "int(\"3.5\") échoue : il faut float() pour un nombre à virgule."],
        "conseil": "En cas de doute, affiche type(valeur) pour vérifier ce que tu manipules.",
        "mots_cles": ["type", "types", "int", "float", "str", "bool", "entier", "flottant", "booléen",
                      "conversion", "convertir", "transtypage"],
    },
    {
        "id": "conditions", "nom": "Conditions (if / elif / else)", "categorie": "Structures de contrôle",
        "resume": "Une condition permet d'exécuter un bloc seulement si une expression est vraie. elif teste un "
                  "autre cas, else traite tout le reste. Python teste dans l'ordre et s'arrête au premier cas vrai.",
        "syntaxe": c('''
            if condition:
                instructions
            elif autre_condition:
                instructions
            else:
                instructions
        '''),
        "exemple": c('''
            niveau = 4
            if niveau >= 5:
                print("Accès total")
            elif niveau >= 3:
                print("Accès limité")
            else:
                print("Accès refusé")
        '''),
        "pieges": ["Oublier les deux-points « : » à la fin de la ligne if.",
                   "Écrire = au lieu de == dans une condition.",
                   "Mal ordonner les cas : le premier cas vrai « gagne »."],
        "conseil": "Opérateurs utiles : == != < <= > >=, et pour combiner : and, or, not.",
        "mots_cles": ["if", "elif", "else", "condition", "conditions", "conditionnel", "comparaison",
                      "and", "or", "not", "structures de contrôle"],
    },
    {
        "id": "boucle-for", "nom": "Boucle for et range()", "categorie": "Structures de contrôle",
        "resume": "La boucle for répète un bloc pour chaque élément d'une collection (liste, texte, range…). "
                  "range(n) produit les nombres de 0 à n - 1.",
        "syntaxe": c('''
            for element in collection:
                instructions

            range(fin)               # 0, 1, …, fin - 1
            range(debut, fin, pas)   # fin toujours EXCLUE
        '''),
        "exemple": c('''
            total = 0
            for montant in [120, 80, 45]:
                total += montant
            print(total)   # 245

            for i in range(3, 0, -1):
                print(i)   # 3, 2, 1
        '''),
        "pieges": ["Oublier que la borne de fin de range() est exclue.",
                   "Écrire for i in 5 au lieu de for i in range(5).",
                   "Placer un return DANS la boucle alors qu'il devrait être après."],
        "conseil": "Parcours directement les éléments (for nom in noms) plutôt que les indices, sauf si tu as besoin de la position.",
        "mots_cles": ["for", "boucle for", "range", "itération", "itérer", "parcourir", "enumerate", "boucle", "boucles"],
    },
    {
        "id": "boucle-while", "nom": "Boucle while", "categorie": "Structures de contrôle",
        "resume": "La boucle while répète un bloc TANT QUE sa condition est vraie. Elle sert quand on ne connaît "
                  "pas à l'avance le nombre de tours. Il faut qu'une instruction rapproche la condition de « fausse ».",
        "syntaxe": c('''
            while condition:
                instructions
                # modifier une variable de la condition !
        '''),
        "exemple": c('''
            carburant = 100
            jours = 0
            while carburant >= 30:
                carburant -= 30
                jours += 1
            print(jours)   # 3
        '''),
        "pieges": ["Oublier de modifier la variable testée : boucle infinie.",
                   "Utiliser while quand une boucle for suffit.",
                   "Mauvaise condition (< au lieu de <=) : un tour de trop ou de moins."],
        "conseil": "Pour chaque while, demande-toi : « quelle ligne fera devenir la condition fausse ? »",
        "mots_cles": ["while", "boucle while", "tant que", "break", "continue", "boucle infinie"],
    },
    {
        "id": "listes", "nom": "Listes", "categorie": "Structures de données",
        "resume": "Une liste est une collection ordonnée et modifiable. Chaque élément a une position (indice) "
                  "qui commence à 0. On ajoute avec append(), on lit avec liste[i], on mesure avec len().",
        "syntaxe": c('''
            ma_liste = [valeur1, valeur2]
            ma_liste[0]            # premier élément
            ma_liste[-1]           # dernier élément
            ma_liste.append(x)     # ajoute à la fin
            ma_liste[1:3]          # découpage (indices 1 et 2)
            x in ma_liste          # True si x est présent
        '''),
        "exemple": c('''
            suspects = ["Ivan", "Lea"]
            suspects.append("Marc")
            print(len(suspects), suspects[-1])   # 3 Marc
        '''),
        "pieges": ["liste[len(liste)] n'existe pas (IndexError) : le dernier indice est len(liste) - 1.",
                   "liste = liste.sort() remplace la liste par None : sort() renvoie None.",
                   "Modifier une liste reçue en paramètre modifie aussi l'originale."],
        "conseil": "sorted(liste) crée une copie triée ; liste.sort() trie l'originale.",
        "mots_cles": ["liste", "listes", "list", "append", "indice", "index", "slicing", "découpage",
                      "insert", "remove", "pop", "sort", "sorted", "len"],
    },
    {
        "id": "tuples", "nom": "Tuples", "categorie": "Structures de données",
        "resume": "Un tuple ressemble à une liste mais il est IMMUABLE : on ne peut pas le modifier après sa "
                  "création. Il sert à regrouper des valeurs qui vont ensemble (coordonnées, nom et âge…).",
        "syntaxe": c('''
            point = (3, 4)
            x, y = point          # déballage
            un_seul = (5,)        # la virgule est obligatoire
        '''),
        "exemple": c('''
            def min_max(valeurs):
                return (min(valeurs), max(valeurs))

            plus_petit, plus_grand = min_max([4, 9, 1])
        '''),
        "pieges": ["Essayer de modifier un élément : point[0] = 5 → TypeError.",
                   "Oublier la virgule pour un tuple d'un seul élément.",
                   "Déballer avec le mauvais nombre de variables (ValueError)."],
        "conseil": "Renvoie un tuple quand une fonction doit renvoyer plusieurs valeurs liées.",
        "mots_cles": ["tuple", "tuples", "immuable", "déballage", "unpacking"],
    },
    {
        "id": "dictionnaires", "nom": "Dictionnaires", "categorie": "Structures de données",
        "resume": "Un dictionnaire associe des CLÉS à des VALEURS (comme un annuaire). On accède à une valeur "
                  "par sa clé, pas par une position. Les clés sont uniques.",
        "syntaxe": c('''
            d = {"cle": valeur}
            d["cle"]                  # lire (KeyError si absente)
            d.get("cle", defaut)      # lire sans risque
            d["nouvelle"] = valeur    # ajouter ou modifier
            for cle, valeur in d.items():
                ...
        '''),
        "exemple": c('''
            compteur = {}
            for ville in ["Berne", "Oslo", "Berne"]:
                compteur[ville] = compteur.get(ville, 0) + 1
            print(compteur)   # {'Berne': 2, 'Oslo': 1}
        '''),
        "pieges": ["Lire une clé absente avec d[cle] → KeyError.",
                   "Utiliser une liste comme clé (TypeError : unhashable).",
                   "Oublier que \"Lynx\" et \"lynx\" sont deux clés différentes."],
        "conseil": "Teste la présence avec « if cle in d: » ou utilise d.get(cle, valeur_par_defaut).",
        "mots_cles": ["dictionnaire", "dictionnaires", "dict", "clé", "clés", "items", "keys", "values",
                      "get", "associatif"],
    },
    {
        "id": "chaines", "nom": "Chaînes de caractères", "categorie": "Bases",
        "resume": "Une chaîne (str) est un texte. Elle se parcourt et se découpe comme une liste, mais elle est "
                  "immuable : les méthodes renvoient une NOUVELLE chaîne.",
        "syntaxe": c('''
            texte.upper() / texte.lower()     # majuscules / minuscules
            texte.strip()                     # retire les espaces autour
            texte.split()                     # découpe en liste de mots
            " ".join(liste)                   # assemble une liste de textes
            texte.replace("a", "b")
            f"Bonjour {nom}"                  # f-string
        '''),
        "exemple": c('''
            brut = "  agent LYNX  "
            propre = brut.strip().capitalize()
            print(f"[{propre}]")   # [Agent lynx]
        '''),
        "pieges": ["Oublier de récupérer le résultat : texte.upper() seul ne change pas texte.",
                   "Vouloir modifier un caractère : texte[0] = \"A\" → TypeError.",
                   "Mélanger guillemets ouvrants et fermants."],
        "conseil": "Préfère les f-strings pour assembler texte et valeurs : f\"Score : {score}\".",
        "mots_cles": ["chaîne", "chaînes", "chaine", "string", "caractère", "caractères", "split", "join",
                      "upper", "lower", "strip", "f-string", "replace", "texte"],
    },
    {
        "id": "fonctions", "nom": "Fonctions", "categorie": "Fonctions",
        "resume": "Une fonction est un bloc de code nommé et réutilisable. Elle reçoit des paramètres, fait un "
                  "travail et renvoie un résultat avec return. Elle permet de découper un problème en petites étapes.",
        "syntaxe": c('''
            def nom_fonction(parametre1, parametre2="defaut"):
                """Docstring : ce que fait la fonction."""
                ...
                return resultat

            valeur = nom_fonction(argument1)
        '''),
        "exemple": c('''
            def aire_rectangle(largeur, hauteur):
                """Renvoie l'aire d'un rectangle."""
                return largeur * hauteur

            print(aire_rectangle(3, 4))   # 12
        '''),
        "pieges": ["Oublier les parenthèses à l'appel : nom_fonction au lieu de nom_fonction().",
                   "Utiliser une variable locale en dehors de la fonction (NameError).",
                   "Donner trop ou pas assez d'arguments (TypeError)."],
        "conseil": "Une fonction = une seule tâche. Si elle dépasse ~20 lignes, découpe-la.",
        "mots_cles": ["fonction", "fonctions", "def", "paramètre", "paramètres", "argument", "arguments",
                      "appel", "docstring", "portée", "locale"],
    },
    {
        "id": "print-return", "nom": "print() ou return ?", "categorie": "Fonctions",
        "resume": "print() AFFICHE une valeur pour l'humain, puis l'oublie. return RENVOIE une valeur au programme, "
                  "qui peut la stocker, la comparer ou l'afficher plus tard. Une fonction sans return renvoie None.",
        "syntaxe": c('''
            def avec_print(x):
                print(x * 2)      # affiche, renvoie None

            def avec_return(x):
                return x * 2      # renvoie la valeur
        '''),
        "exemple": c('''
            a = avec_print(5)    # affiche 10, mais a vaut None
            b = avec_return(5)   # n'affiche rien, b vaut 10
            print(b + 1)         # 11
        '''),
        "pieges": ["Écrire print() dans une fonction dont on veut réutiliser le résultat.",
                   "Placer return dans une boucle alors qu'il devrait être après.",
                   "Croire que la fonction « a marché » parce qu'on voit le résultat à l'écran."],
        "conseil": "Règle d'agent : une fonction calcule et RENVOIE ; le programme principal décide d'afficher.",
        "mots_cles": ["return", "valeur de retour", "renvoyer", "retourner", "none", "print"],
    },
    {
        "id": "exceptions", "nom": "Gestion des erreurs (try / except)", "categorie": "Compléments",
        "resume": "Une exception est un signal d'erreur (ValueError, KeyError…). Avec try / except, on prévoit un "
                  "« plan B » au lieu de laisser le programme s'arrêter.",
        "syntaxe": c('''
            try:
                instruction_risquee
            except TypeDErreur:
                plan_b
            else:
                # si aucune erreur
            finally:
                # toujours exécuté
        '''),
        "exemple": c('''
            saisie = "4A"
            try:
                code = int(saisie)
            except ValueError:
                code = None
            print(code)   # None
        '''),
        "pieges": ["Utiliser « except: » sans préciser l'erreur : cela cache les vrais bugs.",
                   "Mettre trop de code dans le try.",
                   "Utiliser try/except pour éviter de réfléchir au cas normal."],
        "conseil": "Attrape seulement l'erreur que tu sais gérer, au plus près de l'instruction risquée.",
        "mots_cles": ["exception", "exceptions", "try", "except", "erreur", "erreurs", "raise", "finally",
                      "valueerror", "typeerror", "keyerror"],
    },
    {
        "id": "fichiers", "nom": "Fichiers", "categorie": "Compléments",
        "resume": "On lit et écrit des fichiers texte avec open(). Le bloc « with » ferme automatiquement le "
                  "fichier, même en cas d'erreur.",
        "syntaxe": c('''
            with open("fichier.txt", "r", encoding="utf-8") as f:
                for ligne in f:
                    ...

            with open("sortie.txt", "w", encoding="utf-8") as f:
                f.write("texte\\n")
        '''),
        "exemple": c('''
            with open("agents.txt", "w", encoding="utf-8") as f:
                f.write("Lynx\\nOrion\\n")
            with open("agents.txt", encoding="utf-8") as f:
                noms = [ligne.strip() for ligne in f]
        '''),
        "pieges": ["Oublier encoding=\"utf-8\" (accents mal lus sous Windows).",
                   "Le mode \"w\" efface le contenu existant.",
                   "Oublier strip() : chaque ligne lue se termine par \\n."],
        "conseil": "Utilise toujours « with open(...) as f: ». Dans l'application, les fichiers sont virtuels.",
        "mots_cles": ["fichier", "fichiers", "open", "with open", "read", "write", "readline", "csv", "encoding"],
    },
    {
        "id": "poo", "nom": "Programmation orientée objet", "categorie": "Avancé",
        "resume": "Une classe est un plan de construction ; un objet est un exemplaire construit à partir de ce plan. "
                  "Les attributs stockent les données de l'objet, les méthodes sont ses fonctions.",
        "syntaxe": c('''
            class Agent:
                def __init__(self, nom, niveau):
                    self.nom = nom
                    self.niveau = niveau

                def promouvoir(self):
                    self.niveau += 1
        '''),
        "exemple": c('''
            lynx = Agent("Lynx", 2)
            lynx.promouvoir()
            print(lynx.nom, lynx.niveau)   # Lynx 3
        '''),
        "pieges": ["Oublier self comme premier paramètre des méthodes.",
                   "Oublier self. devant un attribut : nom au lieu de self.nom.",
                   "Confondre la classe (Agent) et l'objet (lynx)."],
        "conseil": "Noms de classes en PascalCase (Agent), noms d'objets et de méthodes en snake_case.",
        "mots_cles": ["classe", "classes", "class", "objet", "objets", "méthode", "méthodes", "attribut",
                      "__init__", "self", "héritage", "instance", "orienté objet"],
    },
    {
        "id": "numpy", "nom": "NumPy", "categorie": "Analyse de données",
        "resume": "NumPy fournit des tableaux (array) de nombres très rapides et des opérations appliquées à tous "
                  "les éléments d'un coup, sans boucle.",
        "syntaxe": c('''
            import numpy as np
            tableau = np.array([1, 2, 3])
            tableau * 2          # array([2, 4, 6])
            tableau.mean()       # moyenne
            tableau[tableau > 1] # filtrage
        '''),
        "exemple": c('''
            import numpy as np
            temperatures = np.array([12.5, 15.0, 9.5])
            print(temperatures.mean(), temperatures.max())
        '''),
        "pieges": ["Mélanger listes Python et arrays : [1, 2] * 2 ≠ np.array([1, 2]) * 2.",
                   "Oublier « import numpy as np ».",
                   "Les arrays ont un seul type : mélanger texte et nombres pose problème."],
        "conseil": "Dans l'application, NumPy nécessite un téléchargement supplémentaire : à travailler dans ton IDE habituel.",
        "mots_cles": ["numpy", "np.", "array", "ndarray", "tableau numpy", "vectorisation"],
    },
    {
        "id": "pandas", "nom": "pandas et analyse de données", "categorie": "Analyse de données",
        "resume": "pandas organise les données en tableaux (DataFrame) avec des colonnes nommées. On peut lire un "
                  "CSV, filtrer des lignes, grouper et calculer des statistiques en quelques lignes.",
        "syntaxe": c('''
            import pandas as pd
            df = pd.read_csv("donnees.csv")
            df["colonne"]               # une colonne (Series)
            df[df["age"] > 30]          # filtrer
            df.groupby("ville")["score"].mean()
        '''),
        "exemple": c('''
            import pandas as pd
            df = pd.DataFrame({"agent": ["Lynx", "Orion"], "missions": [12, 7]})
            print(df["missions"].sum())
        '''),
        "pieges": ["Confondre df[\"col\"] (colonne) et df.loc[ligne] (ligne).",
                   "Oublier que la plupart des opérations renvoient un NOUVEAU DataFrame.",
                   "Filtrer avec and/or au lieu de & et |."],
        "conseil": "Commence toujours par df.head() et df.info() pour découvrir les données.",
        "mots_cles": ["pandas", "dataframe", "pd.", "series", "read_csv", "groupby", "analyse de données", "csv"],
    },
]

BADGES = [
    {"id": "premiere-mission", "nom": "Première mission", "symbole": "I",
     "description": "Accomplir ta toute première mission.", "condition": {"type": "missions_accomplies", "valeur": 1}},
    {"id": "maitre-conditions", "nom": "Maître des conditions", "symbole": "?:",
     "description": "Accomplir 3 missions du thème Conditions.", "condition": {"type": "theme", "theme": "conditions", "valeur": 3}},
    {"id": "agent-boucles", "nom": "Agent des boucles", "symbole": "∞",
     "description": "Accomplir 3 missions du thème Boucles.", "condition": {"type": "theme", "theme": "boucles", "valeur": 3}},
    {"id": "specialiste-fonctions", "nom": "Spécialiste des fonctions", "symbole": "ƒ",
     "description": "Accomplir 3 missions du thème Fonctions.", "condition": {"type": "theme", "theme": "fonctions", "valeur": 3}},
    {"id": "maitre-listes", "nom": "Archiviste des listes", "symbole": "[ ]",
     "description": "Accomplir 3 missions du thème Listes.", "condition": {"type": "theme", "theme": "listes", "valeur": 3}},
    {"id": "gardien-dictionnaires", "nom": "Gardien des dictionnaires", "symbole": "{ }",
     "description": "Accomplir 3 missions du thème Dictionnaires.", "condition": {"type": "theme", "theme": "dictionnaires", "valeur": 3}},
    {"id": "decodeur", "nom": "Décodeur", "symbole": "Aa",
     "description": "Accomplir 3 missions du thème Chaînes de caractères.", "condition": {"type": "theme", "theme": "chaines", "valeur": 3}},
    {"id": "demineur", "nom": "Démineur", "symbole": "!",
     "description": "Accomplir 2 missions de gestion des erreurs.", "condition": {"type": "theme", "theme": "exceptions", "valeur": 2}},
    {"id": "chasseur-bugs", "nom": "Chasseur de bugs", "symbole": "⌖",
     "description": "Corriger 2 programmes sabotés (missions de niveau 7).", "condition": {"type": "niveau", "niveau": 7, "valeur": 2}},
    {"id": "code-propre", "nom": "Code propre", "symbole": "✓",
     "description": "Obtenir « Excellent » en qualité de code sur 3 missions.", "condition": {"type": "qualite_excellente", "valeur": 3}},
    {"id": "sans-indice", "nom": "Mission accomplie sans indice", "symbole": "◎",
     "description": "Réussir une mission sans aucun indice.", "condition": {"type": "sans_indice", "valeur": 1}},
    {"id": "serie-5", "nom": "Cinq missions consécutives", "symbole": "5×",
     "description": "Réussir 5 missions d'affilée (en 2 envois maximum, sans révéler la solution).",
     "condition": {"type": "serie", "valeur": 5}},
    {"id": "perseverant", "nom": "Persévérant", "symbole": "↻",
     "description": "Réussir une mission après au moins 3 envois échoués.", "condition": {"type": "perseverance", "valeur": 3}},
    {"id": "createur", "nom": "Stratège", "symbole": "✦",
     "description": "Accomplir 3 missions générées ou créées par toi.", "condition": {"type": "missions_hors_banque", "valeur": 3}},
    {"id": "veteran", "nom": "Vétéran", "symbole": "XV",
     "description": "Accomplir 15 missions.", "condition": {"type": "missions_accomplies", "valeur": 15}},
    {"id": "legende", "nom": "Légende de l'Agence", "symbole": "★",
     "description": "Accomplir 30 missions.", "condition": {"type": "missions_accomplies", "valeur": 30}},
]

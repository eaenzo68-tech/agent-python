"""Fabrique de nouvelles missions, entièrement hors ligne.

Trois services :

1. generer_missions(...)     : crée des variantes à partir de MODÈLES
                               paramétrables (données tirées au hasard,
                               résultats attendus calculés automatiquement) ;
2. analyser_notes(...)       : repère les concepts Python présents dans
                               des notes de cours collées par l'agent ;
3. creer_mission_perso(...)  : transforme le formulaire « Créer ma mission »
                               en vraie mission avec des tests.

Pour ajouter un modèle : écris une fonction `_modele_xxx(rng, difficulte)`
qui renvoie un dictionnaire de mission, puis ajoute-la dans MODELES.
"""

from __future__ import annotations

import ast
import random
import re
import textwrap
from dataclasses import dataclass
from collections.abc import Callable

from core.test_engine import evaluer

DIFFICULTES = ["facile", "intermediaire", "difficile"]
NOMS_AGENTS = ["Faucon", "Lynx", "Cobra", "Orion", "Vega", "Nova", "Corbeau", "Atlas",
               "Sirius", "Écho", "Delta", "Kilo", "Tango", "Bravo", "Mira", "Iris",
               "Ombre", "Fantôme", "Comète", "Sphinx"]
VILLES = ["Neuchâtel", "Genève", "Berne", "Zurich", "Lausanne", "Bâle", "Lugano",
          "Paris", "Berlin", "Vienne", "Prague", "Oslo"]
NOMS_OPERATIONS = ["Aube Grise", "Brume", "Cristal", "Éclipse", "Granit", "Horizon",
                   "Mistral", "Onyx", "Polaris", "Quartz", "Tempête", "Zénith"]


def code(texte: str) -> str:
    """Enlève l'indentation commune d'un bloc de code écrit entre triple guillemets."""
    return textwrap.dedent(texte).strip("\n") + "\n"


def encoder_valeur(valeur):
    """Transforme tuples, ensembles et clés non textuelles en écriture JSON."""
    if isinstance(valeur, tuple):
        return {"__tuple__": [encoder_valeur(v) for v in valeur]}
    if isinstance(valeur, set):
        return {"__set__": [encoder_valeur(v) for v in sorted(valeur, key=repr)]}
    if isinstance(valeur, list):
        return [encoder_valeur(v) for v in valeur]
    if isinstance(valeur, dict):
        if all(isinstance(k, str) for k in valeur):
            return {k: encoder_valeur(v) for k, v in valeur.items()}
        return {"__dict__": [[encoder_valeur(k), encoder_valeur(v)] for k, v in valeur.items()]}
    return valeur


def _test_appel(fonction: str, args: list, attendu, description: str,
                visible: bool = False, **options) -> dict:
    test = {"type": "appel", "fonction": fonction, "args": encoder_valeur(args),
            "attendu": encoder_valeur(attendu), "visible": visible, "description": description}
    test.update(options)
    return test


def _squelette(signature: str, difficulte: str, etapes: list[str], docstring: str) -> str:
    """Code de départ adapté à la difficulté."""
    if difficulte == "facile":
        lignes = [f"def {signature}:", f'    """{docstring}"""']
        lignes += [f"    # {numero}. {etape}" for numero, etape in enumerate(etapes, start=1)]
        lignes.append("    pass  # remplace cette ligne par ton code")
        return "\n".join(lignes) + "\n"
    if difficulte == "intermediaire":
        return f'def {signature}:\n    """{docstring}"""\n    pass\n'
    return f"def {signature}:\n    pass\n"


NIVEAUX = {"facile": 3, "intermediaire": 4, "difficile": 5}


# ---------------------------------------------------------------------------
# Modèles de missions
# ---------------------------------------------------------------------------

def _modele_filtre_seuil(rng: random.Random, difficulte: str) -> dict:
    seuil = rng.randint(40, 75)
    noms = rng.sample(NOMS_AGENTS, 6)
    suspects = [[nom, rng.randint(10, 99)] for nom in noms]
    suspects[rng.randrange(6)][1] = seuil  # au moins un score pile au seuil

    def reference(liste, limite):
        return [nom for nom, score in liste if score >= limite]

    autres = [[nom, rng.randint(10, 99)] for nom in rng.sample(NOMS_AGENTS, 5)]
    tests = [
        _test_appel("suspects_prioritaires", [suspects, seuil], reference(suspects, seuil),
                    "exemple de l'énoncé", visible=True),
        _test_appel("suspects_prioritaires", [autres, 50], reference(autres, 50), "autre liste interceptée"),
        _test_appel("suspects_prioritaires", [[], seuil], [], "liste vide"),
        _test_appel("suspects_prioritaires", [[["Zulu", seuil - 1]], seuil], [], "score juste sous le seuil"),
    ]
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : suspects prioritaires",
        "briefing": "Nos analystes ont attribué un score de risque à chaque suspect. "
                    "L'agence veut la liste des suspects à surveiller en priorité.",
        "objectif": "Parcourir une liste, tester une condition et construire une nouvelle liste.",
        "enonce": "Écris la fonction suspects_prioritaires(suspects, seuil). Chaque suspect est une "
                  "liste [nom, score]. La fonction renvoie la liste des NOMS dont le score est "
                  "supérieur ou égal au seuil, dans l'ordre d'origine.",
        "donnees": f"suspects = {suspects!r}\nseuil = {seuil}",
        "resultat_attendu": f"{reference(suspects, seuil)!r}",
        "elements": "suspects",
        "code_depart": _squelette("suspects_prioritaires(suspects, seuil)", difficulte,
                                  ["crée une liste vide pour le résultat",
                                   "parcours chaque suspect (suspect[0] = nom, suspect[1] = score)",
                                   "si le score est >= seuil, ajoute le nom",
                                   "renvoie la liste"],
                                  "Renvoie les noms des suspects dont le score atteint le seuil."),
        "tests": tests,
        "indices": [
            "Tu dois construire une NOUVELLE liste. Avec quelle valeur commence-t-elle ?",
            "Une boucle for parcourt chaque suspect. suspect[0] est le nom et suspect[1] le score. "
            "Une condition if décide si on ajoute le nom avec append().",
            "Structure type :\nresultat = []\nfor element in liste:\n    if condition_sur(element):\n"
            "        resultat.append(...)\nreturn resultat\nAttention : « supérieur ou égal » s'écrit >=.",
        ],
        "solution": code('''
            def suspects_prioritaires(suspects, seuil):
                """Renvoie les noms des suspects dont le score atteint le seuil."""
                prioritaires = []
                for suspect in suspects:
                    nom = suspect[0]
                    score = suspect[1]
                    if score >= seuil:
                        prioritaires.append(nom)
                return prioritaires
        '''),
        "explication": "C'est le schéma « filtrer » : on part d'une liste vide, on parcourt chaque "
                       "élément et on n'ajoute que ceux qui respectent la condition. "
                       "Le test « score juste sous le seuil » vérifie que tu as bien utilisé >= et non >.",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_compte_lettre(rng, difficulte):
    lettre = rng.choice("aeiorst")
    message = rng.choice([
        "Rendez-vous a la gare de Neuchatel a minuit",
        "Le colis est arrive au port sans incident",
        "Attention agent double repere dans le secteur est",
        "Transmission securisee terminee retour a la base",
    ])

    def reference(texte, symbole):
        return texte.lower().count(symbole.lower())

    tests = [
        _test_appel("compter_signal", [message, lettre], reference(message, lettre), "exemple de l'énoncé", True),
        _test_appel("compter_signal", ["", lettre], 0, "message vide"),
        _test_appel("compter_signal", ["AAA bbb Aa", "a"], 5, "majuscules et minuscules"),
        _test_appel("compter_signal", ["xyz", lettre], 0, "lettre absente"),
    ]
    if difficulte == "difficile":
        tests.append({"type": "structure", "interdit": ["count"], "visible": True,
                      "description": "sans utiliser count()"})
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : signal répété",
        "briefing": "Un message intercepté cache un signal : le nombre d'apparitions d'une lettre "
                    "donne le code d'accès.",
        "objectif": "Parcourir une chaîne de caractères et compter avec une variable.",
        "enonce": "Écris compter_signal(message, lettre) qui renvoie combien de fois la lettre "
                  "apparaît dans le message, SANS tenir compte des majuscules/minuscules."
                  + (" Interdiction d'utiliser count()." if difficulte == "difficile" else ""),
        "donnees": f"message = {message!r}\nlettre = {lettre!r}",
        "resultat_attendu": str(reference(message, lettre)),
        "code_depart": _squelette("compter_signal(message, lettre)", difficulte,
                                  ["crée un compteur à 0", "parcours chaque caractère du message",
                                   "compare-le à la lettre (en minuscules)", "renvoie le compteur"],
                                  "Compte les apparitions de lettre dans message."),
        "tests": tests,
        "indices": [
            "Pour compter, de quelle variable as-tu besoin avant la boucle ?",
            "for caractere in message: parcourt le texte lettre par lettre. "
            "caractere.lower() met en minuscule. Un compteur augmente avec compteur += 1.",
            "Exemple similaire (compter les espaces) :\nnb = 0\nfor c in texte:\n    if c == \" \":\n"
            "        nb += 1\nreturn nb\nPense à comparer les deux lettres en minuscules.",
        ],
        "solution": code('''
            def compter_signal(message, lettre):
                """Compte les apparitions de lettre dans message (sans tenir compte de la casse)."""
                compteur = 0
                for caractere in message:
                    if caractere.lower() == lettre.lower():
                        compteur += 1
                return compteur
        '''),
        "explication": "Une chaîne se parcourt comme une liste. Le compteur commence à 0 et augmente "
                       "à chaque correspondance. lower() permet d'ignorer les majuscules.",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_somme_filtre(rng, difficulte):
    limite = rng.choice([500, 1000, 2000])
    montants = [rng.choice([rng.randint(50, limite - 1), rng.randint(limite + 1, limite * 3)]) for _ in range(6)]
    montants[rng.randrange(6)] = limite

    def reference(valeurs, seuil):
        return sum(v for v in valeurs if v > seuil)

    autres = [rng.randint(100, 5000) for _ in range(7)]
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : transferts suspects",
        "briefing": "Des virements anonymes circulent. Seuls les montants STRICTEMENT supérieurs "
                    "à la limite légale intéressent l'agence.",
        "objectif": "Combiner une boucle et une condition pour faire une somme filtrée.",
        "enonce": "Écris total_suspect(montants, limite) qui renvoie la somme des montants "
                  "strictement supérieurs à limite.",
        "donnees": f"montants = {montants!r}\nlimite = {limite}",
        "resultat_attendu": str(reference(montants, limite)),
        "code_depart": _squelette("total_suspect(montants, limite)", difficulte,
                                  ["crée une variable total à 0", "parcours les montants",
                                   "ajoute le montant au total s'il dépasse la limite", "renvoie le total"],
                                  "Somme des montants strictement supérieurs à limite."),
        "tests": [
            _test_appel("total_suspect", [montants, limite], reference(montants, limite), "exemple de l'énoncé", True),
            _test_appel("total_suspect", [autres, 1000], reference(autres, 1000), "autres virements"),
            _test_appel("total_suspect", [[], limite], 0, "aucun virement"),
            _test_appel("total_suspect", [[limite, limite], limite], 0, "montants égaux à la limite"),
        ],
        "indices": [
            "« Strictement supérieur » : quel opérateur de comparaison faut-il ?",
            "Un accumulateur commence à 0. Dans la boucle, on écrit total += montant, mais seulement "
            "si la condition est vraie.",
            "Exemple (somme des nombres pairs) :\ntotal = 0\nfor n in nombres:\n    if n % 2 == 0:\n"
            "        total += n\nreturn total",
        ],
        "solution": code('''
            def total_suspect(montants, limite):
                """Somme des montants strictement supérieurs à limite."""
                total = 0
                for montant in montants:
                    if montant > limite:
                        total += montant
                return total
        '''),
        "explication": "Accumulateur + condition : le schéma de base de l'analyse de données. "
                       "Le test « montants égaux à la limite » vérifie l'usage de > (strict).",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_maximum(rng, difficulte):
    niveaux = rng.sample(range(1, 100), 7)

    def reference(valeurs):
        return max(valeurs) if valeurs else None

    tests = [
        _test_appel("menace_maximale", [niveaux], reference(niveaux), "exemple de l'énoncé", True),
        _test_appel("menace_maximale", [[-5, -2, -9]], -2, "valeurs négatives"),
        _test_appel("menace_maximale", [[42]], 42, "une seule valeur"),
        _test_appel("menace_maximale", [[]], None, "liste vide"),
    ]
    if difficulte != "facile":
        tests.append({"type": "structure", "interdit": ["max", "sorted", "sort"], "visible": True,
                      "description": "sans max(), sorted() ni sort()"})
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : menace maximale",
        "briefing": "Chaque secteur transmet un niveau de menace. Le commandement doit connaître "
                    "le niveau le plus élevé, sans faire confiance aux outils automatiques.",
        "objectif": "Trouver un maximum « à la main » avec une boucle.",
        "enonce": "Écris menace_maximale(niveaux) qui renvoie la plus grande valeur de la liste, "
                  "ou None si la liste est vide."
                  + (" Interdiction d'utiliser max(), sorted() ou sort()." if difficulte != "facile" else ""),
        "donnees": f"niveaux = {niveaux!r}",
        "resultat_attendu": str(reference(niveaux)),
        "code_depart": _squelette("menace_maximale(niveaux)", difficulte,
                                  ["si la liste est vide, renvoie None",
                                   "garde le premier élément comme « meilleur » provisoire",
                                   "parcours la liste et remplace le meilleur si tu trouves plus grand",
                                   "renvoie le meilleur"],
                                  "Renvoie le plus grand niveau, ou None si la liste est vide."),
        "tests": tests,
        "indices": [
            "Par quelle valeur commencer ? (Attention : 0 ne marche pas si toutes les valeurs sont négatives.)",
            "Commence avec le premier élément : meilleur = niveaux[0]. Puis compare chaque valeur "
            "avec meilleur et remplace-le si elle est plus grande.",
            "Exemple (le plus petit) :\nif not valeurs:\n    return None\nplus_petit = valeurs[0]\n"
            "for v in valeurs:\n    if v < plus_petit:\n        plus_petit = v\nreturn plus_petit",
        ],
        "solution": code('''
            def menace_maximale(niveaux):
                """Renvoie le plus grand niveau, ou None si la liste est vide."""
                if not niveaux:
                    return None
                maximum = niveaux[0]
                for niveau in niveaux:
                    if niveau > maximum:
                        maximum = niveau
                return maximum
        '''),
        "explication": "On garde en mémoire le « meilleur » trouvé jusqu'ici. Commencer par le premier "
                       "élément (et non par 0) rend la fonction correcte même avec des nombres négatifs.",
        "niveau": NIVEAUX[difficulte] + (1 if difficulte != "facile" else 0),
    }


def _modele_inverser_annuaire(rng, difficulte):
    noms = rng.sample(NOMS_AGENTS, 4)
    codes = rng.sample(range(10, 99), 4)
    annuaire = {nom: f"X{c}" for nom, c in zip(noms, codes)}

    def reference(dico):
        return {valeur: cle for cle, valeur in dico.items()}

    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : annuaire inversé",
        "briefing": "L'annuaire associe chaque agent à son code radio. Sur le terrain, on entend "
                    "les codes : il faut retrouver l'agent à partir du code.",
        "objectif": "Parcourir un dictionnaire et en construire un nouveau.",
        "enonce": "Écris inverser_annuaire(annuaire) qui renvoie un NOUVEAU dictionnaire "
                  "{code: nom} à partir du dictionnaire {nom: code}.",
        "donnees": f"annuaire = {annuaire!r}",
        "resultat_attendu": repr(reference(annuaire)),
        "code_depart": _squelette("inverser_annuaire(annuaire)", difficulte,
                                  ["crée un dictionnaire vide", "parcours les paires (nom, code) avec .items()",
                                   "ajoute l'entrée inversée", "renvoie le nouveau dictionnaire"],
                                  "Renvoie le dictionnaire {code: nom}."),
        "tests": [
            _test_appel("inverser_annuaire", [annuaire], reference(annuaire), "exemple de l'énoncé", True),
            _test_appel("inverser_annuaire", [{}], {}, "annuaire vide"),
            _test_appel("inverser_annuaire", [{"Iris": "Z1"}], {"Z1": "Iris"}, "un seul agent"),
        ],
        "indices": [
            "Le résultat est un dictionnaire : par quoi commence-t-il ?",
            "for nom, code in annuaire.items(): donne chaque paire. On ajoute une entrée avec "
            "nouveau[cle] = valeur.",
            "Exemple (doubler les valeurs) :\nresultat = {}\nfor cle, valeur in d.items():\n"
            "    resultat[cle] = valeur * 2\nreturn resultat\nIci, c'est la clé et la valeur qui échangent leur place.",
        ],
        "solution": code('''
            def inverser_annuaire(annuaire):
                """Renvoie le dictionnaire {code: nom}."""
                inverse = {}
                for nom, code_radio in annuaire.items():
                    inverse[code_radio] = nom
                return inverse
        '''),
        "explication": ".items() donne les paires (clé, valeur). On crée chaque entrée inversée avec "
                       "inverse[valeur] = clé. Le dictionnaire d'origine n'est pas modifié.",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_frequences(rng, difficulte):
    villes = rng.sample(VILLES, 3)
    signalements = [rng.choice(villes) for _ in range(8)]

    def reference(liste):
        resultat = {}
        for v in liste:
            resultat[v] = resultat.get(v, 0) + 1
        return resultat

    tests = [
        _test_appel("compter_villes", [signalements], reference(signalements), "exemple de l'énoncé", True),
        _test_appel("compter_villes", [[]], {}, "aucun signalement"),
        _test_appel("compter_villes", [["Berne"] * 3], {"Berne": 3}, "toujours la même ville"),
    ]
    if difficulte == "difficile":
        tests.append({"type": "structure", "interdit": ["count", "Counter"], "visible": True,
                      "description": "sans count() ni Counter"})
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : carte des signalements",
        "briefing": "Des agents ont signalé des activités suspectes dans plusieurs villes. "
                    "Combien de signalements par ville ?",
        "objectif": "Compter des occurrences avec un dictionnaire.",
        "enonce": "Écris compter_villes(signalements) qui renvoie un dictionnaire {ville: nombre}.",
        "donnees": f"signalements = {signalements!r}",
        "resultat_attendu": repr(reference(signalements)),
        "code_depart": _squelette("compter_villes(signalements)", difficulte,
                                  ["crée un dictionnaire vide", "parcours les villes",
                                   "si la ville est déjà une clé, ajoute 1 ; sinon crée-la avec 1",
                                   "renvoie le dictionnaire"],
                                  "Compte les signalements par ville."),
        "tests": tests,
        "indices": [
            "Que faut-il faire la PREMIÈRE fois qu'on rencontre une ville ? Et les fois suivantes ?",
            "« if ville in compteur: » teste si la clé existe. Sinon, on la crée avec la valeur 1.",
            "Raccourci utile : compteur[cle] = compteur.get(cle, 0) + 1\nget renvoie 0 si la clé n'existe pas encore.",
        ],
        "solution": code('''
            def compter_villes(signalements):
                """Compte les signalements par ville."""
                compteur = {}
                for ville in signalements:
                    if ville in compteur:
                        compteur[ville] += 1
                    else:
                        compteur[ville] = 1
                return compteur
        '''),
        "explication": "Le dictionnaire « compteur » est un grand classique : la clé est l'objet compté, "
                       "la valeur le nombre d'apparitions. dict.get(cle, 0) évite le test if/else.",
        "niveau": NIVEAUX[difficulte] + 1,
    }


def _modele_cesar(rng, difficulte):
    decalage = rng.randint(1, 5)
    clair = rng.choice(["rendez vous au pont", "mission accomplie", "la cle est sous le banc",
                        "objectif localise", "extraction a minuit"])

    def chiffrer(texte, d):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        return "".join(alphabet[(alphabet.index(c) + d) % 26] if c in alphabet else c for c in texte)

    chiffre = chiffrer(clair, decalage)
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : code César",
        "briefing": f"L'ennemi utilise un code César : chaque lettre est décalée de {decalage} rangs "
                    "dans l'alphabet. Décode ses messages.",
        "objectif": "Parcourir une chaîne et construire une nouvelle chaîne lettre par lettre.",
        "enonce": "Écris dechiffrer(message, decalage) qui recule chaque lettre minuscule de "
                  "« decalage » rangs (a recule vers z). Les autres caractères restent identiques.",
        "donnees": f"message = {chiffre!r}\ndecalage = {decalage}",
        "resultat_attendu": repr(clair),
        "code_depart": (_squelette("dechiffrer(message, decalage)", difficulte,
                                   ["crée une chaîne vide pour le résultat",
                                    "pour chaque caractère : s'il est dans l'alphabet, trouve sa position "
                                    "avec alphabet.index(c), recule et ajoute la nouvelle lettre",
                                    "sinon, ajoute le caractère tel quel", "renvoie le résultat"],
                                   "Décode un message chiffré avec le code César.")
                        .replace("def dechiffrer", 'ALPHABET = "abcdefghijklmnopqrstuvwxyz"\n\n\ndef dechiffrer')),
        "tests": [
            _test_appel("dechiffrer", [chiffre, decalage], clair, "exemple de l'énoncé", True),
            _test_appel("dechiffrer", ["bcd", 1], "abc", "décalage simple"),
            _test_appel("dechiffrer", ["abc", 3], "xyz", "retour au début de l'alphabet"),
            _test_appel("dechiffrer", ["", 2], "", "message vide"),
            _test_appel("dechiffrer", ["d-e!f", 3], "a-b!c", "ponctuation conservée"),
        ],
        "indices": [
            "Comment trouver la position d'une lettre dans l'alphabet ? Et comment revenir à z après a ?",
            "ALPHABET.index(c) donne la position. Le modulo % 26 fait « boucler » l'alphabet : "
            "(0 - 3) % 26 vaut 23.",
            "Exemple (avancer d'un rang) :\nresultat = \"\"\nfor c in texte:\n    if c in ALPHABET:\n"
            "        pos = (ALPHABET.index(c) + 1) % 26\n        resultat += ALPHABET[pos]\n    else:\n"
            "        resultat += c",
        ],
        "solution": code('''
            ALPHABET = "abcdefghijklmnopqrstuvwxyz"


            def dechiffrer(message, decalage):
                """Décode un message chiffré avec le code César."""
                resultat = ""
                for caractere in message:
                    if caractere in ALPHABET:
                        position = (ALPHABET.index(caractere) - decalage) % len(ALPHABET)
                        resultat += ALPHABET[position]
                    else:
                        resultat += caractere
                return resultat
        '''),
        "explication": "Le modulo (%) ramène toute position dans l'intervalle 0..25 : c'est ce qui "
                       "permet de passer de « a » à « x » en reculant. Une chaîne étant immuable, "
                       "on construit le résultat morceau par morceau.",
        "niveau": NIVEAUX[difficulte] + 1,
    }


def _modele_conversion_sure(rng, difficulte):
    textes = [str(rng.randint(1, 999)) for _ in range(4)]
    for intrus in rng.sample(["7B", "abc", "", "4.5", "N/A"], 2):
        textes.insert(rng.randrange(len(textes) + 1), intrus)

    def reference(liste):
        resultat = []
        for t in liste:
            try:
                resultat.append(int(t))
            except ValueError:
                pass
        return resultat

    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : codes corrompus",
        "briefing": "Le fichier des codes d'accès a été endommagé. Certaines valeurs ne sont plus "
                    "des nombres. Récupère tout ce qui peut l'être, sans faire planter le programme.",
        "objectif": "Utiliser try / except pour gérer une conversion qui peut échouer.",
        "enonce": "Écris codes_valides(textes) qui renvoie la liste des textes convertibles en int "
                  "(convertis), en ignorant les autres. Utilise try / except ValueError.",
        "donnees": f"textes = {textes!r}",
        "resultat_attendu": repr(reference(textes)),
        "code_depart": _squelette("codes_valides(textes)", difficulte,
                                  ["crée une liste vide", "pour chaque texte, ESSAIE de le convertir avec int()",
                                   "si ça marche, ajoute le nombre ; si ValueError, ignore-le",
                                   "renvoie la liste"],
                                  "Convertit les textes valides en entiers."),
        "tests": [
            _test_appel("codes_valides", [textes], reference(textes), "exemple de l'énoncé", True),
            _test_appel("codes_valides", [["x", "y"]], [], "aucun code valide"),
            _test_appel("codes_valides", [["-5", "12"]], [-5, 12], "nombres négatifs"),
            _test_appel("codes_valides", [[]], [], "liste vide"),
            {"type": "structure", "doit_utiliser": ["try"], "visible": True,
             "description": "utilise try / except"},
        ],
        "indices": [
            "Que se passe-t-il quand on écrit int(\"abc\") ? Comment empêcher le programme de s'arrêter ?",
            "try: contient l'instruction risquée ; except ValueError: contient ce qu'on fait en cas d'échec "
            "(ici : rien, avec pass, ou continue).",
            "Exemple :\ntry:\n    nombre = float(texte)\n    valeurs.append(nombre)\nexcept ValueError:\n"
            "    pass   # on ignore ce texte",
        ],
        "solution": code('''
            def codes_valides(textes):
                """Convertit les textes valides en entiers et ignore les autres."""
                codes = []
                for texte in textes:
                    try:
                        codes.append(int(texte))
                    except ValueError:
                        pass  # texte illisible : on l'ignore
                return codes
        '''),
        "explication": "try / except permet de prévoir un « plan B » quand une instruction peut échouer. "
                       "On attrape précisément ValueError : une autre erreur (bug) resterait visible.",
        "niveau": NIVEAUX[difficulte] + 1,
    }


def _modele_moyenne(rng, difficulte):
    notes = [rng.randint(2, 10) for _ in range(rng.randint(4, 7))]

    def reference(valeurs):
        return round(sum(valeurs) / len(valeurs), 1) if valeurs else 0

    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : fiabilité des informateurs",
        "briefing": "Chaque informateur reçoit des notes de fiabilité sur 10. L'agence veut la moyenne.",
        "objectif": "Écrire une fonction complète qui gère aussi le cas particulier de la liste vide.",
        "enonce": "Écris moyenne_fiabilite(notes) qui renvoie la moyenne arrondie à 1 décimale "
                  "(round(valeur, 1)). Si la liste est vide, renvoie 0.",
        "donnees": f"notes = {notes!r}",
        "resultat_attendu": str(reference(notes)),
        "code_depart": _squelette("moyenne_fiabilite(notes)", difficulte,
                                  ["si la liste est vide, renvoie 0", "calcule la somme des notes",
                                   "divise par le nombre de notes", "arrondis à 1 décimale et renvoie"],
                                  "Moyenne des notes arrondie à 1 décimale (0 si aucune note)."),
        "tests": [
            _test_appel("moyenne_fiabilite", [notes], reference(notes), "exemple de l'énoncé", True, tolerance=0.05),
            _test_appel("moyenne_fiabilite", [[7, 8]], 7.5, "deux notes", tolerance=0.05),
            _test_appel("moyenne_fiabilite", [[]], 0, "aucune note"),
            _test_appel("moyenne_fiabilite", [[10, 9, 9]], 9.3, "arrondi", tolerance=0.05),
        ],
        "indices": [
            "Quelles sont les deux informations nécessaires pour calculer une moyenne ?",
            "sum(notes) donne la somme et len(notes) le nombre de notes. Attention : diviser par "
            "len([]) provoque une division par zéro.",
            "Exemple :\nif len(valeurs) == 0:\n    return 0\nresultat = sum(valeurs) / len(valeurs)\n"
            "return round(resultat, 1)",
        ],
        "solution": code('''
            def moyenne_fiabilite(notes):
                """Moyenne des notes arrondie à 1 décimale (0 si aucune note)."""
                if len(notes) == 0:
                    return 0
                moyenne = sum(notes) / len(notes)
                return round(moyenne, 1)
        '''),
        "explication": "Une bonne fonction prévoit les cas particuliers AVANT le calcul principal. "
                       "Sans le test de la liste vide, len(notes) vaudrait 0 et Python lèverait "
                       "ZeroDivisionError.",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_categorie(rng, difficulte):
    bas = rng.randint(30, 45)
    haut = rng.randint(60, 80)

    def reference(score):
        if score < bas:
            return "faible"
        if score < haut:
            return "moyen"
        return "élevé"

    exemples = [rng.randint(0, bas - 1), rng.randint(bas, haut - 1), rng.randint(haut, 100)]
    tests = [_test_appel("niveau_risque", [s], reference(s), f"score {s}", visible=(i == 0))
             for i, s in enumerate(exemples)]
    tests += [
        _test_appel("niveau_risque", [bas], "moyen", "score pile sur la première limite"),
        _test_appel("niveau_risque", [haut], "élevé", "score pile sur la deuxième limite"),
    ]
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : niveau de risque",
        "briefing": "Le système d'alerte classe chaque situation selon un score de 0 à 100.",
        "objectif": "Écrire une suite de conditions if / elif / else.",
        "enonce": f"Écris niveau_risque(score) qui renvoie « faible » si score < {bas}, "
                  f"« moyen » si {bas} <= score < {haut}, et « élevé » sinon.",
        "donnees": f"Exemples : niveau_risque({exemples[0]}) → {reference(exemples[0])!r}",
        "resultat_attendu": "'faible', 'moyen' ou 'élevé' (avec les accents)",
        "code_depart": _squelette("niveau_risque(score)", difficulte,
                                  [f"si score < {bas} : renvoie 'faible'",
                                   f"sinon, si score < {haut} : renvoie 'moyen'",
                                   "sinon : renvoie 'élevé'"],
                                  "Classe un score de risque."),
        "tests": tests,
        "indices": [
            "Combien de cas différents y a-t-il ? Dans quel ordre les tester ?",
            "if / elif / else teste les conditions dans l'ordre : dès qu'une est vraie, "
            "les suivantes sont ignorées.",
            f"Structure :\nif score < {bas}:\n    return ...\nelif ...:\n    return ...\nelse:\n    return ...\n"
            "Vérifie les cas « pile sur la limite ».",
        ],
        "solution": code(f'''
            def niveau_risque(score):
                """Classe un score de risque."""
                if score < {bas}:
                    return "faible"
                elif score < {haut}:
                    return "moyen"
                else:
                    return "élevé"
        '''),
        "explication": "Avec elif, la deuxième condition n'est testée que si la première est fausse : "
                       f"inutile d'écrire « score >= {bas} and score < {haut} ».",
        "niveau": NIVEAUX[difficulte] - 1,
    }


def _modele_calcul_variables(rng, difficulte):
    agents, rations, jours = rng.randint(3, 9), rng.randint(2, 4), rng.randint(3, 10)
    total = agents * rations * jours
    if difficulte == "facile":
        depart = (f"agents = {agents}\nrations_par_jour = {rations}\njours = {jours}\n\n"
                  "total_rations = ...  # complète cette ligne\n"
                  'print(f"Rations nécessaires : {total_rations}")\n')
        niveau = 1
    else:
        depart = (f'agents_texte = "{agents}"\nrations_par_jour = {rations}\njours_texte = "{jours}"\n\n'
                  "# Les valeurs reçues par radio sont du TEXTE : convertis-les avant de calculer.\n")
        niveau = 2
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : ravitaillement",
        "briefing": "Une équipe part en planque. Calcule le nombre de rations à préparer.",
        "objectif": "Créer une variable à partir d'un calcul et l'afficher."
                    + (" Convertir du texte en nombre." if difficulte != "facile" else ""),
        "enonce": "Crée la variable total_rations = agents × rations par jour × jours, puis affiche "
                  "exactement : Rations nécessaires : <total>",
        "donnees": depart,
        "resultat_attendu": f"Rations nécessaires : {total}",
        "code_depart": depart,
        "tests": [
            {"type": "variable", "nom": "total_rations", "attendu": total, "visible": True,
             "description": "valeur de total_rations"},
            {"type": "sortie", "attendu": f"Rations nécessaires : {total}\n", "visible": True,
             "description": "affichage"},
        ],
        "indices": [
            "Quelle opération combine les trois valeurs ?",
            "La multiplication s'écrit *. " + ("Le texte \"4\" se convertit en nombre avec int(\"4\")."
                                               if difficulte != "facile" else "Le résultat se range avec =."),
            "Exemple :\nprix = 3\nquantite = 4\ncout = prix * quantite\nprint(f\"Coût : {cout}\")",
        ],
        "solution": (f"agents = {agents}\nrations_par_jour = {rations}\njours = {jours}\n\n"
                     "total_rations = agents * rations_par_jour * jours\n"
                     'print(f"Rations nécessaires : {total_rations}")\n')
        if difficulte == "facile" else
        (f'agents_texte = "{agents}"\nrations_par_jour = {rations}\njours_texte = "{jours}"\n\n'
         "agents = int(agents_texte)\njours = int(jours_texte)\n"
         "total_rations = agents * rations_par_jour * jours\n"
         'print(f"Rations nécessaires : {total_rations}")\n'),
        "explication": "Une variable range le résultat d'un calcul pour le réutiliser. Les f-strings "
                       "(f\"...{variable}...\") insèrent une valeur dans un texte.",
        "niveau": niveau,
    }


def _modele_recherche_while(rng, difficulte):
    codes = rng.sample(range(100, 999), 6)
    cible = rng.choice(codes)

    def reference(liste, valeur):
        return liste.index(valeur) if valeur in liste else -1

    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : recherche de fréquence",
        "briefing": "Le scanner parcourt les fréquences une par une et doit s'arrêter dès que la "
                    "bonne est trouvée.",
        "objectif": "Utiliser une boucle while avec un indice et une condition d'arrêt.",
        "enonce": "Écris position_code(codes, cible) qui renvoie la position (indice) de la cible "
                  "dans la liste, ou -1 si elle n'y est pas. Utilise une boucle while.",
        "donnees": f"codes = {codes!r}\ncible = {cible}",
        "resultat_attendu": str(reference(codes, cible)),
        "code_depart": _squelette("position_code(codes, cible)", difficulte,
                                  ["crée un indice à 0",
                                   "tant que l'indice est valide (< len(codes)) :",
                                   "   si codes[indice] == cible, renvoie l'indice ; sinon augmente l'indice",
                                   "après la boucle, renvoie -1"],
                                  "Renvoie la position de cible, ou -1."),
        "tests": [
            _test_appel("position_code", [codes, cible], reference(codes, cible), "exemple de l'énoncé", True),
            _test_appel("position_code", [codes, codes[0]], 0, "cible en première position"),
            _test_appel("position_code", [codes, 1000], -1, "cible absente"),
            _test_appel("position_code", [[], 5], -1, "liste vide"),
            {"type": "structure", "doit_utiliser": ["while"], "visible": True,
             "description": "utilise une boucle while"},
        ],
        "indices": [
            "Quand la boucle doit-elle s'arrêter ? (Deux raisons possibles.)",
            "while indice < len(codes): évite de sortir de la liste. N'oublie pas indice += 1, "
            "sinon la boucle ne s'arrête jamais.",
            "Exemple :\ni = 0\nwhile i < len(mots):\n    if mots[i] == \"stop\":\n        return i\n"
            "    i += 1\nreturn -1",
        ],
        "solution": code('''
            def position_code(codes, cible):
                """Renvoie la position de cible, ou -1 si elle est absente."""
                indice = 0
                while indice < len(codes):
                    if codes[indice] == cible:
                        return indice
                    indice += 1
                return -1
        '''),
        "explication": "La boucle while est idéale quand on ne sait pas à l'avance combien de tours "
                       "faire. Le return à l'intérieur arrête la fonction dès que la cible est trouvée.",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_print_return(rng, difficulte):
    variante = rng.choice([
        ("convertir_en_secondes", "minutes", "la durée en secondes", "minutes * 60", lambda x: x * 60),
        ("distance_en_metres", "kilometres", "la distance en mètres", "kilometres * 1000", lambda x: x * 1000),
        ("prime_de_mission", "jours", "la prime (150 CHF par jour)", "jours * 150", lambda x: x * 150),
    ])
    nom, parametre, quoi, formule, reference = variante
    valeurs = rng.sample(range(2, 30), 3)
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : renvoyer, pas afficher",
        "briefing": "Le système automatique de l'agence appelle ta fonction et utilise sa valeur. "
                    "Une valeur seulement affichée est perdue pour lui.",
        "objectif": "Comprendre la différence entre print() et return.",
        "enonce": f"Écris {nom}({parametre}) qui RENVOIE {quoi}. La fonction ne doit rien afficher.",
        "donnees": f"{nom}({valeurs[0]}) doit renvoyer {reference(valeurs[0])}",
        "resultat_attendu": str(reference(valeurs[0])),
        "code_depart": f"def {nom}({parametre}):\n    print({formule})  # ← l'agence ne peut pas récupérer cette valeur !\n",
        "tests": [_test_appel(nom, [v], reference(v), f"{parametre} = {v}", visible=(i == 0))
                  for i, v in enumerate(valeurs)]
        + [{"type": "structure", "doit_utiliser": ["return"], "visible": True, "description": "utilise return"}],
        "indices": [
            "Que renvoie une fonction qui n'a pas de return ?",
            "print() montre une valeur à l'écran. return la donne au programme qui a appelé la fonction.",
            "Exemple :\ndef double(n):\n    return n * 2\n\nresultat = double(4)  # resultat vaut 8",
        ],
        "solution": f"def {nom}({parametre}):\n    return {formule}\n",
        "explication": "return termine la fonction et transmet la valeur. On peut ensuite la stocker, "
                       "la comparer ou l'afficher. print() ne sert qu'à montrer quelque chose à l'humain.",
        "niveau": 3,
        "revision_pour": ["print_return", "retour_none"],
    }


def _modele_dict_get(rng, difficulte):
    noms = rng.sample(NOMS_AGENTS, 4)
    bases = {nom: rng.choice(VILLES) for nom in noms}
    absent = next(n for n in NOMS_AGENTS if n not in bases)
    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : base introuvable",
        "briefing": "Le registre des bases n'est pas complet. Une recherche sur un agent inconnu "
                    "ne doit jamais faire planter le système.",
        "objectif": "Lire un dictionnaire sans provoquer de KeyError.",
        "enonce": "Écris base_de(bases, nom) qui renvoie la ville de l'agent, ou « INCONNUE » "
                  "s'il n'est pas dans le dictionnaire.",
        "donnees": f"bases = {bases!r}",
        "resultat_attendu": f"base_de(bases, {noms[0]!r}) → {bases[noms[0]]!r}",
        "code_depart": _squelette("base_de(bases, nom)", difficulte,
                                  ["vérifie si nom est une clé du dictionnaire (in)",
                                   "si oui, renvoie la ville", "sinon, renvoie 'INCONNUE'"],
                                  "Renvoie la base d'un agent, ou 'INCONNUE'."),
        "tests": [
            _test_appel("base_de", [bases, noms[0]], bases[noms[0]], "agent connu", True),
            _test_appel("base_de", [bases, absent], "INCONNUE", "agent absent", True),
            _test_appel("base_de", [{}, "Lynx"], "INCONNUE", "registre vide"),
            _test_appel("base_de", [bases, noms[-1]], bases[noms[-1]], "dernier agent"),
        ],
        "indices": [
            "Que se passe-t-il si tu écris bases[nom] et que nom n'existe pas ?",
            "« if nom in bases: » vérifie qu'une clé existe. La méthode get() fait la même chose en une ligne.",
            "Exemple :\nscores = {\"Lynx\": 12}\nprint(scores.get(\"Orion\", 0))   # affiche 0, sans erreur",
        ],
        "solution": code('''
            def base_de(bases, nom):
                """Renvoie la base d'un agent, ou 'INCONNUE'."""
                return bases.get(nom, "INCONNUE")
        '''),
        "explication": "dict.get(cle, defaut) renvoie la valeur si la clé existe, sinon la valeur par "
                       "défaut. C'est équivalent à un if cle in dico / else, en plus court.",
        "niveau": NIVEAUX[difficulte] - 1,
        "revision_pour": ["cle"],
    }


def _modele_nettoyage(rng, difficulte):
    bruts = ["  lynx ", "ORION", "", "vega  ", "   ", "nova"]
    rng.shuffle(bruts)

    def reference(liste):
        return [n.strip().capitalize() for n in liste if n.strip()]

    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : données sales",
        "briefing": "Les noms de code saisis à la main sont pleins d'espaces et de majuscules "
                    "aléatoires. Certains champs sont vides.",
        "objectif": "Utiliser les méthodes de chaînes strip() et capitalize() dans une boucle.",
        "enonce": "Écris nettoyer_noms(noms) qui renvoie une nouvelle liste : chaque nom sans espaces "
                  "autour, avec seulement la première lettre en majuscule. Les noms vides sont ignorés.",
        "donnees": f"noms = {bruts!r}",
        "resultat_attendu": repr(reference(bruts)),
        "code_depart": _squelette("nettoyer_noms(noms)", difficulte,
                                  ["crée une liste vide", "pour chaque nom, enlève les espaces avec strip()",
                                   "si le nom n'est pas vide, ajoute nom.capitalize()", "renvoie la liste"],
                                  "Nettoie une liste de noms."),
        "tests": [
            _test_appel("nettoyer_noms", [bruts], reference(bruts), "exemple de l'énoncé", True),
            _test_appel("nettoyer_noms", [[]], [], "liste vide"),
            _test_appel("nettoyer_noms", [["  ", ""]], [], "uniquement des vides"),
            _test_appel("nettoyer_noms", [["cOBRA"]], ["Cobra"], "majuscules mélangées"),
        ],
        "elements": "noms",
        "indices": [
            "Dans quel ordre faut-il faire les opérations : tester si c'est vide, puis nettoyer, ou l'inverse ?",
            "\"  ab \".strip() donne \"ab\". \"aBC\".capitalize() donne \"Abc\". Une chaîne vide est « fausse » "
            "dans un if.",
            "Exemple :\npropres = []\nfor mot in mots:\n    mot = mot.strip()\n    if mot:\n"
            "        propres.append(mot.upper())\nreturn propres",
        ],
        "solution": code('''
            def nettoyer_noms(noms):
                """Nettoie une liste de noms : espaces retirés, majuscule initiale, vides ignorés."""
                propres = []
                for nom in noms:
                    nom = nom.strip()
                    if nom:
                        propres.append(nom.capitalize())
                return propres
        '''),
        "explication": "strip() d'abord : sinon un nom composé seulement d'espaces semblerait non vide. "
                       "Les méthodes de chaînes renvoient une NOUVELLE chaîne, il faut récupérer le résultat.",
        "niveau": NIVEAUX[difficulte],
    }


def _modele_compte_rebours(rng, difficulte):
    valeurs = rng.sample(range(2, 7), 2)

    def sortie(n):
        return "".join(f"{i}\n" for i in range(n, 0, -1)) + "Décollage !\n"

    return {
        "titre": f"Opération {rng.choice(NOMS_OPERATIONS)} : compte à rebours",
        "briefing": "Le drone de reconnaissance décolle après un compte à rebours dont la durée est "
                    "transmise par radio.",
        "objectif": "Lire une entrée avec input(), la convertir et répéter avec une boucle.",
        "enonce": "Lis un nombre n avec input(), affiche les nombres de n jusqu'à 1 (un par ligne), "
                  "puis « Décollage ! ».",
        "donnees": f"Entrée : {valeurs[0]}",
        "resultat_attendu": sortie(valeurs[0]).strip(),
        "code_depart": ("n = int(input())\n# Affiche le compte à rebours ici\n"
                        if difficulte == "facile" else "# Lis n avec input(), puis affiche le compte à rebours\n"),
        "tests": [
            {"type": "sortie", "entrees": [str(valeurs[0])], "attendu": sortie(valeurs[0]),
             "visible": True, "description": f"n = {valeurs[0]}"},
            {"type": "sortie", "entrees": [str(valeurs[1])], "attendu": sortie(valeurs[1]),
             "description": f"n = {valeurs[1]}"},
            {"type": "sortie", "entrees": ["1"], "attendu": sortie(1), "description": "n = 1"},
        ],
        "indices": [
            "input() renvoie toujours un texte. Que faut-il faire avant de compter ?",
            "range(debut, fin, pas) peut compter à l'envers avec un pas de -1. Attention : la fin est exclue.",
            "Exemple (de 3 à 1) :\nfor i in range(3, 0, -1):\n    print(i)",
        ],
        "solution": code('''
            n = int(input())
            for nombre in range(n, 0, -1):
                print(nombre)
            print("Décollage !")
        '''),
        "explication": "range(n, 0, -1) compte de n jusqu'à 1 : la borne de fin (0) n'est jamais atteinte. "
                       "Le dernier print est en dehors de la boucle, il ne s'exécute qu'une fois.",
        "niveau": 2,
    }


@dataclass
class Modele:
    """Un modèle de mission : son identifiant, son thème, ses concepts et sa fabrique."""

    id: str
    theme: str
    concepts: tuple[str, ...]
    fabriquer: Callable[[random.Random, str], dict]


MODELES = [
    Modele("filtre-seuil", "listes", ("listes", "conditions", "boucle-for"), _modele_filtre_seuil),
    Modele("compte-lettre", "chaines", ("chaines", "boucle-for"), _modele_compte_lettre),
    Modele("somme-filtre", "boucles", ("boucle-for", "conditions"), _modele_somme_filtre),
    Modele("maximum", "boucles", ("boucle-for", "listes"), _modele_maximum),
    Modele("inverser-annuaire", "dictionnaires", ("dictionnaires", "boucle-for"), _modele_inverser_annuaire),
    Modele("frequences", "dictionnaires", ("dictionnaires", "boucle-for", "listes"), _modele_frequences),
    Modele("cesar", "chaines", ("chaines", "boucle-for", "conditions"), _modele_cesar),
    Modele("conversion-sure", "exceptions", ("exceptions", "types", "listes"), _modele_conversion_sure),
    Modele("moyenne", "fonctions", ("fonctions", "listes", "conditions"), _modele_moyenne),
    Modele("categorie", "conditions", ("conditions", "fonctions"), _modele_categorie),
    Modele("calcul-variables", "variables", ("variables", "types"), _modele_calcul_variables),
    Modele("recherche-while", "boucles", ("boucle-while", "listes"), _modele_recherche_while),
    Modele("print-return", "fonctions", ("print-return", "fonctions"), _modele_print_return),
    Modele("dict-get", "dictionnaires", ("dictionnaires", "exceptions"), _modele_dict_get),
    Modele("nettoyage", "chaines", ("chaines", "listes"), _modele_nettoyage),
    Modele("compte-rebours", "boucles", ("boucle-for", "types", "variables"), _modele_compte_rebours),
]


# ---------------------------------------------------------------------------
# Génération
# ---------------------------------------------------------------------------

def _adapter_difficulte(difficulte: str, modele: Modele, niveaux_concepts: dict) -> str:
    """Ajuste la difficulté selon le niveau déclaré par l'agent pour chaque concept."""
    rang = DIFFICULTES.index(difficulte) if difficulte in DIFFICULTES else 0
    declares = [niveaux_concepts.get(c) for c in modele.concepts if niveaux_concepts.get(c)]
    if "debutant" in declares:
        rang -= 1
    elif declares and all(n == "a_l_aise" for n in declares):
        rang += 1
    return DIFFICULTES[max(0, min(rang, 2))]


def fabriquer_mission(modele: Modele, rng: random.Random, difficulte: str, adaptee: bool = False) -> dict:
    """Construit une mission complète à partir d'un modèle."""
    mission = modele.fabriquer(rng, difficulte)
    mission.update({
        "id": f"GEN-{modele.id}-{rng.randrange(10000, 99999)}",
        "theme": modele.theme,
        "concepts": list(modele.concepts),
        "difficulte": difficulte,
        "origine": "generee",
        "modele": modele.id,
        "bareme": {"points": 100, "penalite_indice": 10, "penalite_tentative": 5,
                   "penalite_solution": 50, "bonus_qualite": 10},
    })
    mission["niveau"] = max(1, min(7, mission.get("niveau", 3)))
    mission.setdefault("elements", "éléments")
    if adaptee:
        mission["note_difficulte"] = "Difficulté adaptée au niveau que tu as indiqué pour ces concepts."
    return mission


def generer_missions(concepts: list[str], nombre: int = 3, difficulte: str = "facile",
                     niveaux_concepts: dict | None = None, graine: int | None = None,
                     mixte: bool = False) -> list[dict]:
    """Génère `nombre` missions portant sur les concepts choisis.

    - mixte=True : privilégie les modèles qui combinent au moins deux concepts choisis ;
    - les missions sont triées de la plus simple à la plus difficile.
    """
    rng = random.Random(graine)
    niveaux_concepts = niveaux_concepts or {}
    choisis = set(concepts or [])
    nombre = max(1, min(int(nombre), 10))

    def recouvrement(modele):
        return len(choisis & set(modele.concepts))

    candidats = [m for m in MODELES if recouvrement(m) >= (2 if mixte else 1)]
    if not candidats:
        candidats = [m for m in MODELES if recouvrement(m) >= 1] or list(MODELES)
    candidats.sort(key=recouvrement, reverse=True)

    missions = []
    deja = []
    for position in range(nombre):
        disponibles = [m for m in candidats if m.id not in deja[-max(1, len(candidats) - 1):]] or candidats
        poids = [recouvrement(m) + 1 for m in disponibles]
        modele = rng.choices(disponibles, weights=poids, k=1)[0]
        deja.append(modele.id)
        diff = _adapter_difficulte(difficulte, modele, niveaux_concepts)
        # Progression : le premier tiers du lot est un cran plus simple.
        if position < nombre // 3 and diff != "facile":
            diff = DIFFICULTES[DIFFICULTES.index(diff) - 1]
        missions.append(fabriquer_mission(modele, rng, diff, adaptee=diff != difficulte))
    missions.sort(key=lambda m: (m["niveau"], DIFFICULTES.index(m["difficulte"])))
    return missions


# ---------------------------------------------------------------------------
# Analyse des notes de cours
# ---------------------------------------------------------------------------

def analyser_notes(texte: str, catalogue: list[dict]) -> list[dict]:
    """Repère les concepts présents dans un texte (notes de cours, liste de thèmes…).

    `catalogue` est la liste des concepts (data/concepts.json), chacun avec ses mots-clés.
    Renvoie [{"id": ..., "nom": ..., "score": ...}] trié par score décroissant.
    """
    texte_min = (texte or "").lower()
    trouves = []
    for concept in catalogue:
        score = 0
        for mot in concept.get("mots_cles", []):
            mot_min = mot.lower()
            if re.fullmatch(r"[\wàâçéèêëîïôûùüÿœ' -]+", mot_min):
                motif = r"(?<![\w])" + re.escape(mot_min.strip()) + r"(?![\w])"
                score += len(re.findall(motif, texte_min))
            else:
                score += texte_min.count(mot_min)
        if score:
            trouves.append({"id": concept["id"], "nom": concept.get("nom", concept["id"]), "score": score})
    trouves.sort(key=lambda c: c["score"], reverse=True)
    return trouves


# ---------------------------------------------------------------------------
# Missions créées par l'agent
# ---------------------------------------------------------------------------

INDICES_PAR_CONCEPT = {
    "listes": ["Quelle liste dois-tu construire ? Par quoi commence-t-elle ?",
               "Parcours les éléments avec for ; ajoute ceux qui conviennent avec append().",
               "resultat = []\nfor x in valeurs:\n    if ...:\n        resultat.append(x)\nreturn resultat"],
    "conditions": ["Combien de cas différents faut-il distinguer ?",
                   "if / elif / else teste les conditions dans l'ordre ; la première vraie l'emporte.",
                   "if a < 10:\n    ...\nelif a < 20:\n    ...\nelse:\n    ..."],
    "dictionnaires": ["Quelles sont les clés et les valeurs de ton dictionnaire ?",
                      "for cle, valeur in dico.items(): parcourt les paires ; dico.get(cle, defaut) évite les KeyError.",
                      "compteur = {}\nfor x in elements:\n    compteur[x] = compteur.get(x, 0) + 1"],
    "chaines": ["Faut-il parcourir le texte caractère par caractère ?",
                "Les méthodes utiles : lower(), upper(), strip(), split(), replace(), join().",
                "resultat = \"\"\nfor c in texte:\n    resultat += c.upper()"],
    "boucle-for": ["Que faut-il répéter, et combien de fois ?",
                   "for element in liste: parcourt une liste ; for i in range(n): répète n fois.",
                   "total = 0\nfor n in nombres:\n    total += n"],
    "boucle-while": ["Quelle condition doit rester vraie pour continuer ?",
                     "N'oublie pas de modifier la variable de la condition dans la boucle.",
                     "i = 0\nwhile i < 5:\n    print(i)\n    i += 1"],
    "exceptions": ["Quelle instruction peut échouer ? Avec quelle erreur ?",
                   "try: contient l'instruction risquée ; except TypeErreur: le plan B.",
                   "try:\n    n = int(texte)\nexcept ValueError:\n    n = 0"],
    "fonctions": ["Que reçoit la fonction (paramètres) et que doit-elle renvoyer ?",
                  "Écris les étapes en commentaires avant de coder. Termine par return.",
                  "def aire(largeur, hauteur):\n    return largeur * hauteur"],
}
INDICES_PAR_DEFAUT = ["Relis l'énoncé : quelle est l'entrée, quelle est la sortie attendue ?",
                      "Découpe le problème en petites étapes et écris-les en commentaires.",
                      "Teste ton code sur l'exemple à la main, ligne par ligne."]


def _analyser_signature(signature: str) -> tuple[str, list[str]] | None:
    trouve = re.fullmatch(r"\s*(?:def\s+)?([A-Za-z_]\w*)\s*\((.*)\)\s*:?\s*", signature or "")
    if not trouve:
        return None
    parametres = [p.strip() for p in trouve.group(2).split(",") if p.strip()]
    if not all(re.fullmatch(r"[A-Za-z_]\w*", p) for p in parametres):
        return None
    return trouve.group(1), parametres


def _lire_valeur(texte: str):
    """Lit une valeur Python écrite à la main, SANS l'exécuter (ast.literal_eval)."""
    return ast.literal_eval(texte.strip())


def creer_mission_perso(formulaire: dict) -> dict:
    """Valide le formulaire « Créer ma mission » et fabrique la mission correspondante."""
    erreurs = []
    titre = (formulaire.get("titre") or "").strip()
    enonce = (formulaire.get("enonce") or "").strip()
    concept = formulaire.get("concept") or "fonctions"
    if not titre:
        erreurs.append("Donne un titre à ta mission.")
    if not enonce:
        erreurs.append("Écris l'énoncé : que doit faire le programme ?")

    tests = []
    signature = (formulaire.get("signature") or "").strip()
    if signature:
        analyse = _analyser_signature(signature)
        if analyse is None:
            erreurs.append("Signature invalide. Exemple attendu : supprimer_doublons(noms)")
            nom_fonction, parametres = "fonction", []
        else:
            nom_fonction, parametres = analyse
        lignes = [ligne for ligne in (formulaire.get("tests") or "").split("\n") if ligne.strip()]
        if not lignes:
            erreurs.append("Ajoute au moins un test, par exemple : [1, 2, 2] => [1, 2]")
        for numero, ligne in enumerate(lignes, start=1):
            if "=>" not in ligne:
                erreurs.append(f"Test {numero} : il manque « => » entre les arguments et le résultat.")
                continue
            gauche, droite = ligne.rsplit("=>", 1)
            try:
                args = list(_lire_valeur(f"({gauche},)")) if gauche.strip() else []
                attendu = _lire_valeur(droite)
            except (ValueError, SyntaxError):
                erreurs.append(f"Test {numero} : valeurs illisibles. Écris-les comme en Python "
                               "(textes entre guillemets, listes entre crochets).")
                continue
            if parametres and len(args) != len(parametres):
                erreurs.append(f"Test {numero} : {len(args)} argument(s) donné(s), "
                               f"mais la fonction en attend {len(parametres)}.")
                continue
            tests.append(_test_appel(nom_fonction, args, attendu, f"test {numero}", visible=numero <= 2))
        code_depart = formulaire.get("code_depart") or (
            f"def {nom_fonction}({', '.join(parametres)}):\n    # À toi de jouer !\n    pass\n")
    else:
        attendu = formulaire.get("sortie_attendue") or ""
        if not attendu.strip():
            erreurs.append("Indique soit une fonction à écrire (signature), soit la sortie attendue du programme.")
        entrees = [e for e in (formulaire.get("entrees") or "").split("\n") if e.strip()]
        tests.append({"type": "sortie", "entrees": entrees, "attendu": attendu, "visible": True,
                      "description": "sortie du programme"})
        code_depart = formulaire.get("code_depart") or "# Écris ton programme ici\n"

    indices_formulaire = [i.strip() for i in formulaire.get("indices", []) if i and i.strip()]
    indices = (indices_formulaire + INDICES_PAR_CONCEPT.get(concept, INDICES_PAR_DEFAUT))[:3]
    while len(indices) < 3:
        indices.append(INDICES_PAR_DEFAUT[len(indices)])

    mission = {
        "id": "PERSO-" + (re.sub(r"[^A-Za-z0-9]", "", str(formulaire.get("identifiant") or ""))[:12]
                          or str(random.randrange(10**6, 10**7))),
        "titre": titre,
        "theme": formulaire.get("theme") or "fonctions",
        "concepts": [concept],
        "difficulte": formulaire.get("difficulte") or "intermediaire",
        "niveau": 4 if signature else 2,
        "briefing": (formulaire.get("briefing") or "").strip()
        or f"Le commandement te confie une mission spéciale basée sur ton cours : « {titre} ».",
        "objectif": (formulaire.get("objectif") or "").strip() or "Mettre en pratique une notion du cours.",
        "enonce": enonce,
        "donnees": (formulaire.get("donnees") or "").strip(),
        "resultat_attendu": (formulaire.get("resultat_attendu") or "").strip(),
        "code_depart": code_depart,
        "tests": tests,
        "indices": indices,
        "solution": (formulaire.get("solution") or "").strip(),
        "explication": (formulaire.get("explication") or "").strip()
        or "Mission créée par toi : compare ta solution avec tes notes de cours.",
        "origine": "perso",
        "elements": "éléments",
        "bareme": {"points": 80, "penalite_indice": 10, "penalite_tentative": 5,
                   "penalite_solution": 40, "bonus_qualite": 10},
    }

    if not erreurs and mission["solution"]:
        rapport = evaluer(mission, mission["solution"])
        if not rapport["reussi"]:
            premier = next((t for t in rapport["tests"] if not t["reussi"]), None)
            detail = f" (test {premier['numero']} : {premier['message']})" if premier else ""
            erreurs.append("Ta solution de référence ne passe pas tes propres tests" + detail + ".")
    return {"ok": not erreurs, "erreurs": erreurs, "mission": mission}

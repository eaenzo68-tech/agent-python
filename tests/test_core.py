"""Tests automatiques du moteur pédagogique.

Lancer depuis le dossier du projet :   python -m pytest
(pytest s'installe avec : python -m pip install pytest)
"""

import json
import random
from pathlib import Path

import pytest

from core import api
from core.code_quality import analyser_qualite
from core.code_runner import appeler_fonction, executer_programme
from core.error_explainer import expliquer_erreur
from core.mission_generator import MODELES, analyser_notes, creer_mission_perso, fabriquer_mission, generer_missions
from core.test_engine import comparer_valeurs, decoder_valeur, evaluer

DATA = Path(__file__).resolve().parent.parent / "data"
MISSIONS = json.loads((DATA / "missions.json").read_text(encoding="utf-8"))
CONCEPTS = json.loads((DATA / "concepts.json").read_text(encoding="utf-8"))
PAR_ID = {m["id"]: m for m in MISSIONS}


# ---------------------------------------------------------------------------
# Exécution du code
# ---------------------------------------------------------------------------

class TestExecution:
    def test_print_est_capture(self):
        resultat = executer_programme('print("Agent", 7)')
        assert resultat.ok
        assert resultat.sortie == "Agent 7\n"

    def test_input_utilise_les_entrees(self):
        resultat = executer_programme('nom = input("Nom ? ")\nprint(nom.upper())', entrees=["lynx"])
        assert resultat.sortie == "LYNX\n"
        assert "Nom ? lynx" in resultat.console  # la question n'est pas comparée aux tests

    def test_input_sans_entree(self):
        resultat = executer_programme("x = input()")
        assert resultat.erreur["type"] == "EOFError"

    def test_boucle_infinie_arretee(self):
        resultat = executer_programme("i = 0\nwhile i < 10:\n    pass", delai=0.5)
        assert resultat.erreur["type"] == "BoucleInfinie"
        assert resultat.erreur["ligne"] in (2, 3)

    def test_boucle_infinie_non_attrapable_par_except_exception(self):
        code = "try:\n    while True:\n        pass\nexcept Exception:\n    print('attrapé')"
        resultat = executer_programme(code, delai=0.5)
        assert resultat.erreur["type"] == "BoucleInfinie"

    def test_import_interdit(self):
        resultat = executer_programme("import os")
        assert resultat.erreur["type"] == "ImportError"

    def test_import_autorise(self):
        assert executer_programme("import math\nprint(math.floor(2.7))").sortie == "2\n"

    def test_eval_desactive(self):
        resultat = executer_programme('eval("1 + 1")')
        assert resultat.erreur["type"] == "FonctionDesactivee"

    def test_guillemets_ipad_corriges(self):
        resultat = executer_programme("print(“bonjour”)")
        assert resultat.ok and resultat.sortie == "bonjour\n"
        assert resultat.avertissements

    def test_sortie_trop_longue_coupee(self):
        resultat = executer_programme("for i in range(100000):\n    print('x' * 50)")
        assert resultat.tronquee

    def test_appel_de_fonction(self):
        programme = executer_programme("def double(x):\n    return x * 2")
        appel = appeler_fonction(programme.espace, "double", [21])
        assert appel.ok and appel.valeur == 42


# ---------------------------------------------------------------------------
# Explication des erreurs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("code, categorie", [
    ("if x = 3:\n    pass", "egalite_affectation"),
    ("if True\n    pass", "deux_points"),
    ("print((1, 2)", "parentheses"),
    ('print("bonjour)', "guillemets"),
    ("def f():\nreturn 1", "indentation"),
    ("print(agnet)\nagent = 1", "nom_inconnu"),
    ('print("Âge : " + 17)', "conversion_type"),
    ('int("abc")', "conversion_texte"),
    ("[1, 2][5]", "index"),
    ('{"a": 1}["b"]', "cle"),
    ("1 / 0", "division_zero"),
    ("[].push(3)", "attribut"),
    ("def f():\n    pass\nf() + 1", "retour_none"),
])
def test_categories_d_erreurs(code, categorie):
    resultat = executer_programme(code)
    fiche = expliquer_erreur(resultat.erreur, code)
    assert fiche["categorie"] == categorie
    for champ in ("titre", "description", "pourquoi", "question", "rappel", "exemple", "indice"):
        assert fiche[champ], f"champ vide : {champ}"


def test_nom_inconnu_propose_le_nom_proche():
    code = "message = 'ok'\nprint(mesage)"
    fiche = expliquer_erreur(executer_programme(code).erreur, code)
    assert "message" in fiche["indice"]


# ---------------------------------------------------------------------------
# Tests de mission et indices ciblés
# ---------------------------------------------------------------------------

def test_decodage_tuple():
    assert decoder_valeur({"__tuple__": [1, [2, 3]]}) == (1, [2, 3])


def test_comparaison_bool_et_entier():
    assert comparer_valeurs(1, True) == (False, "type")


def test_liste_noire_reussie():
    mission = PAR_ID["LIS-02"]
    rapport = evaluer(mission, mission["solution"])
    assert rapport["reussi"] and rapport["nb_total"] >= 5


def test_liste_noire_avec_set_detecte_l_ordre():
    mission = PAR_ID["LIS-02"]
    code = "def supprimer_doublons(noms):\n    return sorted(set(noms))\n"
    rapport = evaluer(mission, code)
    assert not rapport["reussi"]


def test_indice_cible_nombre_d_elements():
    mission = PAR_ID["LIS-03"]
    code = ("def suspects_dans_tranche(suspects, age_min, age_max):\n    r = []\n"
            "    for nom, age in suspects:\n        if age_min < age <= age_max:\n            r.append(nom)\n"
            "    return r\n")
    diagnostic = evaluer(mission, code)["diagnostic"]
    assert diagnostic["categorie"] == "logique_valeur"
    assert "2 suspects alors que la mission en attend 3" in diagnostic["description"]
    assert "condition" in diagnostic["indice"]


def test_print_au_lieu_de_return():
    mission = PAR_ID["FON-01"]
    diagnostic = evaluer(mission, "def double_code(code):\n    print(code * 2)\n")["diagnostic"]
    assert diagnostic["categorie"] == "print_return"


def test_fonction_incomplete():
    mission = PAR_ID["LIS-02"]
    diagnostic = evaluer(mission, mission["code_depart"])["diagnostic"]
    assert diagnostic["categorie"] == "fonction_incomplete"


def test_modification_du_parametre_detectee():
    mission = PAR_ID["LIS-05"]
    code = "def top_menaces(scores, n):\n    scores.sort(reverse=True)\n    return scores[:n]\n"
    rapport = evaluer(mission, code)
    assert "modification_parametre" in rapport["categories"]


def test_boucle_infinie_dans_une_mission():
    mission = PAR_ID["COR-03"]
    rapport = evaluer(mission, mission["code_depart"], delai=0.5)
    assert rapport["categories"] == ["boucle_infinie"]


# ---------------------------------------------------------------------------
# Banque de missions
# ---------------------------------------------------------------------------

def test_au_moins_25_missions():
    assert len(MISSIONS) >= 25
    themes = {m["theme"] for m in MISSIONS}
    assert {"variables", "conditions", "boucles", "listes", "dictionnaires",
            "chaines", "fonctions", "exceptions"} <= themes
    assert any(m.get("demo") for m in MISSIONS)


@pytest.mark.parametrize("mission", MISSIONS, ids=[m["id"] for m in MISSIONS])
def test_chaque_solution_reussit(mission):
    assert evaluer(mission, mission["solution"])["reussi"]
    assert not evaluer(mission, mission["code_depart"], delai=0.5)["reussi"]
    assert len(mission["indices"]) == 3


def test_identifiants_compatibles_avec_les_adresses():
    import re
    for mission in MISSIONS:
        assert re.fullmatch(r"[A-Za-z0-9-]+", mission["id"])
    for concept in CONCEPTS:
        assert re.fullmatch(r"[a-z0-9-]+", concept["id"])


# ---------------------------------------------------------------------------
# Générateur
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("modele", MODELES, ids=[m.id for m in MODELES])
@pytest.mark.parametrize("difficulte", ["facile", "intermediaire", "difficile"])
def test_modeles_generent_des_missions_valides(modele, difficulte):
    for graine in range(3):
        mission = fabriquer_mission(modele, random.Random(graine), difficulte)
        json.dumps(mission)  # doit être envoyable en JSON
        assert evaluer(mission, mission["solution"])["reussi"]
        assert not evaluer(mission, mission["code_depart"], delai=0.5)["reussi"]


def test_generation_progressive():
    missions = generer_missions(["listes", "conditions"], 5, "intermediaire", graine=4)
    assert len(missions) == 5
    niveaux = [m["niveau"] for m in missions]
    assert niveaux == sorted(niveaux)


def test_generation_mixte():
    missions = generer_missions(["dictionnaires", "boucle-for"], 2, "facile", graine=1, mixte=True)
    for mission in missions:
        assert {"dictionnaires", "boucle-for"} <= set(mission["concepts"])


def test_analyse_des_notes():
    texte = "Aujourd'hui : les boucles for et while, puis les dictionnaires (clé, valeur)."
    trouves = [c["id"] for c in analyser_notes(texte, CONCEPTS)]
    assert "boucle-for" in trouves and "boucle-while" in trouves and "dictionnaires" in trouves


def test_creation_mission_perso():
    resultat = creer_mission_perso({
        "titre": "Maximum", "enonce": "Renvoie le plus grand.", "concept": "listes",
        "signature": "plus_grand(valeurs)", "tests": "[3, 9, 2] => 9\n[-1] => -1",
        "solution": "def plus_grand(valeurs):\n    return max(valeurs)\n", "identifiant": "test1",
    })
    assert resultat["ok"], resultat["erreurs"]
    assert len(resultat["mission"]["tests"]) == 2


def test_creation_mission_perso_refuse_le_code():
    resultat = creer_mission_perso({
        "titre": "Piège", "enonce": "x", "signature": "f(x)",
        "tests": "__import__('os').system('echo') => 1",
    })
    assert not resultat["ok"]  # ast.literal_eval refuse tout ce qui n'est pas une valeur simple


# ---------------------------------------------------------------------------
# Qualité du code
# ---------------------------------------------------------------------------

def test_qualite_code_propre():
    rapport = analyser_qualite(PAR_ID["LIS-02"]["solution"])
    assert rapport["score"] >= 85 and rapport["niveau"] == "Excellent"


def test_qualite_au_plus_trois_conseils_et_jamais_sous_40():
    code = ("def F(maListe):\n  list=[]\n  for i in range(len(maListe)):\n    list.append(maListe[i])\n"
            "  if x == True:\n    return True\n  else:\n    return False\n")
    rapport = analyser_qualite(code)
    assert len(rapport["conseils"]) <= 3
    assert rapport["score"] >= 40


# ---------------------------------------------------------------------------
# API (ce que reçoit l'interface)
# ---------------------------------------------------------------------------

def test_api_executer():
    reponse = json.loads(api.traiter("executer", json.dumps({"code": "print(1/0)"})))
    assert reponse["diagnostic"]["categorie"] == "division_zero"


def test_api_action_inconnue():
    assert "erreur_interne" in json.loads(api.traiter("inexistante", "{}"))


def test_api_evaluer():
    mission = PAR_ID["VAR-01"]
    reponse = json.loads(api.traiter("evaluer", json.dumps({"mission": mission, "code": mission["solution"]})))
    assert reponse["reussi"] and reponse["qualite"]["analysable"]

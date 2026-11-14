"""Exécution contrôlée du code écrit par l'agent (l'utilisateur).

IMPORTANT – sécurité
--------------------
Ce module LIMITE les risques, mais il n'offre PAS une sécurité totale.
Il ne faut exécuter que ton propre code.

Ce qui est mis en place :
- dans l'application, le code tourne dans Pyodide (Python compilé en
  WebAssembly) à l'intérieur d'un « Web Worker » : un fil d'exécution séparé
  du navigateur, sans accès aux fichiers de ton ordinateur ;
- une limite de temps et une limite d'étapes détectent les boucles infinies ;
- si le programme reste bloqué malgré tout (par exemple dans time.sleep),
  l'interface arrête complètement le Worker et le relance (voir
  js/moteur_python.js) ;
- seuls certains modules peuvent être importés ;
- eval(), exec(), input() réel, exit() et quelques autres fonctions sont
  remplacés ou désactivés.
"""

from __future__ import annotations

import builtins
import contextlib
import io
import sys
import time
import traceback
from collections import Counter
from dataclasses import dataclass, field

# Nom de « fichier » donné au code de l'agent. Il permet de reconnaître
# ses lignes dans les messages d'erreur.
FICHIER_MISSION = "<mission>"

# Valeurs par défaut (modifiables depuis les paramètres de l'application).
DELAI_PAR_DEFAUT = 3.0          # secondes
MAX_ETAPES_PAR_DEFAUT = 2_000_000  # lignes exécutées au maximum
TAILLE_SORTIE_MAX = 20_000      # caractères affichés au maximum

# Modules que l'agent a le droit d'importer pendant les missions.
MODULES_AUTORISES = {
    "math", "random", "string", "collections", "itertools", "functools",
    "statistics", "datetime", "time", "re", "json", "copy", "decimal",
    "fractions", "operator", "heapq", "bisect", "textwrap", "unicodedata",
    "dataclasses", "typing", "enum", "calendar", "pprint", "numpy", "pandas",
}

# Guillemets « intelligents » que le clavier de l'iPad insère tout seul.
GUILLEMETS_TYPOGRAPHIQUES = {
    "“": '"', "”": '"', "‘": "'", "’": "'",
}


class ArretExecution(BaseException):
    """Levée quand le programme dépasse la limite de temps ou d'étapes.

    Elle hérite de BaseException (et pas d'Exception) pour qu'un
    « except Exception » écrit par l'agent ne puisse pas l'attraper.
    """

    def __init__(self, ligne: int, raison: str, compteur_ligne: int):
        super().__init__(raison)
        self.ligne = ligne
        self.raison = raison
        self.compteur_ligne = compteur_ligne


class FonctionDesactivee(Exception):
    """Levée quand l'agent appelle une fonction désactivée dans les missions."""


@dataclass
class ResultatExecution:
    """Tout ce qu'on sait après avoir exécuté un morceau de code."""

    ok: bool
    sortie: str = ""          # uniquement ce qu'a affiché print()
    console: str = ""         # sortie + questions posées par input()
    erreur: dict | None = None
    tronquee: bool = False
    duree: float = 0.0
    avertissements: list[str] = field(default_factory=list)
    espace: dict = field(default_factory=dict)  # variables créées (non envoyé à l'interface)

    def vers_dict(self) -> dict:
        """Version simple (sans l'espace de noms) envoyée à l'interface."""
        return {
            "ok": self.ok,
            "sortie": self.sortie,
            "console": self.console,
            "erreur": self.erreur,
            "tronquee": self.tronquee,
            "duree": round(self.duree, 3),
            "avertissements": self.avertissements,
        }


# ---------------------------------------------------------------------------
# Préparation du code
# ---------------------------------------------------------------------------

def preparer_code(code: str) -> tuple[str, list[str]]:
    """Nettoie le code avant de l'exécuter.

    - remplace les guillemets typographiques (“ ” ‘ ’) par des guillemets droits ;
    - remplace les tabulations en début de ligne par 4 espaces.

    Renvoie le code nettoyé et la liste des avertissements à afficher.
    """
    avertissements = []
    nb_guillemets = sum(code.count(c) for c in GUILLEMETS_TYPOGRAPHIQUES)
    if nb_guillemets:
        for courbe, droit in GUILLEMETS_TYPOGRAPHIQUES.items():
            code = code.replace(courbe, droit)
        avertissements.append(
            f"{nb_guillemets} guillemet(s) typographique(s) “ ” ont été remplacés par des "
            "guillemets droits \" '. Sur iPad, désactive « Ponctuation intelligente » "
            "dans Réglages > Général > Clavier."
        )
    return code.replace("\r\n", "\n"), avertissements


# ---------------------------------------------------------------------------
# Capture de la sortie (print)
# ---------------------------------------------------------------------------

class _Ecran(io.TextIOBase):
    """Remplace la sortie standard pour récupérer ce que print() affiche."""

    def __init__(self, limite: int = TAILLE_SORTIE_MAX):
        self.limite = limite
        self._sortie: list[str] = []
        self._console: list[str] = []
        self._taille = 0
        self.tronquee = False

    def writable(self) -> bool:
        return True

    def write(self, texte: str) -> int:
        self._ajouter(texte, aussi_sortie=True)
        return len(texte)

    def ecrire_console(self, texte: str) -> None:
        """Écrit seulement dans la console (pas dans la sortie comparée aux tests)."""
        self._ajouter(texte, aussi_sortie=False)

    def _ajouter(self, texte: str, aussi_sortie: bool) -> None:
        if self.tronquee:
            return
        reste = self.limite - self._taille
        if len(texte) > reste:
            texte = texte[:reste]
            self.tronquee = True
        self._taille += len(texte)
        self._console.append(texte)
        if aussi_sortie:
            self._sortie.append(texte)

    @property
    def sortie(self) -> str:
        return "".join(self._sortie)

    @property
    def console(self) -> str:
        texte = "".join(self._console)
        if self.tronquee:
            texte += "\n[… sortie trop longue, coupée …]"
        return texte


# ---------------------------------------------------------------------------
# Garde-fou contre les boucles infinies
# ---------------------------------------------------------------------------

class _Garde:
    """Compte les lignes exécutées par le code de l'agent.

    On utilise sys.settrace : Python appelle notre fonction à chaque
    nouvelle ligne exécutée. Si le programme dure trop longtemps ou exécute
    trop de lignes, on l'arrête en levant ArretExecution.
    """

    def __init__(self, delai: float, max_etapes: int):
        self.delai = delai
        self.max_etapes = max_etapes
        self.etapes = 0
        self.lignes: Counter = Counter()
        self._debut = 0.0
        self._ancienne_trace = None

    def __enter__(self):
        self._debut = time.monotonic()
        self._ancienne_trace = sys.gettrace()
        sys.settrace(self._trace_globale)
        return self

    def __exit__(self, *details):
        sys.settrace(self._ancienne_trace)
        return False

    def _trace_globale(self, frame, evenement, argument):
        # On ne surveille que le code de la mission (pas les modules Python).
        if frame.f_code.co_filename == FICHIER_MISSION:
            return self._trace_locale
        return None

    def _trace_locale(self, frame, evenement, argument):
        if evenement == "line":
            self.etapes += 1
            self.lignes[frame.f_lineno] += 1
            trop_d_etapes = self.etapes > self.max_etapes
            # Lire l'horloge coûte cher : on le fait toutes les 1024 lignes.
            trop_long = (self.etapes & 1023) == 0 and time.monotonic() - self._debut > self.delai
            if trop_d_etapes or trop_long:
                raison = "etapes" if trop_d_etapes else "temps"
                raise ArretExecution(frame.f_lineno, raison, self.lignes[frame.f_lineno])
        return self._trace_locale


# ---------------------------------------------------------------------------
# Fonctions intégrées surveillées
# ---------------------------------------------------------------------------

def _importer_controle(nom, globales=None, locales=None, fromlist=(), level=0):
    """Remplace __import__ : refuse les modules non autorisés."""
    if level:
        raise ImportError("Les imports relatifs (from . import …) ne sont pas utilisés dans les missions.")
    racine = nom.split(".")[0]
    if racine not in MODULES_AUTORISES:
        raise ImportError(
            f"Le module « {racine} » n'est pas autorisé pendant les missions. "
            f"Modules disponibles : {', '.join(sorted(MODULES_AUTORISES))}."
        )
    return builtins.__import__(nom, globales, locales, fromlist, level)


def _fonction_desactivee(nom: str, raison: str):
    def desactivee(*args, **kwargs):
        raise FonctionDesactivee(f"{nom}() est désactivée dans les missions : {raison}")
    desactivee.__name__ = nom
    return desactivee


def _creer_input(entrees: list[str], ecran: _Ecran):
    """Fabrique une fonction input() qui lit les entrées préparées à l'avance."""
    file_entrees = list(entrees)

    def input_simule(invite: object = "") -> str:
        ecran.ecrire_console(str(invite))
        if not file_entrees:
            raise EOFError(
                "input() attend une valeur, mais aucune entrée n'a été fournie. "
                "Ajoute des valeurs dans la zone « Entrées » (une par ligne)."
            )
        valeur = str(file_entrees.pop(0))
        ecran.ecrire_console(valeur + "\n")  # on « tape » la valeur dans la console
        return valeur

    return input_simule


def creer_builtins(entrees: list[str], ecran: _Ecran) -> dict:
    """Prépare les fonctions intégrées disponibles pour le code de l'agent."""
    disponibles = dict(vars(builtins))
    disponibles["__import__"] = _importer_controle
    disponibles["input"] = _creer_input(entrees, ecran)
    disponibles["eval"] = _fonction_desactivee("eval", "elle exécute du texte comme du code, c'est risqué.")
    disponibles["exec"] = _fonction_desactivee("exec", "elle exécute du texte comme du code, c'est risqué.")
    disponibles["breakpoint"] = _fonction_desactivee("breakpoint", "il n'y a pas de débogueur ici.")
    disponibles["help"] = _fonction_desactivee("help", "consulte plutôt la Bibliothèque des concepts.")
    disponibles["exit"] = _fonction_desactivee("exit", "le programme s'arrête tout seul à la fin.")
    disponibles["quit"] = _fonction_desactivee("quit", "le programme s'arrête tout seul à la fin.")
    return disponibles


# ---------------------------------------------------------------------------
# Description des erreurs
# ---------------------------------------------------------------------------

def _ligne_du_code(code: str, numero: int | None) -> str:
    if not numero:
        return ""
    lignes = code.split("\n")
    if 1 <= numero <= len(lignes):
        return lignes[numero - 1]
    return ""


def decrire_exception(exc: BaseException, code: str) -> dict:
    """Transforme une exception en dictionnaire simple (envoyable en JSON)."""
    if isinstance(exc, ArretExecution):
        return {
            "type": "BoucleInfinie",
            "message": (
                "Le programme a été arrêté : il dépassait la limite de temps."
                if exc.raison == "temps"
                else "Le programme a été arrêté : il exécutait beaucoup trop d'instructions."
            ),
            "ligne": exc.ligne,
            "texte_ligne": _ligne_du_code(code, exc.ligne),
            "repetitions": exc.compteur_ligne,
            "pile": [],
        }

    if isinstance(exc, SyntaxError):  # comprend IndentationError et TabError
        ligne = exc.lineno if exc.filename in (FICHIER_MISSION, None) else None
        return {
            "type": type(exc).__name__,
            "message": exc.msg or str(exc),
            "ligne": ligne,
            "colonne": exc.offset,
            "texte_ligne": _ligne_du_code(code, ligne),
            "pile": [],
        }

    # Erreur pendant l'exécution : on garde uniquement les lignes de la mission.
    pile = []
    for etape in traceback.extract_tb(exc.__traceback__):
        if etape.filename == FICHIER_MISSION:
            pile.append({"ligne": etape.lineno, "fonction": etape.name})
    ligne = pile[-1]["ligne"] if pile else None
    details = {
        "type": type(exc).__name__,
        "message": str(exc),
        "ligne": ligne,
        "texte_ligne": _ligne_du_code(code, ligne),
        "pile": pile,
    }
    # Quelques informations utiles pour expliquer l'erreur.
    if isinstance(exc, NameError) and getattr(exc, "name", None):
        details["nom"] = exc.name
    if isinstance(exc, KeyError) and exc.args:
        details["cle"] = repr(exc.args[0])
    if isinstance(exc, AttributeError) and getattr(exc, "name", None):
        details["attribut"] = exc.name
    return details


def formater_erreur_console(erreur: dict) -> str:
    """Texte court affiché dans la console, comme le ferait Python."""
    morceaux = []
    if erreur.get("ligne"):
        morceaux.append(f"Erreur à la ligne {erreur['ligne']} :")
        if erreur.get("texte_ligne"):
            morceaux.append("    " + erreur["texte_ligne"].strip())
    morceaux.append(f"{erreur['type']}: {erreur['message']}")
    return "\n".join(morceaux)


# ---------------------------------------------------------------------------
# Exécution
# ---------------------------------------------------------------------------

def executer_programme(
    code: str,
    entrees: list[str] | None = None,
    delai: float = DELAI_PAR_DEFAUT,
    max_etapes: int = MAX_ETAPES_PAR_DEFAUT,
) -> ResultatExecution:
    """Exécute tout le programme de l'agent et renvoie un ResultatExecution."""
    code, avertissements = preparer_code(code)
    ecran = _Ecran()
    debut = time.monotonic()

    # 1. Compilation : détecte les erreurs de syntaxe avant d'exécuter quoi que ce soit.
    try:
        programme = compile(code, FICHIER_MISSION, "exec")
    except SyntaxError as exc:
        return ResultatExecution(
            ok=False,
            erreur=decrire_exception(exc, code),
            avertissements=avertissements,
        )

    # 2. Exécution dans un espace de noms tout neuf.
    espace = {"__name__": "__main__", "__builtins__": creer_builtins(entrees or [], ecran)}
    erreur = None
    try:
        with contextlib.redirect_stdout(ecran), contextlib.redirect_stderr(ecran):
            with _Garde(delai, max_etapes):
                exec(programme, espace)  # noqa: S102 - c'est le rôle de ce module
    except SystemExit:
        pass  # « raise SystemExit » : le programme s'arrête simplement
    except BaseException as exc:  # noqa: BLE001 - on veut tout attraper ici
        if isinstance(exc, KeyboardInterrupt):
            raise
        erreur = decrire_exception(exc, code)

    return ResultatExecution(
        ok=erreur is None,
        sortie=ecran.sortie,
        console=ecran.console,
        erreur=erreur,
        tronquee=ecran.tronquee,
        duree=time.monotonic() - debut,
        avertissements=avertissements,
        espace=espace,
    )


@dataclass
class ResultatAppel:
    """Résultat de l'appel d'une fonction écrite par l'agent."""

    ok: bool
    valeur: object = None
    sortie: str = ""
    erreur: dict | None = None


def appeler_fonction(
    espace: dict,
    nom: str,
    args: list,
    kwargs: dict | None = None,
    code: str = "",
    delai: float = DELAI_PAR_DEFAUT,
    max_etapes: int = MAX_ETAPES_PAR_DEFAUT,
) -> ResultatAppel:
    """Appelle la fonction `nom` définie par l'agent, sous surveillance."""
    fonction = espace.get(nom)
    ecran = _Ecran()
    # input() ne doit pas bloquer pendant un test
    if isinstance(espace.get("__builtins__"), dict):
        espace["__builtins__"]["input"] = _creer_input([], ecran)
    try:
        with contextlib.redirect_stdout(ecran), contextlib.redirect_stderr(ecran):
            with _Garde(delai, max_etapes):
                valeur = fonction(*args, **(kwargs or {}))
    except BaseException as exc:  # noqa: BLE001
        if isinstance(exc, KeyboardInterrupt):
            raise
        return ResultatAppel(ok=False, sortie=ecran.sortie, erreur=decrire_exception(exc, code))
    return ResultatAppel(ok=True, valeur=valeur, sortie=ecran.sortie)

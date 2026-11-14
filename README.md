# Agent Python — centre de formation

Application éducative pour apprendre Python en accomplissant des **missions d'agent secret**.
Elle fonctionne **sur Windows et sur iPad**, **hors ligne**, sans compte, sans clé API et sans
serveur distant. Tes données restent sur ton appareil.

- 37 missions de départ (variables et types, conditions, boucles, listes, dictionnaires,
  chaînes, fonctions, gestion des erreurs), niveaux 1 à 7, dont une mission de démonstration
  (« Opération Liste Noire ») ;
- un générateur de missions (16 modèles paramétrables, 3 difficultés, missions mixtes,
  analyse de tes notes de cours) et un formulaire pour créer tes propres missions ;
- un éditeur de code, une console, des tests automatiques (y compris des tests cachés) ;
- un **téléphone d'agent** qui explique tes erreurs en français, propose 3 indices progressifs
  et garde la solution sous clé ;
- une analyse de la **qualité du code** (règles simples inspirées de PEP 8, 3 conseils maximum) ;
- XP, niveaux, 6 grades, 16 badges, séries, historique des erreurs et révisions intelligentes.

---

## 1. Architecture choisie (et pourquoi)

Le cahier des charges proposait Streamlit + SQLite. **Streamlit ne peut pas tourner sur un iPad**
(iPadOS n'autorise pas de serveur Python avec ses dépendances). Pour avoir **une seule application
qui marche partout**, Python s'exécute **directement dans le navigateur** grâce à **Pyodide**
(le vrai Python 3.12, compilé en WebAssembly).

| Demandé | Choisi | Raison |
|---|---|---|
| Streamlit | Page web (HTML/CSS/JavaScript) + Python dans le navigateur (Pyodide) | Fonctionne sur Windows **et** iPad, hors ligne |
| SQLite | Stockage local du navigateur (`localStorage`) + export/import JSON | Intégré à tous les navigateurs, rien à installer ; l'export sert de sauvegarde et de transfert PC ↔ iPad |
| CodeMirror / Monaco | Petit éditeur maison (`js/editeur.js`) | Aucune bibliothèque à télécharger ; barre de symboles et correction des guillemets pour l'iPad |
| `exec()` dans un processus séparé | Code exécuté dans un **Web Worker** (fil séparé), arrêté de force après le délai | Équivalent navigateur d'un processus séparé |
| pytest | ✅ `tests/test_core.py` (131 tests) | Vérifie le moteur ET chaque mission |
| Ruff | ✅ configuré dans `pyproject.toml` pour le code du projet ; l'analyse de **ton** code est faite par `core/code_quality.py` | Ruff ne tourne pas dans un navigateur |

**Point important pour apprendre :** toute la logique pédagogique est écrite **en Python**, dans
le dossier `core/`. Les mêmes fichiers tournent dans le navigateur (via Pyodide) et sur ton
ordinateur (pour les tests). Le JavaScript ne s'occupe que de l'affichage.

```
Navigateur (Windows ou iPad)
├── Interface (HTML/CSS/JS)  ── pages, éditeur, téléphone, progression (localStorage)
│        │  messages JSON
│        ▼
└── Web Worker  ── Pyodide (Python 3.12)  ── core/*.py
                     exécute ton code, lance les tests, explique les erreurs,
                     analyse la qualité, génère des missions
```

---

## 2. Lancer l'application sur Windows

**Prérequis :** Python 3.12 (ou plus récent) et un navigateur récent (Edge, Chrome ou Firefox).
Aucune bibliothèque à installer.

1. Décompresse le dossier `agent-python` où tu veux (par exemple dans `Documents`).
2. Double-clique sur **`lancer_windows.bat`**.
3. Le navigateur s'ouvre sur `http://localhost:8000`. Garde la fenêtre noire ouverte pendant
   que tu utilises l'application ; ferme-la (ou Ctrl + C) pour arrêter.

Ou, dans un terminal ouvert dans le dossier :

```
python serveur.py
```

> Ouvrir `index.html` par un double-clic **ne fonctionne pas** : les navigateurs bloquent le
> moteur Python sur les fichiers locaux. Il faut passer par `serveur.py`.

**Premier lancement :** Python (≈ 10 Mo) est téléchargé une seule fois puis gardé en cache.
Ensuite, plus besoin d'Internet. Pour ne JAMAIS avoir besoin d'Internet, voir la section 4.

macOS / Linux : `sh lancer_mac_linux.sh` (ou `python3 serveur.py`).

---

## 3. Utiliser l'application sur iPad

Un iPad ne peut pas lancer `serveur.py`, mais il peut ouvrir l'application dans Safari.
Trois options, de la plus simple à la plus complète :

### Option A — Depuis ton PC, sur le même Wi-Fi (rien à installer)
1. Sur le PC : `lancer_windows.bat --reseau` (ou `python serveur.py --reseau`).
2. La fenêtre affiche une adresse du type `http://192.168.1.23:8000/`.
3. Sur l'iPad, ouvre cette adresse dans Safari. Si Windows demande l'autorisation du pare-feu,
   accepte pour les « réseaux privés ».

Limites : le PC doit rester allumé, et la progression est liée à l'adresse affichée (si elle
change, utilise Paramètres > Exporter / Importer).

### Option B — Héberger gratuitement sur GitHub Pages (recommandé : vraie app hors ligne)
1. Crée un compte sur github.com, puis un dépôt (par exemple `agent-python`).
2. Envoie tout le contenu du dossier dans ce dépôt (bouton « Add file > Upload files »).
   Le fichier `.nojekyll` doit être inclus (il est déjà dans le dossier).
3. Dans le dépôt : Settings > Pages > « Deploy from a branch » > branche `main`, dossier `/root`.
4. Après une minute, ouvre l'adresse `https://ton-pseudo.github.io/agent-python/` dans Safari.
5. Bouton Partager > **« Sur l'écran d'accueil »**. Lance l'app depuis l'icône **une fois avec
   Internet** : elle est ensuite disponible **hors ligne**, comme une vraie application.

Il ne s'agit que de fichiers statiques : aucune donnée ne part vers GitHub, la progression
reste dans l'iPad. (Un dépôt public est visible de tous : n'y mets rien de personnel.)

### Option C — Le même hébergement, mais avec le moteur Python inclus
Fais d'abord la section 4 sur ton PC, puis envoie aussi le dossier `vendor/` sur GitHub.
L'app ne dépend alors plus du tout d'un site externe.

### Réglage indispensable sur iPad
Réglages > Général > Clavier > désactive **« Ponctuation intelligente »**. Sinon le clavier
transforme `"` en `“ ”`, que Python refuse. (L'éditeur les corrige aussi automatiquement.)

Sans clavier physique, utilise la **barre de symboles** au-dessus de l'éditeur (⇥ pour
indenter, `:`, `()`, `[]`, `{}`, guillemets, `==`…).

---

## 4. Mode 100 % hors ligne (copie locale de Python)

Une seule fois, avec Internet :

```
python outils/telecharger_pyodide.py
```

Le moteur est copié dans `vendor/pyodide/` (≈ 12 Mo). L'application l'utilise automatiquement
à la place d'Internet (Paramètres > Moteur Python indique « copie locale »). Pratique pour une
clé USB ou pour l'option C.

---

## 5. Comment se déroule une mission

1. Lis le **dossier** : briefing, objectif pédagogique, concepts, énoncé, données, résultat attendu.
2. Ouvre « Méthode d'agent » : entrées → sortie → exemple à la main → étapes en commentaires.
3. Écris ton code. **Exécuter le code** (Ctrl/Cmd + Entrée) l'essaie ; la zone « Entrées » sert
   à répondre aux `input()`.
4. **Envoyer la mission** (Ctrl/Cmd + Maj + Entrée) lance tous les tests, y compris des tests
   cachés (liste vide, cas limites…).
5. En cas d'échec, le **téléphone** s'ouvre : catégorie, passage concerné, pourquoi, une question
   pour réfléchir, un rappel, un exemple différent, une piste. **Jamais la réponse.**
6. Onglet **Indices** : 3 niveaux (piste → explication → exemple similaire), −10 points chacun.
7. Onglet **Solution** : verrouillée ; révélable volontairement, avec un avertissement (−50 points,
   la série s'arrête). Recommandée seulement après 3 envois.
8. En cas de réussite, le **débriefing** affiche séparément « Mission accomplie » et
   « Qualité du code », au plus 3 conseils, l'explication et la solution de l'agence.

**Barème :** 100 points − 10 par indice − 5 par envoi échoué − 50 si solution révélée
+ 10 si qualité ≥ 85 (minimum 10). XP = points × 1 (facile), 1,5 (intermédiaire) ou 2 (difficile).
Rejouer une mission ne rapporte que les points gagnés **en plus** de ton meilleur score.

**Déblocage :** dans chaque thème, une mission se débloque quand la précédente est accomplie.
Les missions de révision, la démo et les missions générées sont toujours ouvertes.
Le **mode libre** (Paramètres) débloque tout, pour suivre l'ordre de ton cours.

**Révisions intelligentes :** quand une même erreur revient 3 fois (par ex. `print` au lieu de
`return`, `=` au lieu de `==`, indice hors limites, clé absente, boucle infinie…), l'application
propose automatiquement une mission courte centrée sur cette notion.

### Les 8 pages
1. **Tableau de bord** — grade, XP, mission recommandée, concepts récents, notions à revoir,
   dernières missions, progression générale.
2. **Nouvelle mission** — générer des missions à partir de tes thèmes / notes (avec ton niveau
   par concept, le nombre et la difficulté), ou créer ta propre mission avec tests.
3. **Mission en cours** — la dernière mission ouverte.
4. **Centre d'entraînement** — révisions recommandées, mission mixte, révision surprise,
   notions maîtrisées / à travailler, catalogue filtrable, recommencer une mission.
5. **Progression** — carte d'agent, grades, tableau de progression, concepts, badges, historique.
6. **Concepts** — une fiche récapitulative par notion (16 fiches, dont POO, fichiers, NumPy, pandas).
7. **Historique des erreurs** — erreurs regroupées par catégorie, journal détaillé.
8. **Paramètres** — nom, éditeur, délai d'exécution, mode libre, sauvegarde, moteur Python.

---

## 6. Sécurité — à lire

L'application exécute du code Python. **Cette exécution n'est pas totalement sécurisée.**
**N'exécute que ton propre code**, jamais un code copié depuis une source inconnue.

Ce qui limite les risques :
- le code tourne dans **Pyodide, à l'intérieur d'un Web Worker** : un fil séparé du navigateur,
  sans accès à tes fichiers ni à ton système (les fichiers que ton code crée sont virtuels) ;
- une **limite de temps et d'étapes** détecte les boucles infinies (`core/code_runner.py`) ;
- si le programme reste bloqué malgré tout, l'interface **arrête complètement le Worker** et
  en relance un neuf (`js/moteur_python.js`) ;
- seuls certains **modules** peuvent être importés (`math`, `random`, `collections`…) ;
- `eval()`, `exec()`, `exit()`, `help()` sont désactivés pendant les missions ;
- l'application elle-même n'utilise jamais `eval()` : les valeurs saisies dans
  « Créer ma mission » sont lues avec `ast.literal_eval`, qui refuse tout code ;
- `serveur.py` n'écoute que ton ordinateur (`127.0.0.1`), sauf si tu ajoutes `--reseau`.

---

## 7. Arborescence du projet

```
agent-python/
├── index.html                 Page unique de l'application
├── manifest.webmanifest       Installation sur l'écran d'accueil (iPad)
├── service-worker.js          Mode hors ligne (cache de l'app et de Python)
├── serveur.py                 Petit serveur local (bibliothèque standard uniquement)
├── lancer_windows.bat         Lancement par double-clic sous Windows
├── lancer_mac_linux.sh        Lancement sous macOS / Linux
├── requirements.txt           Vide : rien à installer pour utiliser l'app
├── requirements-dev.txt       pytest + ruff, pour les tests (facultatif)
├── pyproject.toml             Configuration de pytest et Ruff
├── .nojekyll                  Nécessaire pour GitHub Pages
│
├── core/                      LE MOTEUR PÉDAGOGIQUE (Python)
│   ├── api.py                 Point d'entrée unique appelé par l'interface
│   ├── code_runner.py         Exécution contrôlée : sortie, input(), délai, modules
│   ├── test_engine.py         Tests automatiques d'une mission
│   ├── error_explainer.py     Explication des erreurs Python en français
│   ├── hint_engine.py         Indices ciblés pour les erreurs de logique
│   ├── code_quality.py        Analyse de qualité (PEP 8 simplifié)
│   └── mission_generator.py   Modèles de missions, analyse des notes, missions perso
│
├── data/                      Données (générées par outils/construire_donnees.py)
│   ├── missions.json          37 missions
│   ├── concepts.json          16 fiches de concepts
│   └── badges.json            16 badges
│
├── js/                        L'INTERFACE (JavaScript)
│   ├── app.js                 Démarrage, navigation, barre du haut
│   ├── moteur_python.js       Pont avec le Worker (délais, redémarrage)
│   ├── editeur.js             Éditeur de code (clavier + tactile)
│   ├── coloration.js          Coloration syntaxique Python
│   ├── telephone.js           Le téléphone d'agent
│   ├── progression.js         Score, XP, grades, badges, révisions
│   ├── stockage.js            Sauvegarde locale, export / import
│   ├── donnees.js             Chargement des missions et concepts
│   ├── generation.js          Génération de missions
│   ├── composants.js          Cartes réutilisables
│   ├── interface.js           Outils d'affichage (fenêtres, notifications…)
│   └── pages/                 Une page par fichier (les 8 pages)
│
├── worker/moteur_python.js    Le Web Worker qui charge Pyodide
├── assets/                    Styles et icônes
├── outils/
│   ├── missions_source.py     Les missions, écrites en Python (facile à lire)
│   ├── concepts_source.py     Les fiches de concepts et les badges
│   ├── construire_donnees.py  Vérifie toutes les missions et génère data/*.json
│   └── telecharger_pyodide.py Copie locale du moteur Python (mode 100 % hors ligne)
├── tests/test_core.py         Tests pytest
└── vendor/                    (vide) copie locale de Pyodide après la section 4
```

**Pourquoi s'écarter de la structure proposée ?** `database/` et `pages/*.py` (Streamlit)
n'ont plus lieu d'être : l'interface est en JavaScript (`js/pages/`) et la progression est
dans le navigateur (`js/stockage.js`). La progression (`progression.py` dans la proposition)
est calculée côté interface (`js/progression.js`) car elle concerne l'affichage et la
sauvegarde ; tout ce qui touche à TON code est resté en Python dans `core/`.

---

## 8. Ajouter ou modifier des missions

1. Ouvre `outils/missions_source.py` et copie une mission existante (format Python lisible).
2. Lance :

   ```
   python outils/construire_donnees.py
   ```

   Le script vérifie que **la solution réussit tous les tests** et que **le code de départ
   ne les réussit pas**, puis met à jour `data/missions.json`.
3. Recharge la page.

Pour un nouveau modèle de génération : ajoute une fonction `_modele_xxx` dans
`core/mission_generator.py` et inscris-la dans `MODELES`.

---

## 9. Tests et qualité du projet (facultatif)

```
python -m pip install -r requirements-dev.txt
python -m pytest            # 131 tests : moteur, explications, chaque mission, chaque modèle
python -m ruff check core outils tests serveur.py
```

---

## 10. Dépannage

| Problème | Solution |
|---|---|
| Page blanche ou « Impossible de charger les données » | Lance l'app avec `serveur.py` / `lancer_windows.bat`, pas en double-cliquant `index.html` |
| « Python indisponible » au premier lancement | Il faut Internet la toute première fois, ou faire la section 4 |
| `SyntaxError: invalid character '“'` sur iPad | Désactive « Ponctuation intelligente » (section 3) |
| Le programme « ne répond plus » | Boucle infinie : le moteur redémarre seul en quelques secondes |
| Progression disparue | Le navigateur a été vidé ou l'adresse a changé : Paramètres > Importer ta dernière sauvegarde |
| Port 8000 déjà utilisé | `serveur.py` essaie automatiquement 8001, 8002… |

**Sauvegarde :** exporte régulièrement ta progression (Paramètres). Sur iPad, Safari peut effacer
les données d'un site non utilisé pendant plusieurs semaines ; l'app installée sur l'écran
d'accueil est mieux protégée.

---

## 11. Limites de cette première version

- Les missions de la banque couvrent les 8 thèmes demandés. POO, fichiers, NumPy et pandas ont
  une fiche dans la Bibliothèque, mais pas encore de modèle de génération : crée tes propres
  missions sur ces sujets avec « Créer ma mission ».
- NumPy et pandas fonctionnent dans Pyodide mais demandent un téléchargement supplémentaire :
  ils ne sont pas chargés dans cette version.
- La génération de missions est faite par des modèles paramétrables (pas d'intelligence
  artificielle), conformément à la contrainte « aucune API externe ».

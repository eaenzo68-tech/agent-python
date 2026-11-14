"""Moteur pédagogique de l'application « Agent Python ».

Ce paquet contient toute la logique liée au code Python de l'agent :

- code_runner      : exécute le code de l'utilisateur de façon contrôlée ;
- test_engine      : vérifie une mission avec des tests automatiques ;
- error_explainer  : explique les erreurs Python en français ;
- hint_engine      : produit des indices ciblés quand le résultat est faux ;
- code_quality     : analyse la qualité du code (règles simples inspirées de PEP 8) ;
- mission_generator: fabrique de nouvelles missions à partir de modèles ;
- api              : point d'entrée unique appelé par l'interface web.

Les mêmes fichiers tournent :
- dans le navigateur (Windows ou iPad) grâce à Pyodide ;
- sur ton ordinateur avec Python 3.12, pour lancer les tests avec pytest.
"""

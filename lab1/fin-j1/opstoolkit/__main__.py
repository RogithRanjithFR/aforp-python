"""Permet « python -m opstoolkit » depuis la racine du projet.

Avec l'option -m, Python exécute ce fichier comme programme principal du package.
Jour 1 : affiche la version. Au lab 2.3, ce fichier appellera cli.main().
"""
# Import relatif : le point désigne le package courant, donc la variable vient de __init__.py
from . import __version__

# Affiche le nom et la version du package, par exemple « opstoolkit 0.1.0 »
print(f"opstoolkit {__version__}")

# Point de reprise — fin du jour 1

État de référence du projet OpsToolkit à la fin du lundi. À donner le mardi matin aux équipes ou aux apprenants
qui n'ont pas terminé les labs 1.2 à 1.5, pour qu'ils commencent le jour 2 avec tout le monde.
Le livrable n°1 est noté le mardi à 16 h 15 : cette reprise ne donne aucun avantage sur la note.

## Contenu

| Fichier | Lab |
| --- | --- |
| `opstoolkit/__init__.py`, `opstoolkit/__main__.py` | 1.3 — package, `python -m opstoolkit` |
| `opstoolkit/inventory.py` | 1.2 — `count_by_role`, `down_servers`, `overloaded` |
| `inventaire_j1.py` | 1.4 et 1.5 — script CLI robuste (codes retour 0, 2, 3) |
| `data/` | `servers.json`, `servers_casse.json`, `servers_incomplet.json` |
| `requirements.txt`, `.gitignore` | 1.1 — dépendances figées, fichiers exclus de Git |
| `tests/` | Vide : les tests arrivent au jour 5 (lab 5.1) |

## Intégrer la reprise dans un dépôt d'équipe

Ne copier que les fichiers qui manquent ou ne fonctionnent pas, sur une branche, puis merge request relue :

```bash
git switch -c reprise/j1
# copier les fichiers manquants depuis la reprise
git add . && git commit -m "Intègre le point de reprise du jour 1"
git push -u origin reprise/j1
```

## Vérification

```bash
python -m opstoolkit                                   # opstoolkit 0.1.0
python inventaire_j1.py data/servers.json; echo $?     # tableau, puis 2
python inventaire_j1.py data/servers_incomplet.json    # ERROR Serveur n°2 : champ(s) manquant(s) cpu
```

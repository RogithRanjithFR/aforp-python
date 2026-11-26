# Résultats attendus (générés avec la graine 2026)

## Lab 2.2 — servers.csv (50 serveurs)

| Rôle | Nombre | CPU moyen (%) | RAM totale (Go) |
| --- | --- | --- | --- |
| web | 10 | 45.0 | 264 |
| db | 10 | 57.6 | 296 |
| cache | 10 | 58.7 | 380 |
| batch | 10 | 37.8 | 236 |
| monitoring | 10 | 51.9 | 240 |

Serveurs arrêtés : 3

## Lab 2.4 — access.log

- Requêtes valides : 5000 (3 lignes corrompues à ignorer)
- Top 5 IP : 203.0.113.66 (1130), 198.51.100.23 (766), 192.168.1.19 (124), 192.168.1.13 (118), 192.168.1.15 (116)
- Familles de statut : 2xx = 4080, 3xx = 117, 4xx = 541, 5xx = 262
- Top URL en 5xx : /recherche (142), /api/paiement (120)

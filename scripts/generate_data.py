"""Génère les jeux de données des labs (déterministes grâce à une graine fixe).

Usage : python scripts/generate_data.py   (depuis le dossier lab/)
Produit data/servers.csv, data/servers_piege.csv, data/access.log,
data/inventory.yaml, data/targets.yaml et data/RESULTATS_ATTENDUS.md.
"""
import csv
import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

random.seed(2026)
DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

# ---------- servers.csv (lab 2.2) ----------
ROLES = ["web", "db", "cache", "batch", "monitoring"]
OS = ["Debian 12", "Ubuntu 24.04", "RHEL 9", "Rocky 9"]
rows = []
for i in range(1, 51):
    role = ROLES[(i - 1) % len(ROLES)]
    rows.append({
        "name": f"{role}{i:02d}",
        "ip": f"10.0.{ROLES.index(role)}.{i}",
        "role": role,
        "os": random.choice(OS),
        "cpu": random.randint(5, 98),
        "ram_gb": random.choice([4, 8, 16, 32, 64]),
        "up": random.choice(["true"] * 9 + ["false"]),
    })
with open(DATA / "servers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# version piégée : lignes vides, valeurs non numériques, colonne manquante
with open(DATA / "servers_piege.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for i, r in enumerate(rows[:12]):
        r = dict(r)
        if i == 3:
            r["cpu"] = "N/A"
        if i == 7:
            r["ram_gb"] = ""
        w.writerow(r)
        if i == 5:
            f.write("\n")
    f.write("orphan99,10.0.9.99,web\n")

stats = {}
for r in rows:
    s = stats.setdefault(r["role"], {"count": 0, "cpu": 0, "ram": 0})
    s["count"] += 1
    s["cpu"] += r["cpu"]
    s["ram"] += r["ram_gb"]

# ---------- access.log (lab 2.4) ----------
IPS = [f"192.168.1.{n}" for n in range(10, 40)] + ["203.0.113.66", "198.51.100.23"]
WEIGHTS = [1] * 30 + [12, 8]
URLS = ["/", "/produits", "/panier", "/api/commandes", "/api/paiement", "/login",
        "/static/app.js", "/static/style.css", "/admin", "/recherche"]
UA = "Mozilla/5.0 (X11; Linux x86_64)"
start = datetime(2026, 11, 16, 0, 0, 0)
lines, parsed = [], []
for i in range(5000):
    ip = random.choices(IPS, WEIGHTS)[0]
    url = random.choice(URLS)
    method = "POST" if url in ("/api/commandes", "/api/paiement", "/login") and random.random() < 0.6 else "GET"
    r = random.random()
    if url == "/api/paiement" and r < 0.25:
        status = 503
    elif url == "/recherche" and r < 0.30:
        status = 500
    elif url == "/admin":
        status = random.choice([401, 403, 403, 200])
    elif r < 0.05:
        status = 404
    elif r < 0.08:
        status = 302
    else:
        status = 200
    size = random.randint(200, 25000) if status == 200 else random.randint(0, 600)
    ts = (start + timedelta(seconds=i * 17)).strftime("%d/%b/%Y:%H:%M:%S +0100")
    lines.append(f'{ip} - - [{ts}] "{method} {url} HTTP/1.1" {status} {size} "-" "{UA}"')
    parsed.append((ip, url, status))
# lignes corrompues volontaires
for pos, bad in [(120, "### rotation du fichier ###"), (2500, ""), (4100, '10.0.0.1 - - [corrompu')]:
    lines.insert(pos, bad)
(DATA / "access.log").write_text("\n".join(lines) + "\n", encoding="utf-8")

ip_top = Counter(p[0] for p in parsed).most_common(5)
fam = Counter(f"{p[2] // 100}xx" for p in parsed)
err5 = Counter(p[1] for p in parsed if p[2] >= 500).most_common(5)

# ---------- inventory.yaml (labs 2.3, 3.3, 3.5) ----------
(DATA / "inventory.yaml").write_text("""\
# Inventaire CloudNova — utilisé par opstoolkit inventory / health / ssh
environments:
  dev:
    servers:
      - {name: web-dev, host: 127.0.0.1, role: web, ports: [8081]}
      - {name: cache-dev, host: 127.0.0.1, role: cache, ports: [6379]}
  recette:
    servers:
      - {name: api-recette, host: 127.0.0.1, role: api, ports: [8000]}
      - {name: s3-recette, host: 127.0.0.1, role: storage, ports: [9000]}
  prod:
    servers:
      - {name: web-prod, host: 127.0.0.1, role: web, ports: [8081]}
      - {name: db-prod, host: 127.0.0.1, role: db, ports: [5432]}
      - {name: app01, host: 127.0.0.1, role: app, ports: [2221], ssh_port: 2221}
      - {name: app02, host: 127.0.0.1, role: app, ports: [2222], ssh_port: 2222}
""", encoding="utf-8")

# ---------- targets.yaml (épreuve de sortie) ----------
(DATA / "targets.yaml").write_text("""\
# Cibles de l'épreuve de sortie (watchdog.py). Avant l'épreuve : docker stop lab-db
targets:
  - {name: site-web, host: 127.0.0.1, port: 8081, health_url: "http://127.0.0.1:8081/"}
  - {name: api-statut, host: 127.0.0.1, port: 8000, health_url: "http://127.0.0.1:8000/health"}
  - {name: api-flaky, host: 127.0.0.1, port: 8000, health_url: "http://127.0.0.1:8000/flaky"}
  - {name: cache, host: 127.0.0.1, port: 6379}
  - {name: base-clients, host: 127.0.0.1, port: 5432}
""", encoding="utf-8")

# ---------- résultats attendus pour le formateur ----------
out = ["# Résultats attendus (générés avec la graine 2026)", "",
       "## Lab 2.2 — servers.csv (50 serveurs)", "",
       "| Rôle | Nombre | CPU moyen (%) | RAM totale (Go) |", "| --- | --- | --- | --- |"]
for role in ROLES:
    s = stats[role]
    out.append(f"| {role} | {s['count']} | {s['cpu'] / s['count']:.1f} | {s['ram']} |")
out += ["", f"Serveurs arrêtés : {sum(r['up'] == 'false' for r in rows)}", "",
        "## Lab 2.4 — access.log", "",
        f"- Requêtes valides : {len(parsed)} (3 lignes corrompues à ignorer)",
        "- Top 5 IP : " + ", ".join(f"{ip} ({n})" for ip, n in ip_top),
        "- Familles de statut : " + ", ".join(f"{k} = {fam[k]}" for k in sorted(fam)),
        "- Top URL en 5xx : " + ", ".join(f"{u} ({n})" for u, n in err5), ""]
(DATA / "RESULTATS_ATTENDUS.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))

# ---------- app-logs/ (lab 2.1) ----------
APP = DATA / "app-logs"
APP.mkdir(exist_ok=True)
LEVELS = ["INFO"] * 14 + ["WARNING"] * 4 + ["ERROR"] * 2
for name, n in [("api-commandes.log", 400), ("paiements.log", 250), ("batch-nuit.log", 120)]:
    with open(APP / name, "w", encoding="utf-8") as f:
        for i in range(n):
            lvl = random.choice(LEVELS)
            f.write(f"2026-11-16 0{i % 10}:{i % 60:02d}:00 {lvl} {name.split('.')[0]} message {i}\n")
(APP / "notes.txt").write_text("pas un log\n", encoding="utf-8")
(APP / "archives").mkdir(exist_ok=True)
(APP / "archives" / "api-commandes.2026-11-15.log").write_text(
    "2026-11-15 23:59:00 ERROR api-commandes timeout base\n" * 3, encoding="utf-8")
print("app-logs générés")

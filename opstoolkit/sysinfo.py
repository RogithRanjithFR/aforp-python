"""Pilotage du système : subprocess, shutil, pathlib (labs 3.1 et 3.2)."""
import logging
import platform
import shutil
import socket
import subprocess
import time
from pathlib import Path

log = logging.getLogger(__name__)


# cmd est une liste de textes ; la fonction renvoie un couple (code retour, sortie standard)
def run(cmd: list[str], timeout: float = 10) -> tuple[int, str]:
    """Exécute une commande système SANS shell ; renvoie son code retour et sa sortie standard (lab 3.1).

    La fonction ne lève jamais d'exception quand la commande échoue : elle renvoie un code, comme le
    ferait le shell. Un code non nul est journalisé, avec le message d'erreur de la commande.

    Paramètres :
        cmd : la commande sous forme de liste, un élément par argument, par exemple ["uptime", "-p"].
        timeout : durée maximale en secondes ; au-delà, la commande est arrêtée.

    Renvoie :
        (code retour, sortie standard en texte). Programme introuvable : (127, "").
        Délai dépassé : (124, "").

    Exemples :
        >>> run([sys.executable, "-c", "print('bonjour')"])
        (0, 'bonjour\\n')
        >>> run(["commande-inexistante-aforp"])
        (127, '')
        >>> run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=1)
        (124, '')
    """
    # Bloc surveillé : les deux échecs prévus deviennent un code retour, pas une trace Python
    try:
        # TODO 1 : lancer cmd sans shell ; récupérer stdout et stderr sous forme de texte ; arrêter la
        #          commande au-delà de timeout ; ne PAS lever d'exception si le code retour n'est pas 0.
        # Aide : diapositive 38, colonne « À faire », et doc-3.pdf, partie 1 : quatre paramètres nommés.
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check = False)  # <- TODO 1
    # Le programme n'existe pas sur ce poste (macOS sans « uptime -p », image minimale…)
    except FileNotFoundError:
        # TODO 2 : renvoyer le code que le shell donne à « command not found », et une sortie vide.
        # Aide : doc-3.pdf, partie 1, tableau « Une commande peut échouer de trois façons ».
        return 127, "Command Not Found"  # <- TODO 2
    # Le programme n'a pas répondu à temps : subprocess l'a déjà arrêté
    except subprocess.TimeoutExpired:
        # TODO 3 : renvoyer le code de la commande Linux « timeout » quand le délai est dépassé, et "".
        # Aide : même tableau qu'au TODO 2, ou essayez « timeout 1 sleep 5; echo $? » dans un terminal.
        return 124, "Timeout 1 sleep 5; echo $?"  # <- TODO 3
    # La commande a tourné mais signale un échec : on le journalise, avec son message d'erreur
    if result.returncode != 0:
        # cmd[0] est le nom du programme ; strip() retire le saut de ligne final de stderr
        log.warning("%s a échoué (code %d) : %s", cmd[0], result.returncode, result.stderr.strip())
    # Code retour et sortie standard, que la commande ait réussi ou non
    return result.returncode, result.stdout


# path est un point de montage ; alert_pct le seuil d'alerte en pourcentage
def disk_usage(path: str = "/", alert_pct: int = 80) -> dict:
    """Mesure l'occupation d'un disque, sans lancer df (lab 3.1).

    Paramètres :
        path : point de montage à mesurer, « / » par défaut.
        alert_pct : seuil d'alerte en pourcentage ; l'alerte est levée dès que l'occupation l'atteint.

    Renvoie :
        {"path": path, "total_gb": taille en Go (10**9 octets) arrondie à 0,1,
        "used_pct": pourcentage utilisé arrondi à 0,1, "alert": True si used_pct >= alert_pct}.

    Exemples :
        >>> d = disk_usage("/", alert_pct=0)
        >>> sorted(d)
        ['alert', 'path', 'total_gb', 'used_pct']
        >>> d["total_gb"] > 0 and 0 < d["used_pct"] < 100 and d["alert"]
        True
        >>> disk_usage("/", alert_pct=101)["alert"]
        False
    """
    # TODO 4 : taille totale et espace utilisé du disque path, en octets, SANS lancer de commande.
    # Aide : doc-3.pdf, partie 2, tableau « Information / Python », ligne « Espace disque ».
    total, used, _ = shutil.disk_usage(path)  # <- TODO 4
    # TODO 5 : pourcentage d'espace utilisé, arrondi à 1 décimale.
    # Aide : une règle de trois avec les deux valeurs du TODO 4, puis un arrondi.
    pct = round (used/total * 100, 1)  # <- TODO 5
    # Dictionnaire sérialisable en JSON
    return {
        # Point de montage mesuré
        "path": path,
        # Taille totale en Go : 1 Go = 10**9 octets, comme df -H
        "total_gb": round(total / 1e9, 1),
        # Pourcentage calculé au TODO 5
        "used_pct": pct,
        # TODO 6 : True si le pourcentage atteint ou dépasse le seuil, False sinon.
        # Aide : pas besoin de if : une comparaison vaut déjà True ou False.
        "alert": pct >= alert_pct,  # <- TODO 6
    }


# n est le nombre de processus voulus ; la fonction renvoie une liste de dictionnaires
def top_memory(n: int = 5) -> list[dict]:
    """Liste les n processus qui occupent le plus de mémoire, avec ps (lab 3.1, Linux uniquement).

    Paramètres :
        n : nombre de processus à garder.

    Renvoie :
        Une liste de dictionnaires {"pid": int, "command": str, "mem_pct": float}, du plus gourmand
        au moins gourmand. Liste vide si ps échoue ou n'existe pas (macOS, Windows).

    Résultat attendu (valeurs propres à chaque poste) :
        [{"pid": 2412, "command": "code", "mem_pct": 6.1}, ...]
    """
    # TODO 7 : lancer ps avec run() pour obtenir, pour TOUS les processus, trois colonnes dans cet
    #          ordre : pid, %mem, comm ; les processus étant triés par mémoire décroissante.
    # Aide : man ps (options -e, -o et --sort) ; dans la liste, un élément par argument, sans espace.
    code, out = run(["ps", "-eo", "pid,%mem,comm", "--sort=-%mem"])  # <- TODO 7
    # ps a échoué ou n'existe pas : pas de classement, mais pas de plantage non plus
    if code != 0:
        # Liste vide : collect() l'écrira telle quelle dans le JSON
        return []
    # Liste des processus retenus
    procs = []
    # TODO 8 : parcourir les n premières lignes de résultats, SANS la ligne d'en-tête de ps.
    # Aide : la sortie est un seul texte : découpez-la en lignes, puis ne gardez que la tranche utile.
    for line in out.splitlines()[1:n + 1]:  # <- TODO 8
        # Découpage en 3 morceaux au plus : comm vient en dernier, car un nom peut contenir des espaces
        pid, mem, comm = line.split(None, 2)
        # TODO 9 : ajouter ce processus, avec des NOMBRES pour pid et mem_pct (le JSON attend des nombres).
        # Aide : split() ne renvoie que des textes ; quel type pour un numéro, quel type pour un pourcentage ?
        procs.append({"pid": int(pid), "command": comm, "mem_pct": float(mem)})  # <- TODO 9
    # Du plus gourmand au moins gourmand, grâce au tri fait par ps
    return procs


# alert_pct est transmis à disk_usage ; la fonction renvoie un dictionnaire prêt pour json.dumps
def collect(alert_pct: int = 80) -> dict:
    """Rassemble l'état du poste dans un dictionnaire sérialisable en JSON (lab 3.1).

    Paramètres :
        alert_pct : seuil d'alerte disque en pourcentage, transmis à disk_usage().

    Renvoie :
        {"hostname", "system", "python", "uptime", "disk", "top_memory"}. uptime vaut None si la
        commande « uptime -p » échoue ou n'existe pas.

    Exemples :
        >>> info = collect()
        >>> sorted(info)
        ['disk', 'hostname', 'python', 'system', 'top_memory', 'uptime']
        >>> info["hostname"] == platform.node()
        True
    """
    # TODO 10 : temps de fonctionnement du poste, donné par la commande « uptime -p » lancée avec run().
    # Aide : run() renvoie déjà un couple (code, sortie) : un seul appel suffit.
    code, uptime = run(["uptime", "-p"])  # <- TODO 10
    # Dictionnaire de l'état du poste ; json.dumps le convertira tel quel
    return {
        # TODO 11 : nom d'hôte du poste, sans lancer la commande hostname.
        # Aide : doc-3.pdf, partie 2 ; c'est le module qui sert aussi aux connexions TCP du lab 3.3.
        "hostname": socket.gethostname(),  # <- TODO 11
        # Système et version du noyau, par exemple « Linux 6.8.0-49-generic »
        "system": f"{platform.system()} {platform.release()}",
        # Version de Python qui exécute ce script
        "python": platform.python_version(),
        # Sortie d'uptime sans le saut de ligne final ; None si la commande a échoué
        "uptime": uptime.strip() if code == 0 else None,
        # Occupation du disque racine, avec le seuil d'alerte demandé
        "disk": disk_usage("/", alert_pct),
        # Les 5 processus les plus gourmands en mémoire
        "top_memory": top_memory(),
    }


# dry_run vaut True par défaut : rien n'est supprimé sans une demande explicite
def clean_old_files(folder: str | Path, pattern: str = "*.log", days: int = 7,
                    dry_run: bool = True) -> list[Path]:
    """Liste, et en mode réel supprime, les fichiers plus vieux que `days` jours (lab 3.2).

    Seuls les fichiers du dossier lui-même sont concernés, pas ceux des sous-dossiers. Chaque fichier
    est journalisé : « [dry-run] supprimerait … » en simulation, « supprimé … » en mode réel.

    Paramètres :
        folder : dossier à nettoyer.
        pattern : motif des fichiers concernés, « *.log » par défaut.
        days : âge minimal en jours, d'après la date de dernière modification.
        dry_run : True (défaut) pour simuler, False pour supprimer réellement.

    Renvoie :
        La liste triée des fichiers concernés, supprimés ou non.

    Exemples (dossier temporaire : a.log et b.log ont 10 jours, c.log vient d'être créé) :
        >>> import os, tempfile
        >>> d = Path(tempfile.mkdtemp())
        >>> for name, age in [("a.log", 10), ("b.log", 10), ("c.log", 0), ("d.txt", 10)]:
        ...     p = d / name
        ...     p.touch()
        ...     t = time.time() - age * 86400
        ...     os.utime(p, (t, t))
        >>> [p.name for p in clean_old_files(d, days=7)]
        ['a.log', 'b.log']
        >>> sorted(p.name for p in d.iterdir())
        ['a.log', 'b.log', 'c.log', 'd.txt']
        >>> [p.name for p in clean_old_files(d, days=7, dry_run=False)]
        ['a.log', 'b.log']
        >>> sorted(p.name for p in d.iterdir())
        ['c.log', 'd.txt']
    """
    # TODO 13 : horodatage limite : maintenant, moins `days` jours exprimés en secondes.
    # Aide : le module time donne l'heure actuelle en secondes depuis 1970 ; combien de secondes par jour ?
    limit = time.time() - days * 86400  # <- TODO 13
    # TODO 14 : fichiers de folder qui correspondent à pattern, qui sont bien des fichiers, et dont la
    #           date de dernière modification est antérieure à limit ; le tout trié.
    # Aide : doc-3.pdf, partie 3, tableau « Brique Python » : trois de ses briques, plus sorted.
    old: list[Path] = sorted(p for p in Path(folder).glob(pattern) if p.is_file() and p.stat().st_mtime < limit)  # <- TODO 14
    # Traitement de chaque vieux fichier
    for p in old:
        # Simulation : on annonce, on ne touche à rien
        if dry_run:
            # %s est remplacé par le chemin ; logging ne construit le message que s'il l'affiche
            log.info("[dry-run] supprimerait %s", p)
        # Mode réel, demandé explicitement par --force
        else:
            # TODO 15 : supprimer le fichier p, sans erreur s'il a déjà disparu.
            # Aide : une méthode de Path ; regardez son paramètre facultatif dans la documentation.
            p.unlink(missing_ok = True)  # <- TODO 15
            # Trace de chaque suppression
            log.info("supprimé %s", p)
    # Liste des fichiers concernés
    return old

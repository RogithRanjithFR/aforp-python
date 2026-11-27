"""Supervision réseau : sockets, HTTP et parallélisme (labs 3.3 et 3.4)."""
import socket
import time
from concurrent.futures import ThreadPoolExecutor

import requests


# Le résultat est un couple : (le port répond ?, temps de connexion en ms, ou None)
def port_check(host: str, port: int, timeout: float = 2.0) -> tuple[bool, int | None]:
    """Teste une connexion TCP vers host:port et mesure son temps d'établissement (lab 3.3).

    Paramètres :
        host : nom ou adresse IP, par exemple « 127.0.0.1 ».
        port : port TCP, par exemple 5432.
        timeout : délai maximal de connexion, en secondes.

    Renvoie :
        (True, durée en millisecondes arrondie à l'entier) si le port accepte la connexion ;
        (False, None) sinon : refus, délai dépassé ou nom inconnu.

    Exemples (un serveur TCP temporaire, ouvert puis fermé) :
        >>> srv = socket.create_server(("127.0.0.1", 0))
        >>> port = srv.getsockname()[1]
        >>> ok, ms = port_check("127.0.0.1", port)
        >>> ok, isinstance(ms, int)
        (True, True)
        >>> srv.close()
        >>> port_check("127.0.0.1", port, timeout=0.5)
        (False, None)
    """
    # Top départ du chronomètre ; perf_counter ne recule jamais, contrairement à l'horloge du système
    start = time.perf_counter()
    # Bloc surveillé : refus, délai dépassé et nom inconnu lèvent tous une OSError
    try:
        # TODO 17 : ouvrir une connexion TCP vers (host, port) avec le timeout, la refermer aussitôt,
        #           et renvoyer True avec la durée écoulée depuis start, en millisecondes arrondies.
        # Aide : doc-3.pdf, partie 4 (fonction try_connect) ; un bloc with referme la connexion tout seul.
        with socket.create_connection((host, port), timeout=timeout):
            return True, round((time.perf_counter() - start) * 1000) # <- TODO 17
    # Toutes les erreurs réseau dérivent d'OSError : une seule clause except suffit
    except OSError:
        # Le port ne répond pas : pas de durée
        return False, None


# Le résultat est un couple : (le service répond 200 ?, code HTTP, ou None)
def http_check(url: str, timeout: float = 2.0) -> tuple[bool, int | None]:
    """Teste un service au niveau applicatif : la requête GET aboutit-elle avec le code 200 ? (lab 3.3)

    Paramètres :
        url : adresse complète, par exemple « http://127.0.0.1:8000/health ».
        timeout : délai maximal en secondes ; sans lui, requests peut attendre indéfiniment.

    Renvoie :
        (True, 200) si le service répond 200 ; (False, code HTTP) pour un autre code ;
        (False, None) si la connexion échoue ou dépasse le délai.

    Résultats attendus avec le labo :
        /health donne (True, 200) ; /flaky donne (False, 500) ; /slow avec timeout=2 donne (False, None).
    """
    # Bloc surveillé : toute erreur de requests devient un résultat KO
    try:
        # TODO 18 : envoyer une requête GET vers url, avec le timeout.
        # Aide : doc-3.pdf, partie 5, « Rappels sur requests ».
        response = requests.get(url, timeout=timeout)  # <- TODO 18
    # Connexion impossible, délai dépassé… : toutes ces exceptions dérivent de RequestException
    except requests.RequestException:
        # Pas de réponse, donc pas de code HTTP
        return False, None
    # TODO 19 : renvoyer (service OK ?, code HTTP) ; le service n'est OK qu'avec le code 200.
    # Aide : le code HTTP est un attribut de la réponse ; une comparaison donne le booléen.
    return response.status_code == 200, response.status_code  # <- TODO 19


# job est un triplet (nom du serveur, hôte, port) ; la fonction renvoie le résultat de ce test
def check_job(job: tuple[str, str, int], timeout: float = 2.0) -> dict:
    """Teste un port d'un serveur et met le résultat en forme (lab 3.3).

    Paramètres :
        job : (nom du serveur, hôte, port), par exemple ("db-prod", "127.0.0.1", 5432).
        timeout : délai maximal de connexion, en secondes.

    Renvoie :
        {"name": nom, "host": hôte, "port": port, "ok": True ou False, "ms": durée en ms ou None}.
    """
    # Déballage du triplet en trois variables
    name, host, port = job
    # TODO 20 : tester ce port avec la fonction du TODO 17, en lui transmettant le timeout.
    # Aide : cette fonction renvoie déjà le couple attendu ici.
    ok, ms = port_check(host, port, timeout)  # <- TODO 20
    # Résultat complet, prêt à être affiché par cmd_health
    return {"name": name, "host": host, "port": port, "ok": ok, "ms": ms}


# workers est le nombre de threads : 1 pour tester en séquence
def check_targets(servers: list[dict], workers: int = 10, timeout: float = 2.0) -> list[dict]:
    """Teste tous les ports de tous les serveurs (lab 3.3), en parallèle (lab 3.4).

    Paramètres :
        servers : serveurs de l'inventaire, chacun avec « name », « host » et la liste « ports ».
        workers : nombre de threads ; 1 pour tester en séquence.
        timeout : délai maximal de chaque connexion, en secondes.

    Renvoie :
        Un résultat check_job() par port, dans l'ordre des serveurs, puis de leurs ports.

    Exemple (un serveur TCP temporaire, déclaré avec deux fois le même port) :
        >>> srv = socket.create_server(("127.0.0.1", 0))
        >>> port = srv.getsockname()[1]
        >>> servers = [{"name": "local", "host": "127.0.0.1", "ports": [port, port]}]
        >>> [(r["name"], r["port"] == port, r["ok"]) for r in check_targets(servers)]
        [('local', True, True), ('local', True, True)]
        >>> srv.close()
    """
    # TODO 21 : un triplet (nom, hôte, port) pour CHAQUE port de CHAQUE serveur, dans cet ordre.
    # Aide : une compréhension de liste peut contenir deux « for » ; le premier parcourt les serveurs.
    jobs = [(s["name"], s["host"], p) for s in servers for p in s["ports"]]  # <- TODO 21
    # Un seul thread demandé : test en séquence, un port après l'autre (version du lab 3.3)
    if workers <= 1:
        # Les attentes s'additionnent : N ports muets coûtent N fois le timeout
        return [check_job(job, timeout) for job in jobs]
    # Groupe de threads ; la sortie du bloc with attend la fin de toutes les tâches
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # TODO 23 (lab 3.4) : lancer check_job sur tous les jobs EN PARALLÈLE avec pool, en gardant l'ordre
        #           de jobs. La valeur provisoire donne le bon résultat, mais en séquence.
        # Aide : diapositive 43 et doc-3.pdf, partie 6 ; attention, check_job attend aussi le timeout.
        return list(pool.map(lambda job: check_job(job, timeout), jobs))  # <- TODO 23

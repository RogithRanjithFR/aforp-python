import argparse
import json
import logging
import socket
import sys
import time

import requests
import yaml

log = logging.getLogger("watchdog")


def load_targets(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise ValueError(e) from e

    if not isinstance(data, dict) or not isinstance(data.get("targets"), list):
        raise ValueError("clé 'targets' absente ou invalide")

    for i, t in enumerate(data["targets"]):
        if not isinstance(t, dict):
            raise ValueError(f"cible n°{i} invalide")
        for key in ("name", "host", "port"):
            if key not in t:
                raise ValueError(f"cible n°{i} : champ '{key}' manquant")
    return data["targets"]



def check_port(host, port, timeout=2.0):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except OSError:
        return False, None
    return True, int((time.perf_counter() - start) * 1000)


def check_http(url, timeout=2.0):
    """True seulement pour un statut 200."""
    try:
        return requests.get(url, timeout=timeout).status_code == 200
    except requests.RequestException:
        return False


def check_target(target):
    up, ms = check_port(target["host"], target["port"])
    ok = up
    if up and target.get("health_url"):
        ok = check_http(target["health_url"])
    return {"name": target["name"], "ok": ok, "ms": ms}




def main(argv=None):
    parser = argparse.ArgumentParser(description="Vérifie des services.")
    parser.add_argument("targets_file", metavar="FICHIER_CIBLES")
    parser.add_argument("-o", "--output", default="watchdog-report.json")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    try:
        targets = load_targets(args.targets_file)
    except ValueError as e:
        log.error("Fichier de cibles invalide : %s", e)
        return 2

    report = []
    for target in targets:
        entry = check_target(target)
        log.debug("Résultat détaillé : %s", entry)
        log.info("%s : %s", entry["name"], "OK" if entry["ok"] else "KO")
        report.append(entry)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return 0 if all(e["ok"] for e in report) else 1


if __name__ == "__main__":
    sys.exit(main())


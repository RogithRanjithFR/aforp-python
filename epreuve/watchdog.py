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


#Exigence 3


def check_port(host, port, timeout=2.0):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except OSError:
        return False, None
    return True, int((time.perf_counter() - start) * 1000)


#Exigence 4

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





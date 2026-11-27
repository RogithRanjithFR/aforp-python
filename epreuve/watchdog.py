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

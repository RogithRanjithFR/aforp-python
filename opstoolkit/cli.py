"""Point d'entrée en ligne de commande d'OpsToolkit (lab 1.4, enrichi chaque jour).

Codes retour : 0 = tout va bien, 1 = au moins une cible KO, 2 = erreur d'usage ou de configuration.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

from . import __version__
from .inventory import InventoryError

log = logging.getLogger("opstoolkit")


def cmd_inventory(args) -> int:
    from .inventory import load_inventory, servers_of
    servers = servers_of(load_inventory(args.inventory), args.env)
    print(f"{'ENV':<9}{'NOM':<13}{'RÔLE':<9}{'HÔTE':<12}PORTS")
    for s in servers:
        print(f"{s['env']:<9}{s['name']:<13}{s['role']:<9}{s['host']:<12}{','.join(map(str, s['ports']))}")
    return 0


def cmd_logs(args) -> int:
    from .logs import analyze
    report = analyze(args.file, args.top)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("Rapport écrit dans %s", args.output)
    return 0


def cmd_report(args) -> int:
    from .health import check_targets
    from .inventory import load_inventory, servers_of
    from .report import render
    servers = servers_of(load_inventory(args.inventory), args.env)
    health = check_targets(servers) if args.with_health else None
    content = render(servers, health, args.format)
    Path(args.output).write_text(content, encoding="utf-8")
    print(f"Rapport écrit dans {args.output}")
    return 0


def cmd_sysinfo(args) -> int:
    from .sysinfo import clean_old_files, collect
    if args.clean:
        files = clean_old_files(args.clean, days=args.days, dry_run=not args.force)
        print(f"{len(files)} fichier(s) {'supprimé(s)' if args.force else 'à supprimer (dry-run)'}")
        return 0
    info = collect(args.alert)
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 1 if info["disk"]["alert"] else 0


def cmd_health(args) -> int:
    from .health import check_targets
    from .inventory import load_inventory, servers_of
    results = check_targets(servers_of(load_inventory(args.inventory), args.env), timeout=args.timeout)
    for r in results:
        state = "OK" if r["ok"] else "KO"
        ms = f"{r['ms']} ms" if r["ms"] is not None else "-"
        print(f"[{state}] {r['name']:<13}{r['host']}:{r['port']:<6} {ms}")
    return 1 if any(not r["ok"] for r in results) else 0


def cmd_ssh(args) -> int:
    from .inventory import load_inventory, servers_of
    from .sshrun import run_on_servers
    results = run_on_servers(servers_of(load_inventory(args.inventory), args.env), args.command)
    for r in results:
        print(f"--- {r['name']} ({r['host']}) code={r['code']}\n{r['stdout'] or r['stderr']}")
    return 0 if results and all(r["ok"] for r in results) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opstoolkit", description="Boîte à outils d'exploitation CloudNova")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="logs détaillés (DEBUG)")
    parser.add_argument("-i", "--inventory", default="data/inventory.yaml", help="fichier d'inventaire YAML")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("inventory", help="afficher l'inventaire")
    p.add_argument("--env")
    p.set_defaults(func=cmd_inventory)

    p = sub.add_parser("logs", help="analyser un log Nginx")
    p.add_argument("file")
    p.add_argument("--top", type=int, default=5)
    p.add_argument("-o", "--output", help="écrire le rapport JSON dans ce fichier")
    p.set_defaults(func=cmd_logs)

    p = sub.add_parser("report", help="générer un rapport Markdown ou HTML")
    p.add_argument("--env")
    p.add_argument("--format", choices=["md", "html"], default="md")
    p.add_argument("-o", "--output", default="rapport.md")
    p.add_argument("--with-health", action="store_true")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("sysinfo", help="état du poste ou nettoyage de logs")
    p.add_argument("--alert", type=int, default=80, help="seuil d'alerte disque en %%")
    p.add_argument("--clean", metavar="DOSSIER", help="nettoyer les .log anciens de ce dossier")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--force", action="store_true", help="supprimer réellement (sinon dry-run)")
    p.set_defaults(func=cmd_sysinfo)

    p = sub.add_parser("health", help="tester les ports de l'inventaire")
    p.add_argument("--env")
    p.add_argument("--timeout", type=float, default=2.0)
    p.set_defaults(func=cmd_health)

    p = sub.add_parser("ssh", help="exécuter une commande sur les serveurs SSH")
    p.add_argument("command")
    p.add_argument("--env", default="prod")
    p.set_defaults(func=cmd_ssh)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s")
    try:
        return args.func(args)
    except (InventoryError, FileNotFoundError) as exc:  # erreurs prévues : message clair et code 2
        log.error("%s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())

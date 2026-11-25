#!/usr/bin/env bash
# Vérifie que le labo AFORP Python est opérationnel. Usage : ./scripts/check_lab.sh
set -u
ok=0; ko=0
check() { # nom commande
  if eval "$2" >/dev/null 2>&1; then echo "  [OK] $1"; ok=$((ok+1)); else echo "  [KO] $1"; ko=$((ko+1)); fi
}
echo "== Outils du poste =="
check "Python 3.11 ou plus" "python3 -c 'import sys; sys.exit(sys.version_info < (3,11))'"
check "Git" "git --version"
check "Docker" "docker info"
echo "== Conteneurs du labo =="
for c in lab-web lab-redis lab-db lab-status-api lab-minio lab-ssh1 lab-ssh2; do
  check "$c démarré" "[ \"\$(docker inspect -f '{{.State.Running}}' $c)\" = true ]"
done
echo "== Services joignables =="
check "Nginx      http://127.0.0.1:8081" "curl -fsS http://127.0.0.1:8081/"
check "API statut http://127.0.0.1:8000/health" "curl -fsS http://127.0.0.1:8000/health"
check "MinIO      http://127.0.0.1:9000/minio/health/live" "curl -fsS http://127.0.0.1:9000/minio/health/live"
check "Redis      127.0.0.1:6379" "bash -c 'exec 3<>/dev/tcp/127.0.0.1/6379'"
check "Postgres   127.0.0.1:5432" "bash -c 'exec 3<>/dev/tcp/127.0.0.1/5432'"
check "SSH app01  127.0.0.1:2221" "bash -c 'exec 3<>/dev/tcp/127.0.0.1/2221'"
check "SSH app02  127.0.0.1:2222" "bash -c 'exec 3<>/dev/tcp/127.0.0.1/2222'"
echo
echo "Résultat : $ok OK, $ko KO"
[ "$ko" -eq 0 ] && echo "Labo prêt." || echo "Voir la page Dépannage du guide formateur."
exit "$ko"

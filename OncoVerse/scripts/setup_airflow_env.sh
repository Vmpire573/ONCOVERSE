#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -e .env.local ]]; then
  echo "Using existing .env.local (secrets were not changed)."
  exit 0
fi
umask 077
AIRFLOW_DB_PASSWORD="$(openssl rand -hex 24)"
AIRFLOW_ADMIN_PASSWORD="$(openssl rand -hex 24)"
AIRFLOW_SECRET_KEY="$(openssl rand -hex 32)"
AIRFLOW_FERNET_KEY="$(openssl rand -base64 32 | tr -d '\n')"
cat > .env.local <<EOF
AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASSWORD=$AIRFLOW_DB_PASSWORD
AIRFLOW_ADMIN_PASSWORD=$AIRFLOW_ADMIN_PASSWORD
AIRFLOW_SECRET_KEY=$AIRFLOW_SECRET_KEY
AIRFLOW_FERNET_KEY=$AIRFLOW_FERNET_KEY
EOF
chmod 600 .env.local
echo "Created .env.local with local-only secrets (mode 600). Do not share or commit it."

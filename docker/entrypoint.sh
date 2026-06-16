#!/bin/sh
set -e

mkdir -p /app/var

# Na primeira subida o volume está vazio: popula com os dados já processados no build.
if [ ! -f /app/var/poscomp.sqlite3 ]; then
  echo "[entrypoint] populando /app/var com dados processados no build..."
  cp -a /app/var_seed/. /app/var/
fi

exec "$@"

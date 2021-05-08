#!/bin/bash
cd /opt/codecarbon
set -e
sleep 1
# echo "$DATABASE_USER@$DATABASE_HOST:$DATABASE_PORT"
# until PGPASSWORD=$DATABASE_PASS psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -c '\q'; do
#   >&2 echo "Postgres is unavailable - sleeping"
#   sleep 1
# done
  
# >&2 echo "Postgres is up !"

echo "codecarbon : Alembic migrate..."
alembic upgrade head
echo "codecarbon : starting..."
python3 -m uvicorn main:app --reload
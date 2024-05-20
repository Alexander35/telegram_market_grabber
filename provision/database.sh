#!/bin/bash

export PGPASS=$POSTGRES_PASSWORD
export PGUSER=$POSTGRES_POSTGRES_USER

#export PGPASSWORD=$POSTGRES_PASSWORD; psql -h postgres -U postgres_user -d express_accounting -c "CREATE DATABASE ...;"

alembic upgrade head

echo ALL Migrations are complete

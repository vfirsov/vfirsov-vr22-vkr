#!/bin/sh
set -eu

python manage_catalog.py prepare
exec gunicorn --bind 0.0.0.0:8080 --no-control-socket --workers 1 --threads 2 --access-logfile - --error-logfile - app:app

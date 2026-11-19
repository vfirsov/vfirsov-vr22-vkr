#!/bin/sh
set -eu

python manage_catalog.py prepare
exec python -m granian --interface wsgi --host 0.0.0.0 --port 8080 --blocking-threads 2 --access-log app:app

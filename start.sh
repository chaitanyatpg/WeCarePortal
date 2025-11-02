#!/bin/bash
echo "🚀 Starting WeCarePortal with gunicorn..."
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py loaddata mycareportal_app/fixtures/*.json
exec gunicorn mycareportal.wsgi:application --bind 0.0.0.0:8080 --workers 2 --timeout 120
#!/bin/bash
echo "🚀 Starting WeCarePortal with gunicorn..."
echo "📊 Running migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "📂 Loading fixtures..."
python manage.py loaddata mycareportal_app/fixtures/activity_master.json || echo "Failed to load activity_master"
python manage.py loaddata mycareportal_app/fixtures/activity_tasks.json || echo "Failed to load activity_tasks"
python manage.py loaddata mycareportal_app/fixtures/all_state.json || echo "Failed to load all_state"

echo "🌐 Starting gunicorn server..."
exec gunicorn mycareportal.wsgi:application --bind 0.0.0.0:8080 --workers 2 --timeout 120 --log-level debug
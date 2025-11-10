#!/bin/bash
echo "🚀 Starting WeCarePortal with gunicorn..."
echo "📊 Running migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "📂 Loading all fixtures..."
python manage.py loaddata mycareportal_app/fixtures/activity_master.json || echo "❌ Failed: activity_master"
python manage.py loaddata mycareportal_app/fixtures/activity_sub_category.json || echo "❌ Failed: activity_sub_category"
python manage.py loaddata mycareportal_app/fixtures/activity_tasks.json || echo "❌ Failed: activity_tasks"
python manage.py loaddata mycareportal_app/fixtures/all_state.json || echo "❌ Failed: all_state"
python manage.py loaddata mycareportal_app/fixtures/assessment_categories.json || echo "❌ Failed: assessment_categories"
python manage.py loaddata mycareportal_app/fixtures/assessment_tasks.json || echo "❌ Failed: assessment_tasks"
python manage.py loaddata mycareportal_app/fixtures/client_match_categories.json || echo "❌ Failed: client_match_categories"
python manage.py loaddata mycareportal_app/fixtures/client_match_criteria.json || echo "❌ Failed: client_match_criteria"
python manage.py loaddata mycareportal_app/fixtures/default_incidents.json || echo "❌ Failed: default_incidents"
python manage.py loaddata mycareportal_app/fixtures/incident_locations.json || echo "❌ Failed: incident_locations"
python manage.py loaddata mycareportal_app/fixtures/invoice_rate_type.json || echo "❌ Failed: invoice_rate_type"
python manage.py loaddata mycareportal_app/fixtures/task_template.json || echo "❌ Failed: task_template"
python manage.py loaddata mycareportal_app/fixtures/task_template_entry.json || echo "❌ Failed: task_template_entry"
python manage.py loaddata mycareportal_app/fixtures/task_template_subcategory.json || echo "❌ Failed: task_template_subcategory"

echo "🌐 Starting gunicorn server..."
exec gunicorn mycareportal.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level debug
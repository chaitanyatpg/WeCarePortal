web: gunicorn mycareportal.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py collectstatic --noinput && python manage.py migrate && python create_mock_data.py
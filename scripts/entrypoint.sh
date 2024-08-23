python manage.py collectstatic
gunicorn --access-logfile - --workers=3 --bind 0.0.0.0:8000 --log-level debug star_burger.wsgi:application

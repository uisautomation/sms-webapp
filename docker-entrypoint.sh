#!/bin/sh
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Use gunicorn as a web-server after running migration command
gunicorn \
	--name smswebapp \
	--bind :$PORT \
	--workers 3 \
	--log-level=info \
	--log-file=- \
	--access-logfile=- \
	--capture-output \
	smswebapp.wsgi

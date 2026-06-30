#!/bin/sh

# Зупиняємо скрипт, якщо якась із команд видасть помилку
set -e

echo "Applying database migrations..."
python manage.py migrate

echo "Loading standard fixtures (Grammar)..."
python manage.py loaddata grammar_data.json

echo "Running custom seed commands (Words & Texts)..."
# Викликаємо твої кастомні команди
python manage.py load_words
python manage.py load_texts

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn eng_site.wsgi:application --bind 0.0.0.0:8000
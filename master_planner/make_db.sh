#!/usr/bin/env bash

set -o errexit  # exit on error

python manage.py flush --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py populate_db
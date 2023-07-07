#!/usr/bin/env bash

set -o errexit  # exit on error
cd theme/static_src
npm i --production
cd ../..

pip install -r requirements.txt
python manage.py tailwind build
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

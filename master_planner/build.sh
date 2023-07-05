#!/usr/bin/env bash

set -o errexit  # exit on error

pip install -r requirements.txt
cd theme/static_src
npm i --production
cd ../..

python manage.py tailwind build
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

#!/usr/bin/env bash

set -o errexit  # exit on error

pip install -r requirements.txt

python master_planner/manage.py collectstatic --no-input
python master_planner/manage.py makemigrations
python master_planner/manage.py migrate


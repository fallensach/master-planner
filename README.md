# Master-planner
A webapplication to help students pick their master courses at LiU

## Dependencies
This project requires Python 3.10.X or above and that npm and node is installed on your pc.

To install the projects dependencies run:
> bash install_dependencies.sh

## Tailwind
> Tailwind is included in the development version. To use it you need npm installed.
>
> To use tailwind use:
>
> **python ./manage.py tailwind start**

## Development scripts
There is currently 1 script to help with development.
> reset_db.sh - This script deletes the migration files and remigrates the whole database.

## Deployment migrations
Before deploying the application:

> python manage.py makemigrations
> Commit migration files
> Push the migration files to deployment repo

Whenever you change models in development you have to make the new migration files and push them into the production repo.
When you have the new migration files you can run the command:
> bash make_db.sh

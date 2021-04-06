#!/usr/bin/env bash
# entrypoint.sh

echo "start"

# host="$1"
# shift
# cmd="$@"
sleep 20
# echo "connecting"

# until PGPASSWORD="Difficultpasswd123" psql -h "db" -U "postgres" -c '\q'; do
#   >&2 echo "Postgres is unavailable - sleeping"
#   sleep 1
# done

# while pg_isready -h "db" -p "5432" > /dev/null 2> /dev/null; do
#     echo "Connecting to db Failed"
#     sleep 1
#   done
  
echo "connected"

>&2 echo "Postgres is up - executing command"
exec $cmd

echo "command executed"

python manage.py makemigrations
python manage.py migrate --noinput
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'DifficultParol123')"
gunicorn project.wsgi:application -b 0.0.0.0:8000 --workers 4

echo "end"
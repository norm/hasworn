#!/bin/sh

if [ "$SQL_ENGINE" = 'django.db.backends.postgresql' ]; then
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done
fi

exec "$@"

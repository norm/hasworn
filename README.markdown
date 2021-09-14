hasworn
=======

A place to collection my tshirt wearing history.


## Pre-requisites for working locally

* docker and docker-compose: brew install --cask docker --or-- brew install docker docker-compose
* flask: pip install flask
* libsass: pip install libsass
* entr: brew install entr


## Generated static sites

Running in development:

    # bring up the stack
    export HASWORN_ENV=dev
    ./compose build
    ./start

    # if this is a new checkout, or volumes have been removed
    ./manage collectstatic --noinput
    ./manage migrate
    DJANGO_SUPERUSER_PASSWORD=norm ./manage createsuperuser \
        --username norm --email norm@example.com --noinput

To test a generated hasworn site:

    ./manage import_csv sample/norm.csv

To preview the generated site:

    ./update_css
    python static.py

To automatically remake the CSS when developing it:

    find sass -type f | entr -d ./update_css

When done developing:

    # shut down temporarily
    ./compose down

    # shut down and remove volumes to start afresh (or when development stops)
    ./compose down --volumes --remove-orphans


## Scripts

Scripts to interact with docker-compose, using the right configuration and
environment files. These **default to production**; in development set the
environment variable `HASWORN_ENV=dev` first.

  * **compose**

    Run a docker-compose operation.

      ./compose down

  * **start**

    Bring up all hasworn services with docker-compose.

        ./start

  * **manage**

    Shortcut to running `manage.py` commands inside the app container.

        ./manage makemigrations
        ./manage migrate

  * **cert**

    Register Let's Encrypt certificates.

        ./cert

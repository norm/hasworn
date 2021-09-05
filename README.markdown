hasworn
=======

A place to collection my tshirt wearing history.



## Generated static sites

Running in development:

    # bring up the stack
    export HASWORN_ENV=dev
    ./start

    # if this is a new checkout, or volumes have been removed
    ./manage collectstatic --noinput
    ./manage migrate
    DJANGO_SUPERUSER_PASSWORD=norm ./manage createsuperuser \
        --username norm --email norm@example.com --noinput

To test a generated hasworn site:

    ./manage import_csv sample/norm.csv

To preview the generated site:

    # needs flask, one time run: pip install flask
    python static.py

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

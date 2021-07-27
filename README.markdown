hasworn
=======

A place to collection my tshirt wearing history.



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

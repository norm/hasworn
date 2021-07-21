#!/usr/bin/env -S bash -euo pipefail
#
# Redeploy the hasworn django app.

IP_ADDRESS='{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'


function main {
    reset_checkout_to_main
    migrate_database
    start_new_image
    remove_old_image
}

function reset_checkout_to_main {
    git fetch github
    git reset --hard github/main

    export DOCKER_IMAGE=sha-$(git show-ref --hash=7 main | head -1)

    docker pull ghcr.io/norm/hasworn:$DOCKER_IMAGE
}

function migrate_database {
    docker-compose \
        -f docker-compose.yml \
        -f docker-compose-prod.yml \
            run --rm -T app \
                python manage.py migrate --noinput
}

function start_new_image {
    scale_app 2

    new_id=$(docker ps -f name=app -q | head -1)
    new_addr=$(docker inspect -f $IP_ADDRESS $new_id)

    curl \
        --silent \
        --retry 20 \
        --retry-delay 1 \
        --retry-connrefused \
        --fail \
        --header "Host: app" \
        http://$new_addr:8000/ \
            > /dev/null \
                || exit 1

    reload_nginx
}

function remove_old_image {
    current_id=$(docker ps -f name=app -q | tail -1)

    docker stop $current_id
    docker rm $current_id
    scale_app 1

    reload_nginx
}

function scale_app {
    local count="${1:-1}"

    docker-compose \
        -f docker-compose.yml \
        -f docker-compose-prod.yml \
            up -d \
            --no-deps \
            --scale=app=${count} \
            --no-recreate \
            app
}

function reload_nginx {
    docker-compose exec -T nginx /usr/sbin/nginx -s reload
}

main

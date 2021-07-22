#!/usr/bin/env -S bash -euo pipefail
#
# Fetch and deploy the given version of the application.

IP_ADDRESS='{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'


function main {
    fetch_docker_image
    migrate_database
    start_new_image
    remove_old_image
}

function run_compose {
    docker-compose \
        -f docker-compose.yml \
        -f docker-compose-prod.yml \
            "$@"
}

function fetch_docker_image {
    docker pull ghcr.io/norm/hasworn:sha-$COMMIT_SHA
}

function migrate_database {
    run_compose run --rm -T app \
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

    run_compose up -d \
        --no-deps \
        --scale=app=${count} \
        --no-recreate \
        app
}

function reload_nginx {
    run_compose exec -T nginx /usr/sbin/nginx -s reload
}

main

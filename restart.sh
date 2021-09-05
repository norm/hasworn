#!/usr/bin/env -S bash -euo pipefail
#
# Fetch and deploy the given version of the application.

IP_ADDRESS='{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'


function main {
    update_env_file
    fetch_docker_image
    migrate_database
    update_static_files
    start_new_image
    restart_celery
    remove_old_image
    prune_docker
    regenerate_apex
}

function run_compose {
    docker-compose \
        -f docker-compose.yml \
        -f docker-compose-prod.yml \
            "$@"
}

function update_env_file {
    echo COMMIT_SHA=$COMMIT_SHA > environ.commit
}

function fetch_docker_image {
    docker pull ghcr.io/norm/hasworn:sha-$COMMIT_SHA
}

function migrate_database {
    run_compose run --rm -T app \
        python manage.py migrate --noinput
}

function update_static_files {
    run_compose run --rm -T app \
        python manage.py collectstatic --noinput
}

function regenerate_apex {
    run_compose run --rm -T app \
        python manage.py generate_apex
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
        --header "Host: i.hasworn.com" \
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

function restart_celery {
    run_compose restart celery
}

function prune_docker {
    docker image prune --force --all --filter 'until=168h'
    docker container prune --force
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

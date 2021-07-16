#!/usr/bin/env -S bash -euo pipefail

export DOCKER_IMAGE=sha-$(git show-ref --hash=7 main | head -1)

docker-compose \
    -f docker-compose.yml \
    -f docker-compose-prod.yml \
        up -d

docker-compose \
    logs -tf --tail=2

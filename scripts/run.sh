#! /usr/bin/env sh

# Exit in case of error
set -e

TAG=LOCAL
docker compose -f ../docker-compose.yml up -d

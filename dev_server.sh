#!/usr/bin/env bash
set -Eeuo pipefail

docker-compose run \
  --rm \
  -u $(id -u):$(id -g) \
  --volume=/mnt/data:/app/data \
  --volume=/mnt/out:/app/out \
  --volume=/mnt/models:/app/models \
  dev-gpu

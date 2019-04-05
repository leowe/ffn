#!/usr/bin/env bash
set -Eeuo pipefail

docker-compose run \
  --rm \
  -u $(id -u):$(id -g) \
  dev

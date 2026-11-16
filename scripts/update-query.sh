#!/usr/bin/env bash

set -euo pipefail

pull_image=true
if [[ "${1:-}" == "--no-pull" ]]; then
  pull_image=false
  shift
fi
if [[ "$#" -ne 0 ]]; then
  printf '用法：%s [--no-pull]\n' "$0" >&2
  exit 2
fi

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${workspace_root}"

compose=(docker compose -f docker-compose-query.yml)

"${compose[@]}" config --quiet

if [[ "${pull_image}" == true ]]; then
  printf '正在拉取 aio-life-query 镜像...\n'
  "${compose[@]}" pull aio-life-query
fi

printf '正在更新 aio-life-query 容器...\n'
"${compose[@]}" up -d --no-deps --no-build --pull never aio-life-query

"${compose[@]}" ps aio-life-query

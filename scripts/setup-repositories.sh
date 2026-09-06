#!/usr/bin/env bash

set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

clone_repository() {
  local name="$1"
  local remote="$2"
  local target="${workspace_root}/${name}"
  local repository_root=""

  if [[ -d "${target}" ]]; then
    repository_root="$(git -C "${target}" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ "${repository_root}" == "${target}" ]]; then
      printf '%s 已存在，跳过克隆。\n' "${name}"
      return
    fi

    printf '错误：%s 已存在，但不是独立 Git 仓库。\n' "${target}" >&2
    exit 1
  fi

  git clone "${remote}" "${target}"
}

clone_repository "aio-life-front" "git@github.com:lys1313013/aio-life-front.git"
clone_repository "aio-life-server" "git@github.com:lys1313013/aio-life-server.git"

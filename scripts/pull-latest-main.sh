#!/usr/bin/env bash

set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pull_main() {
  local name="$1"
  local target="${workspace_root}/${name}"
  local repository_root=""
  local branch=""

  if [[ ! -d "${target}" ]]; then
    printf '错误：缺少 %s，请先运行 ./scripts/setup-repositories.sh。\n' "${name}" >&2
    exit 1
  fi

  repository_root="$(git -C "${target}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ "${repository_root}" != "${target}" ]]; then
    printf '错误：%s 不是独立 Git 仓库。\n' "${target}" >&2
    exit 1
  fi

  if [[ -n "$(git -C "${target}" status --porcelain)" ]]; then
    printf '错误：%s 存在未提交修改，已停止拉取。\n' "${name}" >&2
    exit 1
  fi

  branch="$(git -C "${target}" branch --show-current)"
  if [[ "${branch}" != "main" ]]; then
    printf '错误：%s 当前位于 %s 分支，请切换到 main 后重试。\n' "${name}" "${branch:-detached HEAD}" >&2
    exit 1
  fi

  printf '正在拉取 %s 的最新 main...\n' "${name}"
  git -C "${target}" pull --ff-only origin main
}

pull_main "aio-life-front"
pull_main "aio-life-server"

printf '前后端 main 均已更新完成。\n'

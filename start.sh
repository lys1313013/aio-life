#!/usr/bin/env bash

set -euo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repositories=(aio-life-server aio-life-front aio-life-mobile)
service_pids=()

for repository in "${repositories[@]}"; do
  repository_dir="${workspace_root}/${repository}"
  if [[ ! -d "${repository_dir}" ]]; then
    printf '错误：缺少 %s，请先运行 ./scripts/setup-repositories.sh。\n' "${repository}" >&2
    exit 1
  fi
  if [[ ! -f "${repository_dir}/start.sh" || ! -x "${repository_dir}/start.sh" ]]; then
    printf '错误：%s/start.sh 缺失或不可执行。\n' "${repository}" >&2
    exit 1
  fi
done

# 为每个启动脚本分配独立的进程组，以便一并停止 Maven、Vite 等子进程。
set -m
stop_services() {
  local index pid
  for index in "${!service_pids[@]}"; do
    pid="${service_pids[index]}"
    kill -TERM -- "-${pid}" 2>/dev/null || true
  done
  wait
}

trap stop_services EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

for repository in "${repositories[@]}"; do
  printf '正在启动 %s...\n' "${repository}"
  (
    cd "${workspace_root}/${repository}"
    exec ./start.sh
  ) &
  service_pids+=("$!")
done
# 后续轮询留在前台进程组，让 Ctrl+C 能传给启动器。
set +m

# macOS 自带的 Bash 3.2 不支持 wait -n。
while true; do
  for index in "${!service_pids[@]}"; do
    pid="${service_pids[index]}"
    if ! kill -0 "${pid}" 2>/dev/null; then
      status=0
      wait "${pid}" || status=$?
      printf '%s 已退出（状态 %s），正在停止其余服务。\n' "${repositories[index]}" "${status}" >&2
      exit "$((status == 0 ? 1 : status))"
    fi
  done
  sleep 1
done

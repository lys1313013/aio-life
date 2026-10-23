#!/usr/bin/env python3
"""Synchronize generated contracts in isolated GitHub Actions checkouts only."""

import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = {
    "front": ("aio-life-front", "apps/web-antd/src/api/payload.ts"),
    "mobile": ("aio-life-mobile", "src/services/api-payload.ts"),
}
REPOSITORIES = {"server": "aio-life-server", **{key: row[0] for key, row in CLIENTS.items()}}


def git(directory, *args, capture=False):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(ROOT / directory), *args],
        check=True, text=True, stdout=subprocess.PIPE if capture else None,
    ).stdout


def assert_clean(directory, allowed=None):
    changes = git(directory, "status", "--porcelain=v1", "-z", capture=True)
    for entry in filter(None, changes.split("\0")):
        if entry[:2] not in (" M", "M ") or entry[3:] != allowed:
            raise RuntimeError(f"Unexpected worktree change in {directory}: {entry}")


def synchronize():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("Run this script only in isolated GitHub Actions checkouts.")
    for directory in REPOSITORIES.values():
        assert_clean(directory)

    for attempt in range(1, 5):
        print(f"Contract synchronization attempt {attempt}/4", flush=True)
        for key, directory in REPOSITORIES.items():
            target = CLIENTS[key][1] if key in CLIENTS else None
            assert_clean(directory, target)
            if target:
                git(directory, "restore", "--source=HEAD", "--staged", "--worktree", "--", target)
            git(directory, "fetch", "--no-tags", "origin", "+refs/heads/main:refs/remotes/origin/main")
            if key == "server":
                git(directory, "checkout", "--detach", "refs/remotes/origin/main")
            else:
                git(directory, "checkout", "-B", "main", "refs/remotes/origin/main")

        # A concurrent frontend push may also update its locked formatter dependencies.
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"], cwd=ROOT / "aio-life-front",
            env={**os.environ, "HUSKY": "0", "LEFTHOOK": "0"}, check=True,
        )
        subprocess.run([sys.executable, str(ROOT / "scripts/generate-api-contracts.py")], check=True)
        retry = False
        for directory, target in CLIENTS.values():
            assert_clean(directory, target)
            git(directory, "add", "--", target)
            if not git(directory, "diff", "--cached", "--name-only", capture=True).strip():
                continue
            git(directory, "diff", "--cached", "--check")
            git(directory, "-c", "user.name=github-actions[bot]", "-c",
                "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "commit", "-m", "chore(api): 自动同步后端请求契约")
            try:
                git(directory, "push", "origin", "HEAD:refs/heads/main")
            except subprocess.CalledProcessError:
                # Never force-push over an independent client delivery. Refresh and regenerate.
                retry = True
                break

        revisions = {}
        if not retry:
            for key, directory in REPOSITORIES.items():
                head = git(directory, "rev-parse", "HEAD", capture=True).strip()
                remote = git(directory, "ls-remote", "--exit-code", "origin",
                             "refs/heads/main", capture=True).split()[0]
                if head != remote:
                    retry = True
                revisions[key] = head
        if not retry:
            with open(os.environ["GITHUB_OUTPUT"], "a") as output:
                for key, revision in revisions.items():
                    output.write(f"{key}_sha={revision}\n")
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
                summary.write("## API contracts synchronized\n\nBoth generated files are on remote main before checking.\n\n")
                summary.write("| Repository | Checked commit |\n| --- | --- |\n")
                summary.write(f"| aio-life (generator) | {git('.', 'rev-parse', 'HEAD', capture=True).strip()} |\n")
                for key, revision in revisions.items():
                    summary.write(f"| {REPOSITORIES[key]} | {revision} |\n")
            return
        if attempt < 4:
            time.sleep(5)
    raise SystemExit("Repositories changed during synchronization or push was rejected. Retry this workflow; no force-push was used.")


if __name__ == "__main__":
    synchronize()

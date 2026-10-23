#!/usr/bin/env python3
"""Generate contracts locally, push all repositories, then request a read-only check."""

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = {
    "aio-life-front": "apps/web-antd/src/api/payload.ts",
    "aio-life-mobile": "src/services/api-payload.ts",
}
REPOSITORIES = ("aio-life-server", *CLIENTS, ".")
AUTOMATION = (
    "scripts/generate-api-contracts.py", "scripts/push-repositories.py",
    ".github/workflows/api-contracts.yml",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-hooks", action="store_true", help="Skip Git hooks when explicitly requested.")
    args = parser.parse_args()

    def run(*command, cwd=ROOT, capture=False):
        return subprocess.run(command, cwd=cwd, check=True, text=True,
                              stdout=subprocess.PIPE if capture else None).stdout

    def git(repo, *command, capture=False):
        options = ("-c", "core.hooksPath=/dev/null") if args.skip_hooks else ()
        return run("git", *options, "-C", str(ROOT / repo), *command, capture=capture)

    # Business changes must already be reviewed and committed. Never stage them implicitly.
    for repo in REPOSITORIES:
        directory = (ROOT / repo).resolve()
        if Path(git(repo, "rev-parse", "--show-toplevel", capture=True).strip()) != directory:
            raise SystemExit(f"{repo}: not an independent repository; run scripts/setup-repositories.sh first.")
        if git(repo, "branch", "--show-current", capture=True).strip() != "main":
            raise SystemExit(f"{repo}: switch to main before unified delivery.")
        paths = AUTOMATION if repo == "." else ()
        if git(repo, "status", "--porcelain", "--", *paths, capture=True).strip():
            raise SystemExit(f"{repo}: commit intended changes first; no worktree changes were discarded.")
    if not (ROOT / "aio-life-front/node_modules/.bin/prettier").exists():
        raise SystemExit("Install frontend dependencies with pnpm install first.")
    run("gh", "auth", "status", capture=True)
    for repo in REPOSITORIES:
        git(repo, "pull", "--ff-only", "origin", "main")

    run(sys.executable, str(ROOT / "scripts/generate-api-contracts.py"))
    for repo in REPOSITORIES:
        paths = AUTOMATION if repo == "." else ()
        allowed = CLIENTS.get(repo)
        changes = git(repo, "status", "--porcelain=v1", "-z", "--", *paths, capture=True)
        for entry in filter(None, changes.split("\0")):
            if entry[:2] != " M" or entry[3:] != allowed:
                raise SystemExit(f"{repo}: unexpected concurrent change; review it and rerun delivery.")
    for repo, target in CLIENTS.items():
        if git(repo, "diff", "--name-only", "HEAD", "--", target, capture=True).strip():
            git(repo, "diff", "--check", "--", target)
            git(repo, "add", "--", target)
            git(repo, "commit", "--only", "-m", "chore(api): 同步后端请求契约", "--", target)

    revisions = {repo: git(repo, "rev-parse", "HEAD", capture=True).strip() for repo in REPOSITORIES}
    for repo in REPOSITORIES:
        git(repo, "push", "origin", f"{revisions[repo]}:refs/heads/main")
    for repo, revision in revisions.items():
        remote = git(repo, "ls-remote", "--exit-code", "origin", "refs/heads/main", capture=True).split()[0]
        if remote != revision:
            raise SystemExit(f"{repo}: remote main changed during delivery; rerun before requesting the joint check.")

    # All three business repositories (and this generator) are now on the remote.
    run(sys.executable, str(ROOT / "scripts/generate-api-contracts.py"), "--check")
    run("gh", "workflow", "run", "api-contracts.yml", "--repo", "lys1313013/aio-life", "--ref", "main",
        "-f", f"generator_sha={revisions['.']}",
        "-f", f"server_sha={revisions['aio-life-server']}",
        "-f", f"front_sha={revisions['aio-life-front']}",
        "-f", f"mobile_sha={revisions['aio-life-mobile']}")
    print("All repositories pushed; read-only CI check requested for these commits:")
    for repo, revision in revisions.items():
        print(f"{repo}: {revision}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"Delivery stopped: {error}. Earlier pushes may have succeeded; no force-push or rollback was used.") from error

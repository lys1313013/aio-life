#!/usr/bin/env python3
"""Update all Query components from CI images and regenerate matching metadata."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'aio-life-query'
COMPOSE = ['docker', 'compose', '-f', str(ROOT / 'docker-compose-query.yml')]
SERVICES = ['aio-life-query', 'hasura', 'postgresql-connector']


def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-pull', action='store_true', help='Use images already pulled from the registry')
    args = parser.parse_args()
    run(COMPOSE + ['config', '--quiet'])
    revision = run(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    run(['git', '-C', str(SOURCE), 'diff', '--quiet', 'HEAD'])
    if not args.no_pull:
        run(COMPOSE + ['pull', *SERVICES])
    # Capture configuration privately: it contains database and service credentials.
    config = json.loads(run(COMPOSE + ['config', '--format', 'json'], capture_output=True, text=True).stdout)
    for name in SERVICES:
        image = config['services'][name]['image']
        labels = json.loads(run(['docker', 'image', 'inspect', image, '--format', '{{json .Config.Labels}}'],
                                capture_output=True, text=True).stdout) or {}
        if labels.get('org.opencontainers.image.revision') != revision:
            raise SystemExit(f'{name}: image revision differs from aio-life-query checkout {revision}; use matching sha tags/digests')
    query = config['services']['aio-life-query']['environment']
    connector = config['services']['postgresql-connector']['environment']
    mount = next(volume for volume in config['services']['hasura']['volumes'] if volume['target'] == '/metadata')
    output = Path(mount['source'])
    backup = ROOT / 'backups' / ('query-stack-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir(parents=True, mode=0o700)
    if output.exists():
        shutil.copytree(output, backup / 'metadata')
    print('Metadata backup: ' + str(backup), flush=True)
    environment = dict(os.environ, AIO_QUERY_WEBHOOK_KEY=query['AIO_QUERY_WEBHOOK_KEY'],
                       AIO_QUERY_CONNECTOR_KEY=connector['HASURA_SERVICE_TOKEN_SECRET'],
                       AIO_QUERY_CONNECTOR_URL='http://postgresql-connector:8080',
                       AIO_QUERY_AUTH_WEBHOOK_URL='http://aio-life-query:45680/internal/hasura/auth')
    run(['python3', str(SOURCE / 'scripts/build_metadata.py'), '--output', str(output)], env=environment)
    expected_gid = int(config['services']['hasura']['group_add'][0])
    if output.stat().st_gid != expected_gid:
        raise SystemExit('Generated metadata group differs from AIO_QUERY_CONFIG_GID; adjust ownership before starting')
    run(COMPOSE + ['up', '-d', '--no-deps', '--no-build', '--pull', 'never', '--force-recreate', *SERVICES])
    checks = [
        ['exec', '-T', 'aio-life-query', 'wget', '-q', '-T', '3', '-t', '1', '-O', '/dev/null', 'http://127.0.0.1:45681/actuator/health'],
        ['exec', '-T', 'aio-life-query', 'wget', '-q', '-T', '3', '-t', '1', '-O', '/dev/null', 'http://hasura:3000/health'],
        ['exec', '-T', 'postgresql-connector', '/bin/ndc-postgres', 'check-health'],
    ]
    for _ in range(60):
        if all(subprocess.run(COMPOSE + check, cwd=ROOT, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode == 0 for check in checks):
            run(COMPOSE + ['ps', *SERVICES])
            print('Query stack is healthy; query authorization still requires an end-to-end check.')
            return
        time.sleep(1)
    raise SystemExit('Query stack readiness failed; inspect Compose logs. Metadata backup: ' + str(backup))


if __name__ == '__main__':
    main()

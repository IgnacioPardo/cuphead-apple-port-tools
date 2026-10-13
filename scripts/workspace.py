"""Shared paths for private, user-owned recovery outputs."""
import hashlib
import json
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MARKER = '.cuphead-private-workspace.json'


def inside(path, parent):
    return path == parent or parent in path.parents


def external_path(value):
    path = Path(value).expanduser().resolve()
    if inside(path, REPOSITORY) or inside(REPOSITORY, path):
        raise ValueError('Use a separate directory outside the tooling repository.')
    return path


def open_workspace(value, create=False):
    root = external_path(value)
    marker = root / MARKER
    if create and not marker.exists():
        if root.exists() and any(root.iterdir()):
            raise ValueError('New workspace must be empty; existing contents will not be adopted.')
        root.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({'format': 1, 'private_generated_content': True}) + '\n')
        (root / '.gitignore').write_text('*\n')
    if not marker.is_file() or json.loads(marker.read_text()).get('format') != 1:
        raise ValueError('Initialize a private workspace with recover.py first.')
    for name in ('input', 'recovered', 'evidence', 'builds'):
        directory = root / name
        if directory.is_symlink():
            raise ValueError('Workspace output directories must not be symlinks.')
        directory.mkdir(exist_ok=True)
    return root


def digest(path):
    checksum = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')

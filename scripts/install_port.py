#!/usr/bin/env python3
"""Install original helpers into a separate, user-managed Unity project."""
import argparse
import hashlib
from pathlib import Path
import shutil

from workspace import REPOSITORY, external_path


def install(project, game_adapters=False):
    project = external_path(project)
    if not (project / 'Assets').is_dir() or not (project / 'ProjectSettings/ProjectVersion.txt').is_file():
        raise ValueError('Expected an existing Unity project. Raw game folders are not Unity projects.')
    if (project / 'Temp/UnityLockfile').exists():
        raise ValueError('Close the project in Unity before installing helpers.')
    if (project / 'Assets').is_symlink():
        raise ValueError('Assets must not be a symlink.')
    folders = ['Runtime', 'Editor'] + (['Integration'] if game_adapters else [])
    operations = []
    for folder in folders:
        for source in sorted((REPOSITORY / 'port' / folder).glob('*.cs')):
            destination = project / 'Assets/CupheadApplePort' / folder / source.name
            # Never escape through an existing link or introduce duplicate classes.
            if destination.resolve() != destination:
                raise ValueError('Install destination contains a symlink.')
            for existing in (project / 'Assets').rglob(source.name):
                if existing != destination:
                    raise ValueError('A helper with this filename already exists: ' + source.name)
            if destination.exists() and destination.read_bytes() != source.read_bytes():
                raise ValueError('Existing helper was modified; refusing to overwrite: ' + source.name)
            meta = Path(str(destination) + '.meta')
            if meta.is_symlink():
                raise ValueError('Metadata must not be a symlink.')
            operations.append((source, destination, meta))
    for source, destination, meta in operations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copyfile(source, destination)
        if not meta.exists():
            guid = hashlib.sha256(('cuphead-apple-port-tools/' + str(source.relative_to(REPOSITORY))).encode()).hexdigest()[:32]
            meta.write_text('fileFormatVersion: 2\nguid: ' + guid + '\n')
    print('Installed ' + str(len(operations)) + ' helpers. No recovered game source was patched.')
    return len(operations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--game-adapters', action='store_true',
                        help='Also install adapters requiring locally recovered game and Rewired APIs.')
    args = parser.parse_args()
    try:
        install(args.project, args.game_adapters)
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()

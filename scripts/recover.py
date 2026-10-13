#!/usr/bin/env python3
"""Snapshot a user-supplied Mono build; optionally decompile it with local ILSpy."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

from workspace import digest, external_path, inside, open_workspace, write_json

ASSEMBLIES = ('Assembly-CSharp', 'Assembly-CSharp-firstpass', 'GalaxyCSharp',
              'Rewired_Core', 'Rewired_Windows_Lib')


def resolve_game(game_dir=None, app=None):
    if bool(game_dir) == bool(app):
        raise ValueError('Specify exactly one of --game-dir or --app.')
    path = Path(game_dir) if game_dir else Path(app) / 'Contents/Resources/drive_c/GOG Games/Cuphead'
    path = external_path(path)
    if not (path / 'Cuphead_Data/Managed/Assembly-CSharp.dll').is_file():
        raise ValueError('Expected a Mono build with Cuphead_Data/Managed/Assembly-CSharp.dll.')
    return path


def snapshot(game, root):
    source = game / 'Cuphead_Data/Managed'
    target = root / 'input/Managed'
    if target.is_symlink():
        raise ValueError('Managed output must not be a symlink.')
    target.mkdir(exist_ok=True)
    records = []
    # Validate the complete snapshot before copying anything.
    for path in sorted(source.iterdir()):
        if path.is_symlink():
            raise ValueError('Managed inputs must not contain symlinks.')
        if path.suffix not in ('.dll', '.mdb') or not path.is_file():
            continue
        if path.suffix == '.dll' and path.read_bytes()[:2] != b'MZ':
            raise ValueError('Managed input is not a PE file; check for unfetched LFS pointers.')
        checksum = digest(path)
        dest = target / path.name
        if dest.is_symlink() or (dest.exists() and digest(dest) != checksum):
            raise ValueError('Workspace already contains a different assembly snapshot.')
        records.append({'file': path.name, 'bytes': path.stat().st_size, 'sha256': checksum})
    for entry in records:
        dest = target / entry['file']
        if not dest.exists():
            shutil.copyfile(source / entry['file'], dest)
    write_json(root / 'evidence/source.json', {
        'source_game': str(game), 'managed': records,
        'scope': 'Local input paths and hashes; keep this report private.'})
    return target


def decompile(managed, root, ilspy):
    tool = shutil.which(str(ilspy))
    if not tool:
        raise ValueError('ILSpy executable not found. Pass --ilspy /path/to/ilspycmd.')
    missing = [name for name in ASSEMBLIES if not (managed / (name + '.dll')).is_file()]
    if missing:
        raise ValueError('Unsupported build; missing assemblies: ' + ', '.join(missing))
    if any((root / 'recovered' / name).exists() for name in ASSEMBLIES):
        raise ValueError('Raw recovery already exists; use a new workspace to rerun decompilation.')
    environment = os.environ.copy()
    dotnet = shutil.which('dotnet')
    if dotnet and 'DOTNET_ROOT' not in environment:
        binary = Path(dotnet).resolve()
        for candidate in (binary.parent, binary.parent.parent / 'libexec'):
            if (candidate / 'host/fxr').is_dir():
                environment['DOTNET_ROOT'] = str(candidate)
                break
    results = []
    for name in ASSEMBLIES:
        output = root / 'recovered' / name
        command = [tool, '--disable-updatecheck', '-p', '-lv', 'CSharp7_3',
                   '-r', str(managed), '-o', str(output), str(managed / (name + '.dll'))]
        with (root / 'evidence' / (name + '.ilspy.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
        results.append({'assembly': name, 'returncode': result.returncode,
                        'source_files': len(list(output.rglob('*.cs')))})
        write_json(root / 'evidence/recovery.json', results)
        print(name + ': ' + str(result.returncode))
        if result.returncode:
            raise RuntimeError('Decompilation failed; inspect the private workspace log.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--game-dir', type=Path)
    group.add_argument('--app', type=Path)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--ilspy', help='Omit to snapshot assemblies without decompiling.')
    args = parser.parse_args()
    try:
        game = resolve_game(args.game_dir, args.app)
        destination = external_path(args.workspace)
        if inside(game, destination) or inside(destination, game):
            raise ValueError('Source installation and workspace must be separate directories.')
        root = open_workspace(destination, create=True)
        managed = snapshot(game, root)
        if args.ilspy:
            decompile(managed, root, args.ilspy)
        print('Private recovery complete. No generated game content belongs in the tooling repository.')
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()

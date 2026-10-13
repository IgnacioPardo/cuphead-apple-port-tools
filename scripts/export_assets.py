#!/usr/bin/env python3
"""Run a separately installed AssetRipper against the private source manifest."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from workspace import external_path, inside, open_workspace

SETTINGS = {
    'ScriptExportMode': 'Decompiled', 'ShaderExportMode': 'Decompile',
    'SpriteExportMode': 'Yaml', 'ScriptLanguageVersion': 'AutoSafe',
    'ScriptContentLevel': 'Level2', 'ImageExportFormat': 'Png',
    'AudioExportFormat': 'Default', 'TextExportMode': 'Parse',
    'PreferOriginalTextureExtension': 'true',
}


def export(root, executable, port):
    source = Path(json.loads((root / 'evidence/source.json').read_text())['source_game']).resolve()
    if not (source / 'Cuphead_Data').is_dir():
        raise ValueError('The original source installation is unavailable.')
    if inside(source, root) or inside(root, source):
        raise ValueError('Source and workspace must be separate directories.')
    output = root / 'exports'
    if output.exists():
        raise ValueError('Export path already exists; AssetRipper deletes existing output. Use a new workspace.')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', port))
        port = probe.getsockname()[1]
    base = 'http://127.0.0.1:' + str(port)
    def post(path, data):
        with urllib.request.urlopen(base + path, urllib.parse.urlencode(data).encode(), timeout=3600) as reply:
            reply.read()
    with (root / 'evidence/assetripper-server.log').open('w') as log:
        process = subprocess.Popen([str(executable), '--headless', '--port', str(port),
                                    '--log-path', str(root / 'evidence/assetripper-export.log')],
                                   cwd=root, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(120):
                if process.poll() is not None:
                    raise RuntimeError('AssetRipper exited; inspect the private server log.')
                try:
                    with urllib.request.urlopen(base, timeout=1):
                        break
                except (OSError, urllib.error.URLError):
                    time.sleep(0.5)
            else:
                raise RuntimeError('AssetRipper did not become ready.')
            post('/Settings/Update', SETTINGS)
            post('/LoadFolder', {'Path': str(source)})
            post('/Export/UnityProject', {'Path': str(output), 'CreateSubfolder': 'false'})
            if not (output / 'ExportedProject/Assets').is_dir():
                raise RuntimeError('Expected export missing; inspect private logs.')
            print('Raw export completed. It still requires migration, shader reconstruction, and asset repair.')
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--assetripper', required=True, type=Path, help='AssetRipper 2.0.0 executable')
    parser.add_argument('--port', type=int, default=0, help='Local API port; 0 selects an available port.')
    args = parser.parse_args()
    try:
        export(open_workspace(args.workspace), external_path(args.assetripper), args.port)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()

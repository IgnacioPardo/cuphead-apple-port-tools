#!/usr/bin/env python3
"""Compile local recovered/repaired C# against the user's original references."""
import argparse
from pathlib import Path
import shutil
import subprocess

from workspace import open_workspace, write_json

ASSEMBLIES = ('Assembly-CSharp-firstpass', 'GalaxyCSharp', 'Assembly-CSharp')


def compiler():
    dotnet = shutil.which('dotnet')
    if not dotnet:
        raise ValueError('.NET SDK 8 is required.')
    lines = subprocess.check_output([dotnet, '--list-sdks'], text=True).splitlines()
    sdks = []
    for line in lines:
        version, location = line.split(' ', 1)
        if version.startswith('8.'):
            sdks.append((tuple(map(int, version.split('.'))), version, location.strip('[]')))
    if not sdks:
        raise ValueError('.NET SDK 8 is required; no matching installed SDK found.')
    _, version, directory = max(sdks)
    return dotnet, Path(directory) / version / 'Roslyn/bincore/csc.dll', version


def compile_sources(root, source='src'):
    dotnet, csc, version = compiler()
    out = root / 'builds' / ('managed-' + source)
    out.mkdir(parents=True, exist_ok=True)
    managed = root / 'input/Managed'
    if not (managed / 'UnityEngine.dll').is_file():
        raise ValueError('Original Unity references are missing; run recover.py first.')
    built = {}
    results = []
    for name in ASSEMBLIES:
        sources = sorted((root / source / name).rglob('*.cs'))
        if not sources:
            raise ValueError('No sources for ' + name)
        args = ['-nologo', '-target:library', '-nostdlib+', '-unsafe+', '-langversion:7.3',
                '-out:"' + str(out / (name + '.dll')) + '"']
        args += ['-reference:"' + str(built.get(p.stem, p)) + '"'
                 for p in sorted(managed.glob('*.dll')) if p.stem != name]
        args += ['"' + str(p) + '"' for p in sources]
        if any('\n' in value or '\r' in value for value in args):
            raise ValueError('Compiler paths must not contain newlines.')
        response = out / (name + '.rsp')
        response.write_text('\n'.join(args) + '\n')
        result = subprocess.run([dotnet, str(csc), '@' + str(response)], capture_output=True, text=True)
        log = result.stdout + result.stderr
        (root / 'evidence' / (name + '.' + source + '.compile.log')).write_text(log)
        results.append({'assembly': name, 'returncode': result.returncode,
                        'errors': sum(': error ' in line for line in log.splitlines()),
                        'warnings': sum(': warning ' in line for line in log.splitlines()),
                        'source_files': len(sources), 'sdk': version})
        if result.returncode == 0:
            built[name] = out / (name + '.dll')
        print(name + ': exit=' + str(result.returncode))
    write_json(root / 'evidence' / ('compile-' + source + '.json'), {
        'scope': 'Managed compilation only; no Unity runtime or native build validation.',
        'results': results})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--source', choices=('src', 'recovered'), default='src')
    args = parser.parse_args()
    try:
        results = compile_sources(open_workspace(args.workspace), args.source)
        raise SystemExit(int(any(r['returncode'] for r in results)))
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()

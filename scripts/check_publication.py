#!/usr/bin/env python3
"""Check the reviewed file list, working tree, index, and all local Git refs.

This is a conservative publication gate, not legal clearance or a complete
secret detector. It reports locations and rule names without printing values.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 256 * 1024
ALLOWED_SUFFIXES = {'.py', '.cs', '.csproj', '.md', '.json', '.yml', '.yaml'}
FORBIDDEN_TOP = {'input', 'recovered', 'src', 'unity-project', 'exports', 'builds',
                 'evidence', 'tools', 'migration-quarantine', 'workspace'}
RULES = {
    'private key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'GitHub token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b',
    'AWS access key': rb'\bAKIA[0-9A-Z]{16}\b',
    'literal credential': rb'(?i)\b(?:clientSecret|client_secret|apiKey|api_key|password)\s*[:=]\s*["\x27][^"\x27\r\n]{8,}["\x27]',
    'personal absolute path': rb'/(?:Users|Volumes|home)/[A-Za-z0-9_. -]+/',
    'Apple signing team': rb'\bappleDeveloperTeamID:\s*[A-Z0-9]{10}\b',
    'Apple device identifier': rb'\b[0-9A-F]{8}-[0-9A-F]{16}\b',
}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def inspect_content(name, data):
    issues = []
    if len(data) > MAX_BYTES:
        return [name + ': exceeds publication file size limit']
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return [name + ': non-text payload']
    if b'\x00' in data:
        issues.append(name + ': binary payload')
    if data.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
        issues.append(name + ': LFS pointer')
    for label, pattern in RULES.items():
        if re.search(pattern, data):
            issues.append(name + ': ' + label)
    return issues


def inspect_path(name, allowed):
    path = Path(name)
    problems = []
    if name not in allowed:
        problems.append(name + ': not in reviewed public-files.json')
    if path.parts[0] in FORBIDDEN_TOP:
        problems.append(name + ': private output directory')
    if path.suffix not in ALLOWED_SUFFIXES and name not in {'.gitignore', 'LICENSE'}:
        problems.append(name + ': unsupported file type')
    return problems


def audit(root, history=True):
    root = Path(root).resolve()
    allowed = set(json.loads((root / 'public-files.json').read_text())['files'])
    issues = []
    current = set(git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')) - {''}
    for name in sorted(current):
        issues.extend(inspect_path(name, allowed))
        path = root / name
        if path.is_symlink() or not path.is_file():
            issues.append(name + ': missing file or symlink')
        else:
            issues.extend(inspect_content(name, path.read_bytes()))
    for name in sorted(allowed - current):
        issues.append(name + ': reviewed file is missing or ignored')
    seen = set()
    blobs = 0
    def check_blob(mode, oid, name, context):
        nonlocal blobs
        issues.extend(context + ': ' + problem for problem in inspect_path(name, allowed))
        if mode not in ('100644', '100755'):
            issues.append(context + ': ' + name + ': symlink, submodule, or unsupported mode')
            return
        if oid in seen:
            return
        seen.add(oid)
        blobs += 1
        size = int(git(root, 'cat-file', '-s', oid))
        if size > MAX_BYTES:
            issues.append(context + ': ' + name + ': exceeds publication file size limit')
        else:
            data = git(root, 'cat-file', 'blob', oid)
            issues.extend(context + ': ' + problem for problem in inspect_content(name, data))
    for entry in git(root, 'ls-files', '--stage', '-z').decode().split('\0'):
        if not entry:
            continue
        meta, name = entry.split('\t', 1)
        mode, oid, stage = meta.split()
        if stage != '0':
            issues.append(name + ': unresolved index conflict')
        check_blob(mode, oid, name, 'index')
    commits = git(root, 'rev-list', '--all').decode().splitlines() if history else []
    for commit in commits:
        for entry in git(root, 'ls-tree', '-r', '-z', commit).decode().split('\0'):
            if not entry:
                continue
            meta, name = entry.split('\t', 1)
            mode, kind, oid = meta.split()
            check_blob(mode, oid, name, commit[:12])
    return sorted(set(issues)), {'working_files': len(current), 'commits': len(commits), 'git_objects': blobs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-history', action='store_true', help='For initial local checks only; publication requires history.')
    args = parser.parse_args()
    try:
        issues, counts = audit(ROOT, not args.no_history)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, 'Publication check could not complete: ' + type(exc).__name__ + '\n')
    if issues:
        print('\n'.join(issues))
        parser.exit(1, 'FAIL: publication findings require review. Values have been withheld.\n')
    print('PASS: ' + json.dumps(counts) + '. Reviewed text files only; no flagged payloads or credentials.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Record architecture and observed player-log evidence; does not simulate input."""
import argparse
import datetime
import hashlib
import json
import plistlib
import re
import subprocess
from pathlib import Path

from workspace import external_path
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--app', type=Path, required=True)
parser.add_argument('--log', type=Path, help='Optional captured player log')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.app = external_path(args.app)
args.output = external_path(args.output)
if args.log is not None:
    args.log = external_path(args.log)
args.output.parent.mkdir(parents=True, exist_ok=True)
is_macos = (args.app / 'Contents/Info.plist').exists()
plist_path = args.app / ('Contents/Info.plist' if is_macos else 'Info.plist')
with plist_path.open('rb') as source:
    info = plistlib.load(source)
executable = args.app / ('Contents/MacOS' if is_macos else '') / info['CFBundleExecutable']
binaries = [executable]
for directory in (['Contents/Frameworks', 'Contents/Plugins'] if is_macos else ['Frameworks', 'PlugIns']):
    if (args.app / directory).exists():
        for path in (args.app / directory).rglob('*'):
            if path.is_file() and not path.is_symlink():
                kind = subprocess.check_output(['file', '-b', str(path)], text=True).strip()
                if 'Mach-O' in kind:
                    binaries.append(path)
binary_records = []
for path in binaries:
    binary_records.append({
        'path': str(path.relative_to(args.app)),
        'file': subprocess.check_output(['file', '-b', str(path)], text=True).strip(),
        'architectures': subprocess.check_output(['lipo', '-archs', str(path)], text=True).strip().split(),
        'build_version': subprocess.check_output(['xcrun', 'vtool', '-show-build', str(path)], text=True).strip(),
        'sha256': hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(path.read_bytes()).hexdigest(),
    })
log = args.log.read_text(errors='replace') if args.log is not None and args.log.exists() else ''
starts = re.findall(r'APPLE_PORT_START [^\r\n]+', log)
scenes = re.findall(r'APPLE_PORT_SCENE name=(\S+) frame=(\d+)', log)
frames = re.findall(r'APPLE_PORT_FRAME scene=(\S+) frame=(\d+) realtime=([\d.]+)', log)
controllers = re.findall(r'APPLE_PORT_CONTROLLERS[^\r\n]*', log)
buttons = re.findall(r'APPLE_PORT_BUTTON player=(-?\d+) action=(\d+)', log)
axes = re.findall(r'APPLE_PORT_AXIS player=(-?\d+) x=([-\d.]+) y=([-\d.]+)', log)
errors = [line for line in log.splitlines() if re.search(r'\b\w*Exception:|DllNotFound|EntryPointNotFound|Shader error|Crash!!!', line)]
report = {
    'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'app': str(args.app), 'log': str(args.log) if args.log is not None else None, 'binaries': binary_records,
    'bundle_identifier': info['CFBundleIdentifier'],
    'supported_platforms': info.get('CFBundleSupportedPlatforms', []),
    'controller_profiles': info.get('GCSupportedGameControllers', []),
    'all_binaries_arm64_only': all(b['architectures'] == ['arm64'] for b in binary_records),
    'startup': starts, 'scenes': [{'scene': s, 'frame': int(f)} for s, f in scenes],
    'frame_samples': [{'scene': s, 'frame': int(f), 'realtime': float(t)} for s, f, t in frames],
    'frames_advanced': len(frames) >= 2 and int(frames[-1][1]) > int(frames[0][1]),
    'runtime_error_lines': errors,
    'controller_samples': controllers,
    'button_samples': [{'player': int(p), 'action': int(a)} for p, a in buttons],
    'axis_samples': [{'player': int(p), 'x': float(x), 'y': float(y)} for p, x, y in axes],
    'scope': 'Architecture and log evidence only. Visuals, input, audio, and gameplay require separate observation.'
}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['all_binaries_arm64_only', 'startup', 'scenes', 'frames_advanced', 'runtime_error_lines']}, indent=2))

if not report['all_binaries_arm64_only'] or report['runtime_error_lines']:
    raise SystemExit(1)

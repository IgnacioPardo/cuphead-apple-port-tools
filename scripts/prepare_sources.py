#!/usr/bin/env python3
"""Repair the known ILSpy compilation artifacts in a new private working copy."""
import argparse
from pathlib import Path
import re
import shutil

from compile_managed import ASSEMBLIES, compile_sources
from workspace import digest, open_workspace, write_json


def repair_iterator_refs(text, expected):
    # These three ILSpy temporaries alias an assignable value. Inline the alias
    # into the immediately following assignment, preserving the target/value.
    pattern = re.compile(r'(?m)^(\s*)ref \w+ reference = ref ([\w.]+(?:\[[^\]\n]+\])?);\n'
                         r'\s*(reference(?:\.[xy])? = [^;\n]+;)')
    def replace(match):
        return match[1] + re.sub(r'\breference\b', match[2], match[3])
    result, count = pattern.subn(replace, text)
    if count != expected:
        raise ValueError('Unexpected iterator recovery layout; refusing to guess a repair.')
    return result


def repair_character_labels(text, lines):
    source = text.splitlines(keepends=True)
    if len(lines) != 15 or len(set(lines)) != 15:
        raise ValueError('Expected 15 distinct character-switch diagnostics for this build.')
    for number in lines:
        if number < 1 or number > len(source):
            raise ValueError('Compiler line outside source.')
        line = source[number - 1]
        if not re.fullmatch(r'\s*case \d+:\s*', line):
            raise ValueError('Diagnostic is not a numeric case label.')
        source[number - 1] = re.sub(r'case (\d+):', r'case (char)\1:', line)
    return ''.join(source)


def prepare(root):
    target = root / 'src'
    if target.exists():
        raise ValueError('src already exists; working sources will not be overwritten.')
    # Generate the diagnostics ourselves instead of depending on an old local log.
    compile_sources(root, 'recovered')
    gameplay = root / 'recovered/Assembly-CSharp'
    paths = {'DevilLevelGiantHead.cs': 1, 'RetroArcadePaddleShip.cs': 2}
    changes = {name: repair_iterator_refs((gameplay / name).read_text(), count)
               for name, count in paths.items()}
    log = (root / 'evidence/Assembly-CSharp.recovered.compile.log').read_text()
    numbers = [int(n) for n in re.findall(r'TMPro[/\\]TMP_Text.cs\((\d+),\d+\): error CS0266', log)]
    changes['TMPro/TMP_Text.cs'] = repair_character_labels((gameplay / 'TMPro/TMP_Text.cs').read_text(), numbers)
    for name in ASSEMBLIES:
        shutil.copytree(root / 'recovered' / name, target / name)
    records = []
    for name, text in changes.items():
        path = target / 'Assembly-CSharp' / name
        path.write_text(text)
        records.append({'file': name, 'before_sha256': digest(gameplay / name), 'after_sha256': digest(path)})
    write_json(root / 'evidence/source-repairs.json', records)
    return compile_sources(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    args = parser.parse_args()
    try:
        results = prepare(open_workspace(args.workspace))
        raise SystemExit(int(any(r['returncode'] for r in results)))
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()

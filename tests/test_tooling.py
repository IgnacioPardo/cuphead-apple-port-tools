import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_publication
import install_port
import prepare_sources
import recover
import workspace


class WorkspaceTests(unittest.TestCase):
    def test_repository_and_ancestors_rejected(self):
        for path in [workspace.REPOSITORY, workspace.REPOSITORY / 'ignored', workspace.REPOSITORY.parent]:
            with self.assertRaises(ValueError):
                workspace.external_path(path)

    def test_symlink_into_repository_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            alias = Path(temp) / 'linked'
            alias.symlink_to(workspace.REPOSITORY, target_is_directory=True)
            with self.assertRaises(ValueError):
                workspace.external_path(alias / 'workspace')

    def test_existing_directory_not_adopted(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'keep').write_text('existing work')
            with self.assertRaises(ValueError):
                workspace.open_workspace(temp, create=True)
            self.assertEqual((Path(temp) / 'keep').read_text(), 'existing work')

    def test_snapshot_mismatch_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / 'game/Cuphead_Data/Managed'
            source.mkdir(parents=True)
            assembly = source / 'Assembly-CSharp.dll'
            assembly.write_bytes(b'MZsynthetic-one')
            root = workspace.open_workspace(base / 'private', create=True)
            recover.snapshot(base / 'game', root)
            assembly.write_bytes(b'MZsynthetic-two')
            with self.assertRaises(ValueError):
                recover.snapshot(base / 'game', root)
            self.assertEqual((root / 'input/Managed/Assembly-CSharp.dll').read_bytes(), b'MZsynthetic-one')

    def test_lfs_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / 'game/Cuphead_Data/Managed'
            source.mkdir(parents=True)
            (source / 'Assembly-CSharp.dll').write_text('version https://git-lfs.github.com/spec/v1\n')
            root = workspace.open_workspace(base / 'private', create=True)
            with self.assertRaises(ValueError):
                recover.snapshot(base / 'game', root)


class InstallTests(unittest.TestCase):
    def test_idempotent_and_refuses_edited_files(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'project'
            (project / 'Assets').mkdir(parents=True)
            (project / 'ProjectSettings').mkdir()
            (project / 'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.5f1\n')
            count = install_port.install(project)
            self.assertGreater(count, 0)
            self.assertEqual(install_port.install(project), count)
            source = project / 'Assets/CupheadApplePort/Runtime/LocalSaveStore.cs'
            source.write_text('local modification')
            with self.assertRaises(ValueError):
                install_port.install(project)
            self.assertEqual(source.read_text(), 'local modification')


class RepairTests(unittest.TestCase):
    def test_inline_alias_preserves_target_and_expression(self):
        source = '\tref Vector reference = ref direction;\n\treference.y = (int)reference.y * -1;\n'
        self.assertEqual(prepare_sources.repair_iterator_refs(source, 1),
                         '\tdirection.y = (int)direction.y * -1;\n')
        with self.assertRaises(ValueError):
            prepare_sources.repair_iterator_refs(source, 2)

    def test_character_repair_only_changes_diagnostic_lines(self):
        source = ''.join('case ' + str(n) + ':\n' for n in range(16))
        result = prepare_sources.repair_character_labels(source, list(range(1, 16)))
        self.assertIn('case 15:\n', result)
        self.assertEqual(result.count('(char)'), 15)
        with self.assertRaises(ValueError):
            prepare_sources.repair_character_labels(source, [1] * 15)


class PublicationTests(unittest.TestCase):
    def test_literal_credential_is_reported_without_value(self):
        value = 'synthetic-value-for-testing'
        data = ('client' + 'Secret = "' + value + '";').encode()
        issues = check_publication.inspect_content('sample.cs', data)
        self.assertTrue(any('literal credential' in issue for issue in issues))
        self.assertNotIn(value, '\n'.join(issues))

    def test_binary_and_lfs_are_rejected(self):
        self.assertTrue(check_publication.inspect_content('sample.py', b'MZ\x00fake'))
        data = ('version https://git-lfs.github.com/spec/v1' + '\n').encode()
        self.assertTrue(check_publication.inspect_content('sample.py', data))

    def test_staged_and_historical_content_cannot_hide_behind_working_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)
            git('init', '-b', 'main')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            (root / 'public-files.json').write_text(json.dumps({'files': {'public-files.json': 'test', 'sample.py': 'test'}}))
            synthetic = 'client' + 'Secret = "synthetic-credential"\n'
            (root / 'sample.py').write_text(synthetic)
            git('add', '.')
            (root / 'sample.py').write_text('# clean\n')
            issues, _ = check_publication.audit(root)
            self.assertTrue(any(issue.startswith('index:') for issue in issues))
            git('commit', '-m', 'Synthetic historical fixture')
            git('add', '.')
            git('commit', '-m', 'Remove synthetic credential')
            issues, counts = check_publication.audit(root)
            self.assertEqual(counts['commits'], 2)
            self.assertTrue(any('literal credential' in issue for issue in issues))
            self.assertFalse(any(issue.startswith('index:') for issue in issues))

    def test_private_directory_rejected_even_if_added_to_manifest(self):
        path = 'recovered/example.cs'
        issues = check_publication.inspect_path(path, {path})
        self.assertTrue(any('private output directory' in issue for issue in issues))


if __name__ == '__main__':
    unittest.main()

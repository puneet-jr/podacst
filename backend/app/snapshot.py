from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re

from backend.app.transcripts import SOURCE_URL


class SnapshotError(ValueError):
    pass


@dataclass
class Snapshot:
    root: Path
    revision: str
    files: dict[str, str]
    source_url: str = SOURCE_URL
    kind: str = 'corpus'
    complete: bool = True

    @classmethod
    def load(cls, root):
        root = Path(root).resolve()
        manifest = Path(str(root) + '.manifest.json')
        data = json.loads(manifest.read_text())
        if not re.fullmatch(r'[0-9a-f]{40}', data['corpus_revision']) or data['source_url'] != SOURCE_URL:
            raise SnapshotError('invalid_snapshot_identity')
        listed = data['files']
        paths = [item['path'] for item in listed]
        actual = sorted(str(p.relative_to(root)) for p in (root/'episodes').rglob('*') if p.is_file() and p.name.casefold() == 'transcript.md')
        if len(paths) != len(set(paths)) or sorted(paths) != actual or len(actual) != data['discovered']:
            raise SnapshotError('snapshot_manifest_file_mismatch')
        snapshot = cls(root, data['corpus_revision'], {item['path']: item['sha256'] for item in listed})
        for path in snapshot.files:
            snapshot.read(path)
        if not paths: raise SnapshotError('empty_snapshot_refused')
        return snapshot

    def read(self, path):
        relative = PurePosixPath(path)
        file = (self.root/path).resolve()
        if relative.is_absolute() or '..' in relative.parts or not file.is_relative_to(self.root.resolve()):
            raise SnapshotError('unsafe_source_path')
        data = file.read_bytes()
        if sha256(data).hexdigest() != self.files[path]: raise SnapshotError('source_changed_after_manifest')
        return data

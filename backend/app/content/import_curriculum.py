"""Import a curriculum manifest or an ordered index of manifests.

Usage (from the backend directory):

    python -m app.content.import_curriculum content/curriculum/demo/rest-apis.yaml
    python -m app.content.import_curriculum content/curriculum/v1-index.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.content.importer import import_manifest
from app.content.schema import CurriculumIndex, ManifestError
from app.content.validate import validate_manifest, topic_slugs_from_data
from app.db.migrate import ensure_optional_columns
from app.db.session import Base, SessionLocal, engine

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

SKIP_DIR_NAMES = {"_examples"}


def load_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise SystemExit("PyYAML is required to import YAML manifests. pip install pyyaml")
        data = yaml.safe_load(text)
    elif path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        raise SystemExit(f"Unsupported file type: {path.suffix}")
    if not isinstance(data, dict):
        raise SystemExit(f"{path} did not contain a manifest object")
    return data


def expand_targets(path: Path) -> list[Path]:
    data = load_file(path)
    if data.get("kind") == "curriculum_index":
        index = CurriculumIndex.model_validate(data)
        return [(path.parent / rel).resolve() for rel in index.files]
    return [path]


def validate_manifest_group(datas: list[dict]) -> None:
    """Validate manifests together so cross-file prerequisites resolve.

    next_topic must still exist in the *same* file or already-imported DB slugs
    unless the caller passes the full slug set via existing_topic_slugs on each
    file. This helper uses the union of all topic slugs in the group so an
    official index can be checked before import. Cross-file next_topic is
    allowed only when the target slug is in the group (i.e. will exist after
    the full index import).
    """
    all_slugs: set[str] = set()
    for data in datas:
        if data.get("kind") != "curriculum_manifest":
            continue
        all_slugs |= topic_slugs_from_data(data)
    for data in datas:
        if data.get("kind") != "curriculum_manifest":
            continue
        validate_manifest(data, existing_topic_slugs=all_slugs)


def import_path(path: Path) -> dict[str, int]:
    Base.metadata.create_all(bind=engine)
    ensure_optional_columns(engine)
    data = load_file(path)
    if data.get("kind") == "curriculum_index":
        raise ManifestError([f"{path} is an index; expand it before import_path"])
    db = SessionLocal()
    try:
        return import_manifest(db, data)
    finally:
        db.close()


def iter_manifest_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        if path.name == "v1-index.yaml":
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import a curriculum manifest")
    parser.add_argument("path", nargs="?", help="YAML/JSON manifest or v1-index.yaml")
    parser.add_argument(
        "--dir",
        dest="directory",
        help="Import every YAML/JSON file under this directory (skips _examples). Prefer v1-index.yaml for official V1.",
    )
    args = parser.parse_args(argv)

    targets: list[Path] = []
    if args.path:
        targets.extend(expand_targets(Path(args.path)))
    if args.directory:
        targets.extend(iter_manifest_files(Path(args.directory)))
    if not targets:
        parser.print_help()
        return 2

    try:
        datas = [load_file(target) for target in targets]
        if len(datas) > 1:
            validate_manifest_group(datas)
        for target in targets:
            if not target.exists():
                print(f"File not found: {target}", file=sys.stderr)
                return 1
            stats = import_path(target)
            print(
                f"Imported {target}: created={stats.get('created', 0)} "
                f"updated={stats.get('updated', 0)} unchanged={stats.get('unchanged', 0)} "
                f"skipped_resources={stats.get('skipped_resources', 0)}"
            )
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

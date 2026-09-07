#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "src" / "client"
DEFAULT_OUTPUT = ROOT / "src" / "host" / "updates" / "current"
EXCLUDED_FILES = {
    "app/__init__.py",
    "app/ota_boot.py",
    "app/updater.py",
    "boot.py",
    "config/device.ini",
    "config/network.ini",
}
EXCLUDED_DIRS = {"__pycache__", ".update-stage", ".update-backup", "database", "logs"}
DEFAULT_REMOVALS = ["buffers/buffers.py"]


def deployable_files(source):
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError("symlinks are not deployable: " + str(relative))
        if not path.is_file():
            continue
        relative_name = relative.as_posix()
        if relative_name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        yield path, relative


def package(version, source=CLIENT, output=DEFAULT_OUTPUT, removals=()):
    source = Path(source).resolve()
    output = Path(output).resolve()
    if not version.strip():
        raise ValueError("version must not be empty")
    if output.exists():
        shutil.rmtree(output)
    files_root = output / "files"
    files_root.mkdir(parents=True)

    copied = []
    for source_path, relative in deployable_files(source):
        destination = files_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)
        copied.append((destination, relative))

    version_path = files_root / "config" / "version.py"
    version_path.parent.mkdir(parents=True, exist_ok=True)
    version_path.write_text('APP_VERSION = "{}"\n'.format(version), encoding="utf-8")
    copied = [item for item in copied if item[1].as_posix() != "config/version.py"]
    copied.append((version_path, Path("config/version.py")))

    entries = []
    for path, relative in sorted(copied, key=lambda item: item[1].as_posix()):
        data = path.read_bytes()
        entries.append(
            {
                "path": relative.as_posix(),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    manifest = {
        "version": version,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "files": entries,
        "remove": sorted(set(DEFAULT_REMOVALS + list(removals))),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Package ESP32 application files for Message Box OTA"
    )
    parser.add_argument("version", help="application version to publish")
    parser.add_argument("--source", type=Path, default=CLIENT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--remove", action="append", default=[])
    args = parser.parse_args()
    manifest = package(args.version, args.source, args.output, args.remove)
    print(
        "Packaged {} files for version {} at {}".format(
            len(manifest["files"]), manifest["version"], args.output
        )
    )


if __name__ == "__main__":
    main()

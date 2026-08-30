"""Assemble immutable textbook and Python artifacts for a course release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tomllib
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "build" / "course-release"
DEFAULT_DIST = PROJECT_ROOT / "dist"
DEFAULT_TEXTBOOK = PROJECT_ROOT / "textbook" / "textbook.pdf"
TEXTBOOK_NAME = "data-science-machine-learning-textbook.pdf"


def sha256(path: Path) -> str:
    """Return the hexadecimal SHA-256 digest of a file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_version() -> str:
    """Read the package version from the project's authoritative metadata."""

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
        document = tomllib.load(stream)
    return str(document["project"]["version"])


def generated_at(value: str | None = None) -> str:
    """Return an explicit or reproducible UTC build timestamp."""

    if value:
        return value
    source_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_epoch:
        instant = datetime.fromtimestamp(int(source_epoch), tz=UTC)
    else:
        instant = datetime.now(tz=UTC)
    return instant.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_release_bundle(
    *,
    output: Path,
    dist: Path,
    textbook: Path,
    tag: str,
    revision: str,
    timestamp: str | None = None,
) -> Path:
    """Collect release files, provenance metadata, and SHA-256 checksums."""

    expected_tag = f"course-v{project_version()}"
    if tag != expected_tag:
        raise ValueError(
            f"Release tag {tag!r} does not match package version {expected_tag!r}."
        )
    if not revision.strip():
        raise ValueError("A nonempty source revision is required.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Release output must be empty: {output}")
    if not textbook.is_file():
        raise FileNotFoundError(f"Compiled textbook not found: {textbook}")

    package_version = project_version()
    distributions = [
        dist / f"rice_dsm-{package_version}-py3-none-any.whl",
        dist / f"rice_dsm-{package_version}.tar.gz",
    ]
    missing_distributions = [path for path in distributions if not path.is_file()]
    if missing_distributions:
        missing_names = ", ".join(path.name for path in missing_distributions)
        raise FileNotFoundError(
            f"Expected versioned Python distributions in dist/: {missing_names}"
        )

    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(textbook, output / TEXTBOOK_NAME)
    for distribution in distributions:
        shutil.copyfile(distribution, output / distribution.name)

    release_files = sorted(path for path in output.iterdir() if path.is_file())
    manifest = {
        "schema_version": 1,
        "course": "CMOR 438 / INDE 577",
        "tag": tag,
        "revision": revision,
        "package_version": package_version,
        "generated_at": generated_at(timestamp),
        "artifacts": [
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in release_files
        ],
    }
    manifest_path = output / "release-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    checksum_files = [*release_files, manifest_path]
    checksum_text = "".join(
        f"{sha256(path)}  {path.name}\n" for path in sorted(checksum_files)
    )
    (output / "SHA256SUMS").write_text(
        checksum_text,
        encoding="utf-8",
        newline="\n",
    )
    return output


def parse_args() -> argparse.Namespace:
    """Parse the command-line contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    parser.add_argument("--textbook", type=Path, default=DEFAULT_TEXTBOOK)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--timestamp")
    return parser.parse_args()


def main() -> None:
    """Build the bundle and print its location."""

    arguments = parse_args()
    output = build_release_bundle(
        output=arguments.output.resolve(),
        dist=arguments.dist.resolve(),
        textbook=arguments.textbook.resolve(),
        tag=arguments.tag,
        revision=arguments.revision,
        timestamp=arguments.timestamp,
    )
    print(f"Built course release: {output}")


if __name__ == "__main__":
    main()

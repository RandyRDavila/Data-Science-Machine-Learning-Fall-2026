"""Build the bounded static artifact deployed to the public course site."""

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
SITE_SOURCE = PROJECT_ROOT / "site"
DEFAULT_OUTPUT = PROJECT_ROOT / "build" / "course-site"
DEFAULT_TEXTBOOK = (
    PROJECT_ROOT / "output" / "pdf" / "data-science-machine-learning-textbook.pdf"
)
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


def build_course_site(
    *,
    output: Path,
    textbook: Path,
    revision: str,
    timestamp: str | None = None,
) -> Path:
    """Build a complete static site into an empty output directory.

    Raises
    ------
    FileExistsError
        If the output directory is not empty. Refusing to merge with an old
        artifact prevents stale files from surviving a deployment.
    FileNotFoundError
        If reviewed source assets or the compiled textbook are missing.
    ValueError
        If a source revision is empty.
    """

    if not revision.strip():
        raise ValueError("A nonempty source revision is required.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Site output must be empty: {output}")
    if not textbook.is_file():
        raise FileNotFoundError(f"Compiled textbook not found: {textbook}")

    template_path = SITE_SOURCE / "index.html"
    stylesheet_path = SITE_SOURCE / "styles.css"
    favicon_path = SITE_SOURCE / "favicon.svg"
    if not all(
        path.is_file() for path in (template_path, stylesheet_path, favicon_path)
    ):
        raise FileNotFoundError("The reviewed site source is incomplete.")

    output.mkdir(parents=True, exist_ok=True)
    textbook_output = output / "textbook" / TEXTBOOK_NAME
    textbook_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(stylesheet_path, output / "styles.css")
    shutil.copyfile(favicon_path, output / "favicon.svg")
    shutil.copyfile(textbook, textbook_output)

    built_at = generated_at(timestamp)
    substitutions = {
        "{{PACKAGE_VERSION}}": project_version(),
        "{{REVISION_SHORT}}": revision[:12],
        "{{GENERATED_AT}}": built_at,
    }
    html = template_path.read_text(encoding="utf-8")
    for marker, replacement in substitutions.items():
        html = html.replace(marker, replacement)
    if "{{" in html or "}}" in html:
        raise ValueError("The generated page contains an unresolved template marker.")
    (output / "index.html").write_text(html, encoding="utf-8", newline="\n")
    (output / "404.html").write_text(html, encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": 1,
        "course": "CMOR 438 / INDE 577",
        "package_version": project_version(),
        "revision": revision,
        "generated_at": built_at,
        "artifacts": {
            "textbook": {
                "path": f"textbook/{TEXTBOOK_NAME}",
                "bytes": textbook_output.stat().st_size,
                "sha256": sha256(textbook_output),
            }
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return output


def parse_args() -> argparse.Namespace:
    """Parse the command-line contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--textbook", type=Path, default=DEFAULT_TEXTBOOK)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--timestamp")
    return parser.parse_args()


def main() -> None:
    """Build the site and print the artifact location."""

    arguments = parse_args()
    output = build_course_site(
        output=arguments.output.resolve(),
        textbook=arguments.textbook.resolve(),
        revision=arguments.revision,
        timestamp=arguments.timestamp,
    )
    print(f"Built course site: {output}")


if __name__ == "__main__":
    main()

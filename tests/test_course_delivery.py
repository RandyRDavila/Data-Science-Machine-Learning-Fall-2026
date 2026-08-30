"""Tests for the static-site and tagged-release delivery contracts."""

from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest

from scripts.build_course_site import build_course_site, project_version
from scripts.build_release_bundle import build_release_bundle
from scripts.smoke_test_course_site import verify_course_site

PROJECT_ROOT = Path(__file__).parents[1]
REVISION = "0123456789abcdef0123456789abcdef01234567"
TIMESTAMP = "2026-08-30T12:00:00Z"


class PageStructureParser(HTMLParser):
    """Collect the small set of accessibility structures the site requires."""

    def __init__(self) -> None:
        super().__init__()
        self.language: str | None = None
        self.identifiers: set[str] = set()
        self.links: list[str] = []
        self.script_count = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Record semantic attributes without a browser dependency."""

        attributes = dict(attrs)
        if tag == "html":
            self.language = attributes.get("lang")
        if identifier := attributes.get("id"):
            self.identifiers.add(identifier)
        if tag == "a" and (href := attributes.get("href")):
            self.links.append(href)
        if tag == "script":
            self.script_count += 1


def write_fake_pdf(path: Path) -> bytes:
    """Write the smallest useful PDF-shaped fixture."""

    content = b"%PDF-1.7\n% course delivery fixture\n%%EOF\n"
    path.write_bytes(content)
    return content


def test_course_site_builder_records_revision_and_textbook_identity(
    tmp_path: Path,
) -> None:
    textbook = tmp_path / "textbook.pdf"
    textbook_content = write_fake_pdf(textbook)
    output = tmp_path / "site"

    build_course_site(
        output=output,
        textbook=textbook,
        revision=REVISION,
        timestamp=TIMESTAMP,
    )

    page = (output / "index.html").read_text(encoding="utf-8")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    artifact = manifest["artifacts"]["textbook"]

    assert REVISION[:12] in page
    assert TIMESTAMP in page
    assert "{{" not in page
    assert (output / "404.html").read_bytes() == (output / "index.html").read_bytes()
    assert (output / "favicon.svg").read_bytes() == (
        PROJECT_ROOT / "site/favicon.svg"
    ).read_bytes()
    assert artifact["bytes"] == len(textbook_content)
    assert artifact["sha256"] == hashlib.sha256(textbook_content).hexdigest()
    assert manifest["revision"] == REVISION
    assert manifest["package_version"] == project_version()


def test_course_site_builder_rejects_stale_or_incomplete_inputs(tmp_path: Path) -> None:
    textbook = tmp_path / "textbook.pdf"
    write_fake_pdf(textbook)
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "stale.txt").write_text("old artifact", encoding="utf-8")

    with pytest.raises(FileExistsError, match="must be empty"):
        build_course_site(output=occupied, textbook=textbook, revision=REVISION)
    with pytest.raises(ValueError, match="nonempty source revision"):
        build_course_site(
            output=tmp_path / "empty-revision",
            textbook=textbook,
            revision=" ",
        )
    with pytest.raises(FileNotFoundError, match="Compiled textbook"):
        build_course_site(
            output=tmp_path / "missing-pdf",
            textbook=tmp_path / "missing.pdf",
            revision=REVISION,
        )


def test_reviewed_site_source_has_accessible_static_structure() -> None:
    parser = PageStructureParser()
    parser.feed((PROJECT_ROOT / "site/index.html").read_text(encoding="utf-8"))

    assert parser.language == "en"
    assert "main-content" in parser.identifiers
    assert "#main-content" in parser.links
    assert "textbook/data-science-machine-learning-textbook.pdf" in parser.links
    assert any("STUDENT_START_HERE.md" in link for link in parser.links)
    assert "manifest.json" in parser.links
    assert parser.script_count == 0


def test_smoke_check_verifies_public_bytes_against_manifest(tmp_path: Path) -> None:
    textbook = tmp_path / "textbook.pdf"
    write_fake_pdf(textbook)
    output = tmp_path / "site"
    build_course_site(
        output=output,
        textbook=textbook,
        revision=REVISION,
        timestamp=TIMESTAMP,
    )
    root = "https://example.edu/course/"

    def fetch(url: str) -> bytes:
        relative_path = url.removeprefix(root) or "index.html"
        return (output / relative_path).read_bytes()

    manifest = verify_course_site(root, REVISION, fetch=fetch)
    assert manifest["generated_at"] == TIMESTAMP

    manifest_path = output / "manifest.json"
    changed = json.loads(manifest_path.read_text(encoding="utf-8"))
    changed["artifacts"]["textbook"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(RuntimeError, match="checksum does not match"):
        verify_course_site(root, REVISION, fetch=fetch)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("path", "textbook/../../private.txt", "invalid textbook path"),
        ("sha256", "not-a-digest", "invalid textbook checksum"),
        ("bytes", 0, "invalid textbook size"),
    ],
)
def test_smoke_check_rejects_malformed_manifest_fields(
    tmp_path: Path,
    field: str,
    value: str | int,
    message: str,
) -> None:
    textbook = tmp_path / "textbook.pdf"
    write_fake_pdf(textbook)
    output = tmp_path / "site"
    build_course_site(
        output=output,
        textbook=textbook,
        revision=REVISION,
        timestamp=TIMESTAMP,
    )
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"]["textbook"][field] = value
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    root = "https://example.edu/course/"

    def fetch(url: str) -> bytes:
        relative_path = url.removeprefix(root) or "index.html"
        return (output / relative_path).read_bytes()

    with pytest.raises(RuntimeError, match=message):
        verify_course_site(root, REVISION, fetch=fetch)


def test_release_bundle_contains_only_versioned_outputs(tmp_path: Path) -> None:
    textbook = tmp_path / "textbook.pdf"
    textbook_content = write_fake_pdf(textbook)
    dist = tmp_path / "dist"
    dist.mkdir()
    version = project_version()
    wheel = dist / f"rice_dsm-{version}-py3-none-any.whl"
    source = dist / f"rice_dsm-{version}.tar.gz"
    wheel.write_bytes(b"wheel fixture")
    source.write_bytes(b"source fixture")
    (dist / f"rice_dsm-{version}-py3-none-any 2.whl").write_bytes(b"stale wheel")
    (dist / f"rice_dsm-{version} 2.tar.gz").write_bytes(b"stale source")
    output = tmp_path / "release"

    build_release_bundle(
        output=output,
        dist=dist,
        textbook=textbook,
        tag=f"course-v{project_version()}",
        revision=REVISION,
        timestamp=TIMESTAMP,
    )

    expected_names = {
        "SHA256SUMS",
        "data-science-machine-learning-textbook.pdf",
        "release-manifest.json",
        source.name,
        wheel.name,
    }
    assert {path.name for path in output.iterdir()} == expected_names
    assert (output / "data-science-machine-learning-textbook.pdf").read_bytes() == (
        textbook_content
    )

    manifest = json.loads((output / "release-manifest.json").read_text("utf-8"))
    assert manifest["tag"] == f"course-v{project_version()}"
    assert manifest["revision"] == REVISION
    assert {item["name"] for item in manifest["artifacts"]} == {
        "data-science-machine-learning-textbook.pdf",
        source.name,
        wheel.name,
    }
    checksum_names = {
        line.split("  ", maxsplit=1)[1]
        for line in (output / "SHA256SUMS").read_text("utf-8").splitlines()
    }
    assert checksum_names == expected_names - {"SHA256SUMS"}


def test_release_bundle_rejects_version_drift_and_stale_output(tmp_path: Path) -> None:
    textbook = tmp_path / "textbook.pdf"
    write_fake_pdf(textbook)
    dist = tmp_path / "dist"
    dist.mkdir()
    version = project_version()
    (dist / f"rice_dsm-{version}-py3-none-any.whl").write_bytes(b"wheel")
    (dist / f"rice_dsm-{version}.tar.gz").write_bytes(b"source")

    with pytest.raises(ValueError, match="does not match package version"):
        build_release_bundle(
            output=tmp_path / "wrong-tag",
            dist=dist,
            textbook=textbook,
            tag="course-v999.0.0",
            revision=REVISION,
        )

    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "stale.txt").write_text("old artifact", encoding="utf-8")
    with pytest.raises(FileExistsError, match="must be empty"):
        build_release_bundle(
            output=occupied,
            dist=dist,
            textbook=textbook,
            tag=f"course-v{project_version()}",
            revision=REVISION,
        )

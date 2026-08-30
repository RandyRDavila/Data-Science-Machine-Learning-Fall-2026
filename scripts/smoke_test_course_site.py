"""Verify the public course site and its deployed PDF artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

Fetch = Callable[[str], bytes]


def fetch_url(url: str) -> bytes:
    """Fetch one public artifact with a bounded timeout and explicit identity."""

    request = Request(url, headers={"User-Agent": "rice-dsm-deployment-check/1"})
    with urlopen(request, timeout=20) as response:  # noqa: S310
        if response.status != 200:
            raise RuntimeError(
                f"Expected HTTP 200 from {url}; received {response.status}."
            )
        return response.read()


def verify_course_site(
    base_url: str,
    expected_revision: str,
    *,
    fetch: Fetch = fetch_url,
) -> dict[str, Any]:
    """Verify page identity, provenance, and deployed PDF checksums.

    Parameters
    ----------
    base_url
        Root URL of the deployed static site.
    expected_revision
        Complete Git commit SHA expected in the deployment manifest.
    fetch
        Injectable byte-fetching function used by unit tests.

    Returns
    -------
    dict[str, Any]
        The verified deployment manifest.

    Raises
    ------
    ValueError
        If the URL or expected revision is invalid.
    RuntimeError
        If any public artifact violates the deployment contract.
    """

    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("The site URL must be an absolute HTTP or HTTPS URL.")
    if not expected_revision.strip():
        raise ValueError("A nonempty expected revision is required.")

    root = base_url.rstrip("/") + "/"
    page = fetch(root).decode("utf-8")
    if "Data Science and Machine Learning" not in page:
        raise RuntimeError("The deployed landing page has an unexpected identity.")
    if expected_revision[:12] not in page:
        raise RuntimeError("The landing page does not identify the expected revision.")

    course_map = fetch(urljoin(root, "course-map.html")).decode("utf-8")
    for marker in (
        'id="part-i"',
        'id="part-ii"',
        'id="part-iii"',
        'id="appendices"',
        "lecture-01-python-foundations",
        "lecture-17-reliable-supervised-systems",
        "#page=114",
        "#page=144",
    ):
        if marker not in course_map:
            raise RuntimeError("The deployed course map is incomplete.")

    manifest_url = urljoin(root, "manifest.json")
    manifest = json.loads(fetch(manifest_url))
    if not isinstance(manifest, dict):
        raise RuntimeError("The deployment manifest must be a JSON object.")
    if manifest.get("revision") != expected_revision:
        raise RuntimeError("The deployment manifest identifies a different revision.")

    artifacts = manifest.get("artifacts", {})
    for artifact_name, path_prefix, label in (
        ("textbook", "textbook/", "textbook"),
        ("cv", "instructor/", "CV"),
    ):
        artifact = artifacts.get(artifact_name, {})
        artifact_path = artifact.get("path")
        expected_digest = artifact.get("sha256")
        expected_bytes = artifact.get("bytes")
        if (
            not isinstance(artifact_path, str)
            or not artifact_path.startswith(path_prefix)
            or ".." in artifact_path.split("/")
        ):
            raise RuntimeError(
                f"The deployment manifest has an invalid {label} path."
            )
        if not isinstance(expected_digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_digest
        ):
            raise RuntimeError(
                f"The deployment manifest has an invalid {label} checksum."
            )
        if (
            not isinstance(expected_bytes, int)
            or isinstance(expected_bytes, bool)
            or expected_bytes < 1
        ):
            raise RuntimeError(
                f"The deployment manifest has an invalid {label} size."
            )

        content = fetch(urljoin(root, artifact_path))
        if not content.startswith(b"%PDF-"):
            raise RuntimeError(f"The deployed {label} is not a PDF document.")
        if len(content) != expected_bytes:
            raise RuntimeError(
                f"The deployed {label} size does not match the manifest."
            )
        actual_digest = hashlib.sha256(content).hexdigest()
        if actual_digest != expected_digest:
            raise RuntimeError(
                f"The deployed {label} checksum does not match the manifest."
            )
    return manifest


def verify_with_retries(
    base_url: str,
    expected_revision: str,
    *,
    attempts: int = 6,
    delay_seconds: float = 5.0,
) -> dict[str, Any]:
    """Retry verification while a newly deployed edge cache converges."""

    if attempts < 1:
        raise ValueError("At least one verification attempt is required.")
    for attempt in range(1, attempts + 1):
        try:
            return verify_course_site(base_url, expected_revision)
        except (HTTPError, URLError, json.JSONDecodeError, RuntimeError) as error:
            if attempt == attempts:
                raise RuntimeError(
                    f"Course-site verification failed after {attempts} attempts."
                ) from error
            print(f"Attempt {attempt}/{attempts} failed: {error}")
            time.sleep(delay_seconds)
    raise AssertionError("Unreachable retry state")


def parse_args() -> argparse.Namespace:
    """Parse the command-line contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--delay-seconds", type=float, default=5.0)
    return parser.parse_args()


def main() -> None:
    """Verify a deployed site and print its provenance."""

    arguments = parse_args()
    manifest = verify_with_retries(
        arguments.url,
        arguments.revision,
        attempts=arguments.attempts,
        delay_seconds=arguments.delay_seconds,
    )
    print(
        "Verified course site: "
        f"revision={manifest['revision']} generated_at={manifest['generated_at']}"
    )


if __name__ == "__main__":
    main()

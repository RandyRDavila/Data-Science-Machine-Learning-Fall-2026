"""Shared contracts for the reproducible local course runtime.

This module intentionally uses only the Python standard library.  The refresh
and doctor commands run outside the project virtual environment so they can
inspect, replace, and repair ``.venv`` safely.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

KERNEL_NAME = "rice-dsm"
RUNTIME_STAMP = ".rice-dsm-runtime.json"
CORE_IMPORTS = ("numpy", "pandas", "matplotlib", "seaborn", "sklearn")


def project_environment(project_root: Path) -> Path:
    """Return the repository-owned virtual environment directory."""

    return project_root / ".venv"


def project_python(project_root: Path) -> Path:
    """Return the platform-specific Python executable inside ``.venv``."""

    environment = project_environment(project_root)
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def python_request(project_root: Path) -> str:
    """Read the exact managed-Python version committed for the course."""

    request = (project_root / ".python-version").read_text(encoding="utf-8").strip()
    is_exact = request.count(".") == 2 and all(
        part.isdigit() for part in request.split(".")
    )
    if not is_exact:
        raise RuntimeError(
            ".python-version must contain an exact three-component version, "
            f"not {request!r}."
        )
    return request


def uv_version(uv_executable: str) -> str:
    """Return the uv version string used to prepare the environment."""

    completed = subprocess.run(
        [uv_executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return completed.stdout.strip()


def runtime_contract(project_root: Path, uv_executable: str) -> dict[str, str]:
    """Describe every versioned input that makes an environment reusable."""

    lock_bytes = (project_root / "uv.lock").read_bytes()
    contract = {
        "schema": "1",
        "python": python_request(project_root),
        "lock_sha256": hashlib.sha256(lock_bytes).hexdigest(),
        "platform": platform.system().lower(),
        "machine": platform.machine().lower(),
        "uv": uv_version(uv_executable),
    }
    serialized = json.dumps(contract, sort_keys=True).encode()
    contract["fingerprint"] = hashlib.sha256(serialized).hexdigest()
    return contract


def read_runtime_stamp(
    project_root: Path, environment: Path | None = None
) -> dict[str, str] | None:
    """Read the last successfully verified environment contract, if present."""

    stamp = (environment or project_environment(project_root)) / RUNTIME_STAMP
    if not stamp.is_file():
        return None
    try:
        value = json.loads(stamp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def write_runtime_stamp(
    project_root: Path,
    contract: dict[str, str],
    environment: Path | None = None,
) -> Path:
    """Record a contract only after setup and protocol checks succeed."""

    stamp = (environment or project_environment(project_root)) / RUNTIME_STAMP
    stamp.write_text(f"{json.dumps(contract, indent=2, sort_keys=True)}\n")
    return stamp


def runtime_matches(
    project_root: Path,
    contract: dict[str, str],
    environment: Path | None = None,
) -> bool:
    """Return whether the verified environment matches the desired contract."""

    stamp = read_runtime_stamp(project_root, environment)
    return bool(stamp and stamp.get("fingerprint") == contract["fingerprint"])


def _posix_processes() -> list[dict[str, Any]]:
    completed = subprocess.run(
        ["ps", "-axo", "pid=,etime=,command="],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    processes: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        parts = line.strip().split(maxsplit=2)
        if len(parts) == 3 and parts[0].isdigit():
            processes.append(
                {"pid": int(parts[0]), "age": parts[1], "command": parts[2]}
            )
    return processes


def _windows_processes() -> list[dict[str, Any]]:
    command = (
        "Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
    )
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if not completed.stdout.strip():
        return []
    decoded = json.loads(completed.stdout)
    rows = decoded if isinstance(decoded, list) else [decoded]
    return [
        {
            "pid": int(row["ProcessId"]),
            "age": str(row.get("CreationDate") or "unknown"),
            "command": str(row.get("CommandLine") or ""),
        }
        for row in rows
    ]


def active_course_kernels(project_root: Path) -> list[dict[str, Any]]:
    """Find live Jupyter kernels whose interpreter belongs to this checkout."""

    try:
        processes = _windows_processes() if os.name == "nt" else _posix_processes()
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "Could not inspect running processes safely. Close VS Code completely "
            "and retry the refresh."
        ) from error

    environment_text = str(project_environment(project_root)).casefold()
    matches = []
    for process in processes:
        command = process["command"].casefold()
        if "ipykernel_launcher" in command and environment_text in command:
            matches.append(process)
    return matches


def require_no_active_course_kernels(project_root: Path) -> None:
    """Refuse to mutate an environment still owned by VS Code or Jupyter."""

    kernels = active_course_kernels(project_root)
    if not kernels:
        return
    details = "\n".join(
        f"  - PID {item['pid']} (age {item['age']}): {item['command']}"
        for item in kernels
    )
    raise RuntimeError(
        "Rice DSM kernels are still running. Restarting or synchronizing .venv "
        "under a live kernel can corrupt the lecture runtime. Close every course "
        f"notebook and fully quit VS Code, then retry.\n{details}"
    )


def remove_project_environment(project_root: Path) -> None:
    """Remove the disposable project environment without touching course work."""

    environment = project_environment(project_root)
    if not environment.exists():
        return

    def make_writable(function: Any, path: str, _: Any) -> None:
        target = Path(path)
        target.chmod(target.stat().st_mode | stat.S_IWUSR)
        function(path)

    shutil.rmtree(environment, onexc=make_writable)


def warm_scientific_imports(timeout: int = 180) -> list[tuple[str, float]]:
    """Import the core stack once and surface pathological cold-start delays."""

    module_names = repr(CORE_IMPORTS)
    code = f"""
import importlib
import json
import time

results = []
for name in {module_names}:
    started = time.perf_counter()
    importlib.import_module(name)
    results.append([name, time.perf_counter() - started])
print("RICE_DSM_IMPORT_TIMES=" + json.dumps(results), flush=True)
"""
    try:
        completed = subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"Core scientific imports did not finish within {timeout} seconds. "
            "Close VS Code and run the documented refresh command with --repair."
        ) from error

    marker = "RICE_DSM_IMPORT_TIMES="
    line = next(
        (item for item in completed.stdout.splitlines() if item.startswith(marker)),
        None,
    )
    if line is None:
        raise RuntimeError("The scientific import warm-up returned no timing record.")
    timings = json.loads(line.removeprefix(marker))
    return [(str(name), float(seconds)) for name, seconds in timings]


def verify_course_kernel_launch(
    project_root: Path,
    *,
    timeout: int = 45,
    expected_environment: Path | None = None,
) -> dict[str, str]:
    """Launch the named kernel, complete its handshake, and verify its identity."""

    from jupyter_client import KernelManager

    manager = KernelManager(kernel_name=KERNEL_NAME)
    client = None
    started = time.monotonic()
    try:
        manager.start_kernel(cwd=str(project_root))
        client = manager.client()
        client.start_channels()
        client.wait_for_ready(timeout=timeout)
        probe = (
            "import json, sys, rice_dsm; "
            "print('RICE_DSM_KERNEL_PROBE=' + json.dumps({"
            "'executable': sys.executable, 'package': rice_dsm.__file__}), flush=True)"
        )
        message_id = client.execute(probe)
        deadline = time.monotonic() + timeout
        payload: dict[str, str] | None = None
        while time.monotonic() < deadline:
            message = client.get_iopub_msg(timeout=max(1, deadline - time.monotonic()))
            if message.get("parent_header", {}).get("msg_id") != message_id:
                continue
            if message["msg_type"] == "error":
                traceback = "\n".join(message["content"]["traceback"])
                raise RuntimeError("Kernel probe failed: " + traceback)
            if message["msg_type"] == "stream":
                for line in message["content"]["text"].splitlines():
                    if line.startswith("RICE_DSM_KERNEL_PROBE="):
                        payload = json.loads(line.split("=", maxsplit=1)[1])
            is_idle = (
                message["msg_type"] == "status"
                and message["content"]["execution_state"] == "idle"
            )
            if is_idle:
                break
        if payload is None:
            raise RuntimeError("The Rice DSM kernel returned no identity probe.")

        environment = (
            expected_environment or project_environment(project_root)
        ).absolute()
        # Do not resolve the venv interpreter symlink: uv-managed environments
        # intentionally point at a shared base binary while retaining sys.prefix.
        executable = Path(payload["executable"]).absolute()
        package = Path(payload["package"]).resolve()
        if not executable.is_relative_to(environment):
            raise RuntimeError(f"Kernel used {executable}, outside {environment}.")
        if not package.is_relative_to((project_root / "src").resolve()):
            raise RuntimeError(
                f"Kernel imported rice_dsm from the wrong tree: {package}."
            )
        payload["startup_seconds"] = f"{time.monotonic() - started:.2f}"
        return payload
    except Exception as error:
        raise RuntimeError(
            "Rice DSM could not complete a real Jupyter readiness and execution "
            "probe. Close VS Code and run the refresh command with --repair."
        ) from error
    finally:
        if client is not None:
            client.stop_channels()
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)

"""Behavioral contracts for the versioned, disposable course runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import course_runtime


def make_project(tmp_path: Path) -> Path:
    """Create the minimum versioned inputs needed for a runtime contract."""

    project = tmp_path / "course"
    project.mkdir()
    (project / ".python-version").write_text("3.12.13\n")
    (project / "uv.lock").write_text("version = 1\n")
    return project


def test_python_request_requires_an_exact_patch_version(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    (project / ".python-version").write_text("3.12\n")

    with pytest.raises(RuntimeError, match="exact three-component version"):
        course_runtime.python_request(project)


def test_runtime_stamp_matches_only_the_verified_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = make_project(tmp_path)
    (project / ".venv").mkdir()
    monkeypatch.setattr(course_runtime, "uv_version", lambda _: "uv 0.12.6")
    contract = course_runtime.runtime_contract(project, "uv")

    course_runtime.write_runtime_stamp(project, contract)

    assert course_runtime.runtime_matches(project, contract)
    (project / "uv.lock").write_text("version = 2\n")
    changed = course_runtime.runtime_contract(project, "uv")
    assert not course_runtime.runtime_matches(project, changed)


def test_active_kernel_guard_identifies_only_this_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = make_project(tmp_path)
    own = str(project / ".venv" / "bin" / "python")
    monkeypatch.setattr(
        course_runtime,
        "_posix_processes",
        lambda: [
            {
                "pid": 41,
                "age": "01:12",
                "command": f"{own} -m ipykernel_launcher -f kernel.json",
            },
            {
                "pid": 42,
                "age": "00:03",
                "command": "/another/.venv/bin/python -m ipykernel_launcher",
            },
        ],
    )

    kernels = course_runtime.active_course_kernels(project)

    assert [item["pid"] for item in kernels] == [41]
    with pytest.raises(RuntimeError, match="PID 41"):
        course_runtime.require_no_active_course_kernels(project)


class FakeClient:
    """Minimal Jupyter client used to verify cleanup and identity failures."""

    def __init__(
        self,
        payload: dict[str, str] | None,
        ready_error: Exception | None = None,
    ):
        self.payload = payload
        self.ready_error = ready_error
        self.stopped = False
        self.messages: list[dict[str, object]] = []

    def start_channels(self) -> None:
        return None

    def wait_for_ready(self, timeout: int) -> None:
        if self.ready_error:
            raise self.ready_error

    def execute(self, _: str) -> str:
        if self.payload is not None:
            self.messages = [
                {
                    "parent_header": {"msg_id": "probe"},
                    "msg_type": "stream",
                    "content": {
                        "text": "RICE_DSM_KERNEL_PROBE=" + json.dumps(self.payload)
                    },
                },
                {
                    "parent_header": {"msg_id": "probe"},
                    "msg_type": "status",
                    "content": {"execution_state": "idle"},
                },
            ]
        return "probe"

    def get_iopub_msg(self, timeout: float) -> dict[str, object]:
        return self.messages.pop(0)

    def stop_channels(self) -> None:
        self.stopped = True


class FakeManager:
    def __init__(self, client: FakeClient):
        self._client = client
        self.has_kernel = False
        self.shutdown = False

    def start_kernel(self, cwd: str) -> None:
        self.has_kernel = True

    def client(self) -> FakeClient:
        return self._client

    def shutdown_kernel(self, now: bool) -> None:
        self.shutdown = True
        self.has_kernel = False


def install_fake_manager(
    monkeypatch: pytest.MonkeyPatch, manager: FakeManager
) -> None:
    import jupyter_client

    monkeypatch.setattr(jupyter_client, "KernelManager", lambda kernel_name: manager)


def test_kernel_probe_rejects_wrong_interpreter_and_always_shuts_down(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = make_project(tmp_path)
    (project / "src" / "rice_dsm").mkdir(parents=True)
    client = FakeClient(
        {
            "executable": "/wrong/python",
            "package": str(project / "src" / "rice_dsm" / "__init__.py"),
        }
    )
    manager = FakeManager(client)
    install_fake_manager(monkeypatch, manager)

    with pytest.raises(RuntimeError, match="readiness and execution probe"):
        course_runtime.verify_course_kernel_launch(project)

    assert client.stopped
    assert manager.shutdown


def test_kernel_probe_timeout_always_shuts_down(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = make_project(tmp_path)
    client = FakeClient(None, TimeoutError("not ready"))
    manager = FakeManager(client)
    install_fake_manager(monkeypatch, manager)

    with pytest.raises(RuntimeError, match="readiness and execution probe"):
        course_runtime.verify_course_kernel_launch(project)

    assert client.stopped
    assert manager.shutdown

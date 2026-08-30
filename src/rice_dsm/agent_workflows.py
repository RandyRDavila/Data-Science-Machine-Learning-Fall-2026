"""Safe, deterministic boundaries for teaching LLM-assisted workflows."""

from __future__ import annotations

import ast
import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ToolRisk = Literal["read", "propose", "write", "execute"]
AnnotatedDigest = str


class DocstringProposal(BaseModel):
    """Structured model output for a NumPy-style docstring proposal."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    function_name: str
    source_sha256: AnnotatedDigest
    docstring: str = Field(min_length=20, max_length=8_000)
    rationale: str = Field(min_length=10, max_length=1_000)

    @field_validator("docstring")
    @classmethod
    def require_summary(cls, value: str) -> str:
        """Require a nonempty summary before any section heading."""

        if not value.splitlines()[0].strip():
            raise ValueError("docstring must begin with a summary")
        return value


class TrainingRunProposal(BaseModel):
    """Structured proposal for one bounded, reproducible training run."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    request_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{7,79}$")
    dataset_uri: str = Field(min_length=1, max_length=500)
    dataset_version: str = Field(min_length=1, max_length=100)
    feature_version: str = Field(min_length=1, max_length=100)
    code_revision: str = Field(pattern=r"^[0-9a-f]{7,40}$")
    model_family: Literal["linear", "tree", "neural-network"]
    requested_start_at: datetime
    maximum_runtime_minutes: int = Field(ge=1, le=24 * 60)
    accelerator: Literal["cpu", "gpu"]
    rationale: str = Field(min_length=10, max_length=1_000)

    @field_validator("requested_start_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Reject ambiguous schedules without a timezone offset."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("requested_start_at must include a timezone offset")
        return value


@dataclass(frozen=True, slots=True)
class TrainingPolicy:
    """Deterministic authorization limits applied after model output."""

    allowed_dataset_prefixes: tuple[str, ...]
    allowed_model_families: tuple[str, ...]
    maximum_runtime_minutes: int
    gpu_allowed: bool = False

    def violations(self, proposal: TrainingRunProposal) -> tuple[str, ...]:
        """Return every policy violation without taking an action."""

        problems: list[str] = []
        if not proposal.dataset_uri.startswith(self.allowed_dataset_prefixes):
            problems.append("dataset URI is outside the approved namespace")
        if proposal.model_family not in self.allowed_model_families:
            problems.append("model family is not approved")
        if proposal.maximum_runtime_minutes > self.maximum_runtime_minutes:
            problems.append("runtime exceeds the approved maximum")
        if proposal.accelerator == "gpu" and not self.gpu_allowed:
            problems.append("GPU execution is not approved")
        return tuple(problems)


@dataclass(frozen=True, slots=True)
class ApprovedTrainingRun:
    """Human-approved proposal ready for a scheduler adapter."""

    proposal: TrainingRunProposal
    approved_by: str
    approved_at: datetime


def approve_training_run(
    proposal: TrainingRunProposal,
    *,
    policy: TrainingPolicy,
    approved_by: str,
    approved_at: datetime,
) -> ApprovedTrainingRun:
    """Apply deterministic policy and record accountable approval.

    Parameters
    ----------
    proposal : TrainingRunProposal
        Validated but untrusted model/user proposal.
    policy : TrainingPolicy
        Code-owned authorization boundary.
    approved_by : str
        Nonempty identity of the accountable reviewer.
    approved_at : datetime
        Timezone-aware approval time.

    Returns
    -------
    ApprovedTrainingRun
        Immutable authorization record.

    Raises
    ------
    PermissionError
        If the proposal violates policy.
    ValueError
        If approval metadata is incomplete or ambiguous.
    """

    violations = policy.violations(proposal)
    if violations:
        raise PermissionError("; ".join(violations))
    if not approved_by.strip():
        raise ValueError("approved_by must be nonblank")
    if approved_at.tzinfo is None or approved_at.utcoffset() is None:
        raise ValueError("approved_at must include a timezone offset")
    if proposal.requested_start_at < approved_at:
        raise ValueError("requested start cannot precede approval")
    return ApprovedTrainingRun(proposal, approved_by.strip(), approved_at)


class InMemoryTrainingScheduler:
    """Deterministic scheduler adapter that records but never runs jobs."""

    def __init__(self) -> None:
        self._jobs: dict[str, ApprovedTrainingRun] = {}

    def schedule(self, run: ApprovedTrainingRun) -> bool:
        """Record an approved run once and return whether it was new."""

        request_id = run.proposal.request_id
        if request_id in self._jobs:
            return False
        self._jobs[request_id] = run
        return True

    @property
    def jobs(self) -> tuple[ApprovedTrainingRun, ...]:
        """Return an immutable snapshot in insertion order."""

        return tuple(self._jobs.values())


@dataclass(frozen=True, slots=True)
class FunctionAudit:
    """Static information used to decide whether documentation needs help."""

    name: str
    line: int
    parameters: tuple[str, ...]
    has_docstring: bool


def audit_python_docstrings(source: str) -> tuple[FunctionAudit, ...]:
    """Inspect function signatures and docstring presence without execution."""

    tree = ast.parse(source)
    audits = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            positional = (*node.args.posonlyargs, *node.args.args)
            parameter_names = tuple(argument.arg for argument in positional)
            audits.append(
                FunctionAudit(
                    name=node.name,
                    line=node.lineno,
                    parameters=parameter_names,
                    has_docstring=ast.get_docstring(node) is not None,
                )
            )
    return tuple(sorted(audits, key=lambda audit: audit.line))


def source_digest(source: str) -> str:
    """Return a SHA-256 identifier for the exact reviewed source text."""

    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def validate_docstring_proposal(
    proposal: DocstringProposal,
    *,
    source: str,
) -> tuple[str, ...]:
    """Return deterministic review findings for one generated proposal."""

    findings: list[str] = []
    if proposal.source_sha256 != source_digest(source):
        findings.append("proposal source digest does not match current source")

    audits = {audit.name: audit for audit in audit_python_docstrings(source)}
    audit = audits.get(proposal.function_name)
    if audit is None:
        findings.append("function does not exist in current source")
        return tuple(findings)

    if audit.parameters and "Parameters\n----------" not in proposal.docstring:
        findings.append("NumPy-style Parameters section is missing")
    if "Returns\n-------" not in proposal.docstring:
        findings.append("NumPy-style Returns section is missing")
    return tuple(findings)


class ToolArguments(BaseModel):
    """Base class for strict tool arguments."""

    model_config = ConfigDict(extra="forbid")


class AuditDocstringsArguments(ToolArguments):
    """Arguments for the read-only docstring audit tool."""

    source: str = Field(max_length=50_000)


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """One allowlisted callable with typed input and declared risk."""

    name: str
    description: str
    risk: ToolRisk
    arguments_model: type[ToolArguments]
    function: Callable[[ToolArguments], object]


class ToolRegistry:
    """Validate and dispatch only explicitly registered tools."""

    def __init__(self, definitions: tuple[ToolDefinition, ...]) -> None:
        self._definitions = {definition.name: definition for definition in definitions}
        if len(self._definitions) != len(definitions):
            raise ValueError("tool names must be unique")

    def execute(
        self,
        name: str,
        raw_arguments: Mapping[str, object],
        *,
        allowed_risks: frozenset[ToolRisk],
    ) -> object:
        """Validate policy and arguments before calling one tool."""

        definition = self._definitions.get(name)
        if definition is None:
            raise KeyError(f"unknown tool: {name}")
        if definition.risk not in allowed_risks:
            raise PermissionError(f"tool risk {definition.risk!r} is not allowed")
        arguments = definition.arguments_model.model_validate(raw_arguments)
        return definition.function(arguments)


def _audit_tool(arguments: ToolArguments) -> tuple[FunctionAudit, ...]:
    """Adapt strict tool arguments to the static audit function."""

    if not isinstance(arguments, AuditDocstringsArguments):  # pragma: no cover
        raise TypeError("expected AuditDocstringsArguments")
    return audit_python_docstrings(arguments.source)


def teaching_tool_registry() -> ToolRegistry:
    """Build the notebook's least-privilege, read-only tool registry."""

    return ToolRegistry(
        (
            ToolDefinition(
                name="audit_python_docstrings",
                description="Statically list Python functions and docstring presence.",
                risk="read",
                arguments_model=AuditDocstringsArguments,
                function=_audit_tool,
            ),
        )
    )

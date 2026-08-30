"""Tests for deterministic boundaries around LLM-assisted workflows."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from rice_dsm.agent_workflows import (
    DocstringProposal,
    InMemoryTrainingScheduler,
    TrainingPolicy,
    TrainingRunProposal,
    approve_training_run,
    audit_python_docstrings,
    source_digest,
    teaching_tool_registry,
    validate_docstring_proposal,
)

EXAMPLE_SOURCE = """\
def kinetic_energy(mass: float, velocity: float) -> float:
    return 0.5 * mass * velocity**2
"""


def valid_training_proposal() -> TrainingRunProposal:
    """Return one bounded reproducible training proposal."""

    return TrainingRunProposal(
        request_id="training-proposal-0001",
        dataset_uri="s3://approved-science/snapshots/2026-08-29/",
        dataset_version="sha256:dataset-001",
        feature_version="temperature-features-v3",
        code_revision="a1b2c3d4e5f6",
        model_family="linear",
        requested_start_at=datetime(2026, 8, 30, 3, tzinfo=UTC),
        maximum_runtime_minutes=60,
        accelerator="cpu",
        rationale="Evaluate the reviewed feature change on a fixed snapshot.",
    )


def approved_policy() -> TrainingPolicy:
    """Return a restrictive teaching policy."""

    return TrainingPolicy(
        allowed_dataset_prefixes=("s3://approved-science/snapshots/",),
        allowed_model_families=("linear", "tree"),
        maximum_runtime_minutes=120,
        gpu_allowed=False,
    )


def test_docstring_audit_parses_source_without_executing_it() -> None:
    audits = audit_python_docstrings(EXAMPLE_SOURCE)

    assert len(audits) == 1
    assert audits[0].name == "kinetic_energy"
    assert audits[0].parameters == ("mass", "velocity")
    assert audits[0].has_docstring is False


def test_docstring_proposal_is_bound_to_exact_source_and_style() -> None:
    proposal = DocstringProposal(
        function_name="kinetic_energy",
        source_sha256=source_digest(EXAMPLE_SOURCE),
        docstring="""Compute kinetic energy.

Parameters
----------
mass : float
    Mass in kilograms.
velocity : float
    Velocity in meters per second.

Returns
-------
float
    Energy in joules.
""",
        rationale="Documents units, inputs, output, and scientific meaning.",
    )

    assert validate_docstring_proposal(proposal, source=EXAMPLE_SOURCE) == ()
    assert validate_docstring_proposal(proposal, source=EXAMPLE_SOURCE + "\n") == (
        "proposal source digest does not match current source",
    )


def test_docstring_validator_reports_missing_numpy_sections() -> None:
    proposal = DocstringProposal(
        function_name="kinetic_energy",
        source_sha256=source_digest(EXAMPLE_SOURCE),
        docstring="Compute kinetic energy from mass and velocity.",
        rationale="A deliberately incomplete proposal for a negative test.",
    )

    assert validate_docstring_proposal(proposal, source=EXAMPLE_SOURCE) == (
        "NumPy-style Parameters section is missing",
        "NumPy-style Returns section is missing",
    )


def test_training_proposal_requires_timezone_and_rejects_extra_fields() -> None:
    payload = valid_training_proposal().model_dump()
    payload["requested_start_at"] = datetime(2026, 8, 30, 3)
    payload["unreviewed_action"] = "deploy"

    with pytest.raises(ValidationError) as error:
        TrainingRunProposal.model_validate(payload)

    locations = {tuple(item["loc"]) for item in error.value.errors()}
    assert ("requested_start_at",) in locations
    assert ("unreviewed_action",) in locations


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"dataset_uri": "s3://unapproved/data/"}, "dataset URI"),
        ({"model_family": "neural-network"}, "model family"),
        ({"maximum_runtime_minutes": 121}, "runtime"),
        ({"accelerator": "gpu"}, "GPU"),
    ],
)
def test_policy_rejects_model_proposals_outside_authority(
    change: dict[str, object], message: str
) -> None:
    proposal = TrainingRunProposal.model_validate(
        valid_training_proposal().model_dump() | change
    )

    with pytest.raises(PermissionError, match=message):
        approve_training_run(
            proposal,
            policy=approved_policy(),
            approved_by="course-reviewer",
            approved_at=datetime(2026, 8, 29, 18, tzinfo=UTC),
        )


def test_approval_and_scheduling_are_explicit_and_idempotent() -> None:
    proposal = valid_training_proposal()
    approved_at = proposal.requested_start_at - timedelta(hours=1)
    approved = approve_training_run(
        proposal,
        policy=approved_policy(),
        approved_by="course-reviewer",
        approved_at=approved_at,
    )
    scheduler = InMemoryTrainingScheduler()

    assert scheduler.schedule(approved) is True
    assert scheduler.schedule(approved) is False
    assert scheduler.jobs == (approved,)


def test_tool_registry_is_allowlisted_typed_and_risk_gated() -> None:
    registry = teaching_tool_registry()

    result = registry.execute(
        "audit_python_docstrings",
        {"source": EXAMPLE_SOURCE},
        allowed_risks=frozenset({"read"}),
    )
    assert result[0].name == "kinetic_energy"

    with pytest.raises(KeyError, match="unknown tool"):
        registry.execute(
            "run_arbitrary_shell",
            {},
            allowed_risks=frozenset({"read", "execute"}),
        )

    with pytest.raises(PermissionError, match="not allowed"):
        registry.execute(
            "audit_python_docstrings",
            {"source": EXAMPLE_SOURCE},
            allowed_risks=frozenset(),
        )

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        registry.execute(
            "audit_python_docstrings",
            {"source": EXAMPLE_SOURCE, "command": "delete everything"},
            allowed_risks=frozenset({"read"}),
        )

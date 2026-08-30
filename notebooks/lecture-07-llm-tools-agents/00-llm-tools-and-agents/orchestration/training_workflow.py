"""Offline teaching example for an approved, idempotent training schedule."""

from datetime import datetime

from rice_dsm.agent_workflows import (
    InMemoryTrainingScheduler,
    TrainingPolicy,
    TrainingRunProposal,
    approve_training_run,
)


def main() -> None:
    """Validate, authorize, approve, and record one harmless proposal."""

    proposal = TrainingRunProposal.model_validate(
        {
            "request_id": "training-proposal-20260901",
            "dataset_uri": "s3://rice-dsm-approved/measurements",
            "dataset_version": "sha256:teaching-snapshot",
            "feature_version": "features-v1",
            "code_revision": "a1b2c3d",
            "model_family": "linear",
            "requested_start_at": "2026-09-01T22:00:00-05:00",
            "maximum_runtime_minutes": 30,
            "accelerator": "cpu",
            "rationale": "Run the reviewed baseline after the weekly data snapshot.",
        }
    )
    policy = TrainingPolicy(
        allowed_dataset_prefixes=("s3://rice-dsm-approved/",),
        allowed_model_families=("linear", "tree"),
        maximum_runtime_minutes=120,
        gpu_allowed=False,
    )
    approved = approve_training_run(
        proposal,
        policy=policy,
        approved_by="course-instructor",
        approved_at=datetime.fromisoformat("2026-09-01T16:00:00-05:00"),
    )
    scheduler = InMemoryTrainingScheduler()

    assert scheduler.schedule(approved) is True
    assert scheduler.schedule(approved) is False
    print(f"Recorded {len(scheduler.jobs)} approved job; no training was executed.")


if __name__ == "__main__":
    main()

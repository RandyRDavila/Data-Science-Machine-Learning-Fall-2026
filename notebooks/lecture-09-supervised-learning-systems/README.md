# Lecture 9: Machine Learning and Supervised Learning Systems

This unit begins Part II by locating supervised learning within the broader
machine-learning landscape and then constructing a complete first prediction
system. Real clinical, chemical, and image datasets distinguish supervised and
unsupervised tasks; a clearly labeled simulation isolates the interactive
mechanism of reinforcement learning. Linear regression then develops from
residual geometry, least-squares calculus, and the normal equations into a
held-out diabetes progression study with an explicit target, prediction time,
population, split, preprocessing, baseline, metrics, diagnostics, and artifact
boundary.

The real observations live in the versioned, read-only
[`data/course_datasets.sqlite`](../../data/course_datasets.sqlite) database.
Students inspect its catalog and query the required columns with SQL. The
separate ingestion script is reproducible and tested; notebooks do not hide
data acquisition behind library dataset loaders.

## Current student route

Read the shared [`Part II student guide`](../PART_II_STUDENT_GUIDE.md), then
complete the released notebooks in order:

1. `00-machine-learning-landscape.ipynb`
2. `01-supervised-learning-linear-regression.ipynb`

Notebook 02 remains planned and is not assigned until its file is published
and named in the weekly announcement.

## Planned notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | ML branches and problem formulation | Problem-first learning-signal map |
| 01 | OLS mathematics and a complete regression pipeline | Derived model, leakage-safe pipeline, and evaluation dossier |
| 02 | Group- and time-aware vertical slice *(planned)* | Versioned baseline artifact and batch prediction |

Students will distinguish prediction from causal explanation, identify target
and feature leakage, reserve data for honest evaluation, fit preprocessing only
inside the training boundary, compare with a baseline, interpret complementary
metrics, and diagnose residual behavior.

This unit may span part of one meeting or several meetings. The notebooks are
laboratories; durable schemas and evaluation utilities belong in `rice_dsm`.

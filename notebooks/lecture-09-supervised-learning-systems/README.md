# Lecture 9: Supervised Learning Systems

This unit begins Part II by defining supervised learning as an estimation and
system-design problem. A battery-cell case makes the observation, target,
prediction time, horizon, population, loss, split, and baseline explicit before
any model is trained.

## Current student route

Read the shared [`Part II student guide`](../PART_II_STUDENT_GUIDE.md), then
complete the released `00-supervised-learning-contract.ipynb`. Notebooks 01 and
02 below are planned and are not assigned until their files are published and
named in the weekly announcement.

## Planned notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | The supervised-learning contract | Machine-readable prediction contract |
| 01 | Splits, baselines, and leakage | Group- and time-aware evaluation fixture |
| 02 | A deliberately simple vertical slice | Versioned baseline artifact and batch prediction |

Students will distinguish prediction from causal explanation, identify target
and feature leakage, select a split that matches deployment, and trace a dummy
model through training, promotion, prediction, and outcome collection.

This unit may span part of one meeting or several meetings. The notebooks are
laboratories; durable schemas and evaluation utilities belong in `rice_dsm`.

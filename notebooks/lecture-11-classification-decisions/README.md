# Lecture 11: Classification and Decisions

This unit moves from the affine score of linear regression to logistic
probability estimation, then to maximum-margin classification, and finally to
an explicit decision rule. The opening
laboratory derives a single logistic neuron from a Bernoulli likelihood,
verifies its gradient, and compares a transparent optimizer with a professional
scikit-learn pipeline. Notebook 01 keeps the affine score but replaces the
probabilistic objective with regularized hinge loss, making the distinction
between shared representation and different estimator semantics explicit. The
unit then begins professional performance measurement with
baselines, confusion matrices, conditional rates, prevalence, threshold sweeps,
uncertainty, and population scope. A later laboratory will deepen threshold,
calibration, subgroup, and monitoring workflows as separate parts of the
classification contract.

## Current student route

Read the shared [`Part II student guide`](../PART_II_STUDENT_GUIDE.md), then
complete Lecture 10 Notebook 00 before the released notebooks 00 and 01 in
order. Each core route ends after held-out evidence; implementation and
regularization investigations are extensions.

The released notebooks are
[`00-logistic-model-and-decision-policy.ipynb`](00-logistic-model-and-decision-policy.ipynb)
and
[`01-linear-svm-margin-and-hinge-loss.ipynb`](01-linear-svm-margin-and-hinge-loss.ipynb).
Notebooks 02 and 03 are planned and remain unavailable until their contracts,
data route, and tests are complete.

## Planned notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | Bernoulli likelihood, the single-neuron gradient, and performance foundations | Verified probability model, optimization trace, and scoped evidence report |
| 01 | Linear SVM geometry, hinge loss, support vectors, and maximum margins | Verified margin classifier and scoped evidence report |
| 02 | Decision metrics, costs, thresholds, calibration, and subgroup audits | Versioned decision policy |
| 03 | Multiclass and classification contracts | Classification model card |

Notebooks 00 and 01 use the repository's read-only Wisconsin Diagnostic Breast
Cancer table. Students recode labels explicitly, preserve a sealed test
partition, and treat the results only as instructional models of image-derived
measurements—not clinical devices or diagnostic claims.

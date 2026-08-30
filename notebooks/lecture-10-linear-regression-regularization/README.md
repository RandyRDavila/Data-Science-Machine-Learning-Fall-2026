# Lecture 10: Linear Regression and Regularization

This unit develops affine predictors from least squares through gradient-based
optimization, conditioning, polynomial features, and regularization. Geometry,
objective functions, diagnostics, and software contracts remain connected.

## Current student route

Read the shared [`Part II student guide`](../PART_II_STUDENT_GUIDE.md), then
complete the released `00-affine-model-and-least-squares.ipynb`. Notebooks 01
and 02 below remain planned until their files are published.

## Planned notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | Affine models and least squares | Tested design-matrix contract |
| 01 | Gradient descent and numerical conditioning | Reproducible optimizer experiment |
| 02 | Ridge, lasso, diagnostics, and packaging | Regression pipeline with diagnostics |

The battery case uses regression to estimate a future capacity quantity. The
unit emphasizes that a low training error is neither evidence of generalization
nor proof that a coefficient has a causal interpretation.

# Lecture 16: Neural Networks and Automatic Differentiation

This unit begins with the affine map already understood from regression, then
adds nonlinear composition. One tiny network is differentiated and checked by
hand before a modern automatic-differentiation framework owns routine gradient
calculation.

## Planned notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | Affine units, activations, and computation graphs | Shape-checked forward pass |
| 01 | Backpropagation and gradient checking | Verified tiny manual network |
| 02 | Mini-batch training with automatic differentiation | Versioned neural artifact |

The goal is conceptual and professional fluency, not a semester spent building
an inferior deep-learning framework. Seeds, devices, checkpoints, evaluation
mode, and serialization are part of correctness.

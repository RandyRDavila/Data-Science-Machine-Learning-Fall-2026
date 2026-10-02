# Lecture 12: Learning APIs, Neural Networks, and Backpropagation

This unit begins with the single affine neuron already understood from linear
and logistic regression. Students first design a reusable estimator API without
confusing a fitted estimator with a neuron inside a network. They then assemble
literal neurons into layers, derive backpropagation path by path, vectorize the
same calculation, and identify the boundary between manual mathematics and
automatic differentiation.

## Current student route

Read the shared [`Part II student guide`](../PART_II_STUDENT_GUIDE.md), then
complete the notebooks in order. Notebook 00 supplies the software and
mathematical contracts used by Notebook 01.

## Planned notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | Shared structure, output objectives, estimator and component APIs | Tested `SingleNeuron` interface |
| 01 | Literal layers, pathwise backpropagation, vectorization, and autodiff boundary | Gradient-checked dense network |

The implementation in `src/rice_dsm/ml/neural.py` is deliberately bounded and
inspectable. It is a teaching microscope, not a replacement for a mature tensor
framework. Seeds, shapes, objective semantics, checkpoints, evaluation mode,
and serialization remain part of correctness when students cross that boundary.

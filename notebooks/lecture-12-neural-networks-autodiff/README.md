# Lecture 12: Neural Networks from First Principles to TensorFlow

This unit begins with the single affine neuron already understood from linear
and logistic regression. Students first design a reusable estimator API without
confusing a fitted estimator with a neuron inside a network. They then assemble
literal neurons into layers, derive backpropagation path by path, vectorize the
same calculation, and identify the boundary between manual mathematics and
automatic differentiation.

## Current student route

Read the shared [`Part II student guide`](../PART_II_STUDENT_GUIDE.md), then
complete the notebooks in order. The sequence is intentionally layered: first
make the abstractions and derivatives visible, then apply them to real images,
then use a production framework for vision and language.

Before class, refresh the locked environment and register the repository's
named VS Code kernel from the repository root:

```bash
uv sync --locked
uv run python scripts/setup_course.py
```

Open each notebook in VS Code and select **Rice DSM**. Every Lecture 12 notebook
starts with a preflight that reports the running interpreter and gives recovery
commands if VS Code retained a stale kernel. The notebooks do not launch
JupyterLab.

## Notebook sequence

| Notebook | Topic | Professional artifact |
| --- | --- | --- |
| 00 | Shared structure, output objectives, estimator and component APIs | Tested `SingleNeuron` interface |
| 01 | Literal layers, pathwise backpropagation, vectorization, and autodiff boundary | Gradient-checked dense network |
| 02 | Authentic MNIST, flattening, one-hot targets, fan-in initialization, softmax, and minibatch backpropagation | Tested NumPy multilayer perceptron and error analysis |
| 03 | TensorFlow/Keras, automatic differentiation, CNN geometry, cats-versus-dogs transfer path, logging, and TensorBoard | Reproducible image classifier with run evidence |
| 04 | Tokenization, embeddings, sequence aggregation, and movie-review sentiment | Leakage-aware text-classification pipeline |

The implementation in `src/rice_dsm/ml/neural.py` is deliberately bounded and
inspectable. It is a teaching microscope, not a replacement for a mature tensor
framework. Seeds, shapes, objective semantics, checkpoints, evaluation mode,
and serialization remain part of correctness when students cross that boundary.

Notebook 03 writes local TensorBoard events beneath
`output/tensorboard/lecture-12/`. From the repository root, inspect them with:

```bash
uv run tensorboard --logdir output/tensorboard/lecture-12 --port 6006
```

The small authentic-MNIST artifact keeps Notebook 02 fully inspectable and
gives CI a bounded real-data smoke test. In the normal student route, Notebook
03 downloads full MNIST and Notebook 04 downloads Stanford IMDB through
documented, cache-aware APIs. These network and storage expectations are stated
up front, and the lessons keep provenance, licensing, cache behavior, and split
contracts visible.

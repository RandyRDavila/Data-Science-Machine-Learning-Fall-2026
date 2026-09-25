# Class-built machine-learning platform

This namespace is the integrated software product built collectively by CMOR
438 / INDE 577. It is not a folder in which forty independent projects happen
to coexist. Every accepted component must interoperate through a small common
contract and become part of a reviewed, tagged `rice-dsm` release.

## Platform and product are different artifacts

The class jointly implements reusable algorithms and infrastructure here.
Final-project teams then consume an exact tagged release in separate product
repositories:

```text
issues and design review
        -> class-built rice_dsm.ml
        -> verified course release
        -> independently graded final products
```

A final product records the package tag and commit it used. It does not copy
algorithm source files into the application or silently replace them with
notebook state.

## Common behavioral contracts

`base.py` defines structural protocols for supervised predictors,
transformers, and clusterers. Structural typing means an implementation earns
compatibility by supplying the documented methods; it need not inherit from a
framework superclass.

The first common surface intentionally remains small:

- supervised estimators implement `fit(features, targets)` and
  `predict(features)`;
- fitted transformations implement `fit(features, targets=None)` and
  `transform(features)`; and
- clusterers implement `fit(features)` and `predict(features)`.

Individual implementations still define precise validation, fitted attributes,
randomness, numerical behavior, and exceptions. Interface similarity must not
erase mathematical differences.

## Planned subsystem map

Directories should be created when an approved task supplies real code and
tests, not as empty promises:

```text
rice_dsm.ml
├── preprocessing
├── linear_models
├── neighbors
├── trees
├── ensembles
├── neural_networks
├── clustering
├── decomposition
├── model_selection
└── evaluation
```

Shared metrics already in `rice_dsm.metrics` should be reused or deliberately
migrated rather than duplicated.

## Acceptance standard for an algorithm

An algorithm is not ready for integration merely because it produces plausible
numbers. Its pull request must include:

1. mathematical specification, assumptions, and update equations;
2. a typed public API with NumPy-style docstrings;
3. explicit input, shape, fitted-state, and hyperparameter validation;
4. tests for ordinary behavior, boundaries, invalid input, and invariants;
5. differential comparison with a trusted implementation when one exists;
6. reproducible randomness and numerical-stability analysis;
7. a worked example using real, provenance-documented data;
8. computational-complexity and known-limitation discussions; and
9. peer review plus final maintainer review.

Agreement with scikit-learn is evidence, not the definition of truth. Tests
should also use analytically checkable cases and mathematical properties.

## From incubation to integration

`rice_dsm.contrib` is used for the first toolchain PR and for bounded
experiments whose interface is still being negotiated. Mature code moves here
through an integration issue that identifies its stable module, public names,
tests, documentation, and migration plan. Do not automatically import every
incubator package into this namespace.

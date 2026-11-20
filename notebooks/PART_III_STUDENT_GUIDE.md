# Part III student guide

Part III studies learning objectives that do not begin with an ordinary supplied
target. Its recurring discipline is to name the representation, preserved
structure, fitted artifact, validation evidence, and downstream claim.

## Before each unit

1. Fully close running course notebooks and refresh a clean `main` with
   `uv run --no-project --python 3.12.13 python scripts/refresh_course.py`.
2. Read the matching textbook chapter and lecture README.
3. Inspect the data source, schema, ranges, missingness, and observation unit.
4. State the unsupervised output and invariances before fitting anything.
5. Decide which information is withheld from fitting and may be used only for audit.

## Evidence checklist

An unsupervised result should report:

- the population, observation or node unit, and data provenance;
- feature, scaling, distance, neighborhood, or graph-construction policy;
- objective, hyperparameters, initialization, solver, and stopping rule;
- internal fit evidence and sensitivity to reasonable perturbations;
- external or downstream evidence whose role is clearly separated from fitting;
- computational cost, fitted artifact identity, and known limitations; and
- one conclusion that the evidence does **not** justify.

## Artifact boundary

Use notebooks to investigate and interpret. Move reusable transformations and
algorithms into `src/`, mathematical and failure contracts into `tests/`, and
repeatable jobs into scripts or workflows. Persist every fitted mean, scale,
component, centroid, neighborhood rule, and schema needed to transform future
observations consistently.

## Current route

Lecture 16 introduces clustering, dimensionality reduction, and graph/relational
representations, then derives PCA and evaluates it inside a supervised KNN
pipeline. Later Part III units will deepen clustering, latent-variable,
manifold, density, anomaly, graph, and representation-learning methods without
changing this evidence standard.

# Part II student guide

Part II treats supervised learning as an operated prediction system. The units
are numbered by conceptual dependency, not by calendar week, and an in-person
meeting may cover part of one unit or portions of several.

## Current availability

Every Part II directory contains at least a released notebook 00. Lecture 9
also contains the first complete supervised-learning pipeline, Lecture 12 has
five released neural-network laboratories, Lecture 13 has three released
nearest-neighbor laboratories, Lecture 14 has separate released classification-
tree and regression-tree laboratories, and Lecture 15 has three released ensemble
laboratories spanning forests, boosting, voting, and stacking. A notebook listed in a
unit README is not assigned until the corresponding `.ipynb` file exists and the weekly
announcement names it. Do not create empty substitutes for planned notebooks.

## Before each unit

1. On a clean local `main`, run `uv run --locked python scripts/refresh_course.py`.
   This single cross-platform command fast-forwards main, synchronizes the
   locked environment, verifies course data, and repairs the Rice DSM kernel.
2. Read the matching textbook chapter or chapters and the unit `README.md`.
3. Open the assigned notebook in VS Code and select the **Rice DSM** kernel.
4. Confirm that `data/course_datasets.sqlite` exists; inspect
   `dataset_catalog` before querying an observation table.
5. Record the prediction population, information boundary, target or scientific
   quantity, and evidence claim before fitting a model.

## Completion evidence

For every released notebook:

1. restart the kernel and run all cells in order;
2. complete its written checkpoints and exercises;
3. preserve seeds, units, split definitions, and version identities;
4. identify which code belongs in a reusable module rather than the notebook;
5. run the focused tests named by the unit; and
6. state one limitation that the observed evidence does not resolve.

The professional artifact in each unit README is part of the learning objective,
not decorative paperwork. It makes the model's population, data, transformations,
evaluation, decisions, resource assumptions, and release evidence reviewable.

Lecture 13 additionally bridges the course package and the separate final
project template. Students should reproduce the demonstrated boundary:
full/local data under ignored `data/local/`, a lawful CI fixture under
`data/fixtures/`, reusable algorithms under `src/`, behavior contracts under
`tests/`, and a question-led notebook that imports rather than redefines the
package.

Lecture 14 continues that project handoff. Both tree notebooks import a shared
implementation from `src/`, pair it with analytic and failure tests, and show
how classification and regression evidence differ without duplicating the
algorithm inside the notebooks.

Lecture 15 extends that boundary from one model to systems of models. Students
must preserve bootstrap and random-state contracts, construct stacking features
out of fold, align probability columns by class, and justify the additional
latency, memory, dependency, monitoring, and ownership burden before promoting
an ensemble.

## The cumulative system

Part II follows three paths:

```text
training:   versioned database query -> observations -> candidate -> evaluation -> approved artifact
prediction: validated input -> approved artifact -> score -> decision record
feedback:   delayed outcome -> prediction join -> quality evidence -> governed response
```

Notebook experiments explain and test pieces of these paths. Reusable code
belongs in `rice_dsm`; repeatable operations belong in scripts; service state
belongs behind explicit APIs and stores; CI verifies source; deployment promotes
an identified artifact; monitoring observes the running release.

## Production monitoring unit

Before the operated monitoring laboratory, read Computing Foundations 09 and
10. Students able to run Docker use the live service. Students unable to run
containers use the committed offline evidence and record that they could not
exercise service startup or live recovery. Both routes require a diagnostic
timeline, competing hypotheses, evidence citations, a mitigation, and a
post-incident review.

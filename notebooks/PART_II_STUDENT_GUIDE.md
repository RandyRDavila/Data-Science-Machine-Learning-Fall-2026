# Part II student guide

Part II treats supervised learning as an operated prediction system. The units
are numbered by conceptual dependency, not by calendar week, and an in-person
meeting may cover part of one unit or portions of several.

## Current availability

Every Part II directory currently contains a released notebook 00 and a plan
for later laboratories. A notebook listed in a unit README is not assigned until
the corresponding `.ipynb` file exists and the weekly announcement names it.
Do not create empty substitutes for planned notebooks 01 or 02.

## Before each unit

1. Update an unchanged local `main` branch with `git pull --ff-only`.
2. Run `uv run python scripts/setup_course.py` from the repository root.
3. Read the matching textbook chapter and the unit `README.md`.
4. Open the assigned notebook in VS Code and select the **Rice DSM** kernel.
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

## The cumulative system

Part II follows three paths:

```text
training:   versioned observations -> candidate -> evaluation -> approved artifact
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

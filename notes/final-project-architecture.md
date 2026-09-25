# Final project architecture

The course has one cumulative final project. Earlier shared-platform issues,
pull requests, tests, reviews, and maintenance events are milestones and
evidence within that final assessment rather than unrelated graded exercises.

## Two products, one learning arc

The class first produces a collective software artifact: a tagged release of
`rice-dsm` implementing the semester's machine-learning algorithms and common
experiment contracts. Students then produce independently graded domain
products that consume that release.

This separation resolves an authorship problem. A student should not claim to
have individually implemented forty people's shared library, and a final team
should not copy shared source code to make it appear local. Instead, the final
artifact records exactly which shared release it used and demonstrates that the
student understands, evaluates, integrates, and operates it.

## Cohort structure for approximately forty students

Use eight to ten temporary platform guilds of four or five students. Guilds own
algorithm families or cross-cutting subsystems, not permanent private folders.
Roles rotate across work:

- primary implementer;
- independent verifier or differential tester;
- mathematical or scientific reviewer;
- integration and documentation maintainer; and
- operations or failure-analysis maintainer where relevant.

Across the semester, each student supplies at least one primary implementation,
one independent verification contribution, two substantive peer reviews, and
one integration, conflict-resolution, or maintenance event. These are process
evidence for the final project, not activity-count grades.

## Final team size

Final products may have one to four participants. All products satisfy the same
core end-to-end contract. Each participant adds and defends one substantial
vertical slice, so expected scope scales with team size without lowering the
quality bar for solo work.

Final-product teams need not match platform guilds. Reviewer automation avoids
assigning a final teammate when possible so peer review remains independent.

## Dataset and algorithm breadth

Each product selects a coherent domain dataset suite with regression,
classification, and unsupervised or representation-learning tasks. The product
runs every course algorithm applicable to those task types through the common
experiment interface. It explains exclusions rather than forcing incompatible
algorithms into meaningless comparisons.

The product retains complete candidate evidence and distinguishes:

- class-built algorithms used to demonstrate mathematical understanding;
- trusted-library comparisons used for differential verification; and
- the model selected for a deployed decision or analytical interface.

These may be the same model, but the report must not assume that pedagogical
implementation automatically implies production fitness.

## Final assessment dimensions

Publish point weights only after the project contract stabilizes. Preserve these
dimensions:

1. **Shared-platform evidence:** implementation, verification, review, and
   maintenance work.
2. **Mathematical correctness:** derivations, assumptions, compatibility, and
   interpretation.
3. **Data and experimentation:** provenance, leakage prevention, baselines,
   model selection, uncertainty, and final evaluation.
4. **End-to-end product:** database, package, service, interface, deployment,
   and user-facing coherence.
5. **Reliability and operations:** tests, CI/CD, artifacts, logs, metrics,
   monitoring, failure diagnosis, and rollback.
6. **Communication and responsibility:** documentation, limitations,
   responsible use, demonstration, and oral defense.

For team products, combine a substantial shared-artifact evaluation with
individual evidence and oral defense. Commit counts, lines changed, issue
counts, and automated reviewer assignments are context, not measures of
intellectual quality.

## Release cadence

Publish bounded platform releases after coherent groups of algorithms stabilize
rather than making final products depend on a moving `main` branch. Each release
must pass the existing cross-platform CI and release workflow. Final products
pin the designated release and update only through reviewed dependency PRs.

The final project template remains documentation-only until the first platform
release fixes installation and experiment interfaces. At that point, add a
runnable service scaffold and verify it against the published artifact.

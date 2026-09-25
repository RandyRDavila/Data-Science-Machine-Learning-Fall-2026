# Student contribution program: instructor playbook

This note records the operating design for student contributions to the shared
`rice_dsm` package. It is intentionally separate from the student procedure:
the public workflow should feel simple even though the instructor maintains
substantial safety and integration boundaries behind it.

The working enrollment assumption is approximately forty students. Use eight
to ten temporary platform guilds of four or five students; final-product teams
may later contain one to four students and need not match those guilds.

## Learning outcomes

By the end of the contribution sequence, a student should be able to:

1. turn an open-ended scientific or engineering need into a bounded software
   contract;
2. distinguish upstream, fork, clone, remote, branch, commit, pull request,
   review, CI, and merge;
3. design a typed and documented Python package interface;
4. write unit, boundary, failure, and domain-property tests;
5. interpret CI failures across operating systems;
6. give and respond to evidence-based code review;
7. reconcile concurrent changes without discarding another person's work; and
8. maintain a merged feature when integration exposes a defect or limitation.

## Non-negotiable boundaries

- Students contribute through public forks; do not grant routine write access.
- Only maintainers merge into `main` or create release tags.
- `main` requires the stable `CI gate`; no force pushes or branch deletion.
- Student code executes only in read-only, secret-free pull-request workflows.
- Deployment occurs from reviewed `main`, never directly from a fork PR.
- New dependencies and edits to automation, deployment, shared core interfaces,
  or the lockfile require prior architectural approval.
- Grades, accommodations, student IDs, private communications, secrets, and
  restricted data never enter public GitHub artifacts.
- Provide an equivalent private route when public contribution creates a
  privacy, accessibility, safety, employment, or legal concern.

## Rollout in bounded stages

Do not begin with simultaneous feature PRs from the entire class.

### Stage 0: maintainer rehearsal

Use a separate test fork or volunteer account to execute every documented
command on Windows, macOS, and Linux where practical. Confirm first-time
workflow approval, CI permissions, labels, review requests, and merge behavior.

### Stage 1: toolchain onboarding

Students propose a slug and submit only the generated scaffold. The learning
goal is repository topology, package discovery, tests, commits, and PR review;
domain complexity remains intentionally absent.

### Stage 2: first vertical slice

Each contribution adds one useful behavior with a public contract, focused
tests, and documentation. Limit review size so a classmate can understand the
entire change rather than approve by impression.

### Stage 3: peer review rotation

Assign reviewers across application areas when possible. Require each reviewer
to identify one contract claim, one boundary or failure mode, and one scientific
or mathematical assumption before commenting on style.

### Stage 4: integration and controlled conflict

Pair compatible contributions behind an explicit interface. Create a small,
recoverable conflict in a teaching branch after students have successfully
merged independent work. Never manufacture a conflict in `main` or in a
student's only copy of unmerged work.

### Stage 5: operations and maintenance

Introduce a failing cross-platform check, dependency update, logged failure, or
monitoring signal. The original author and a peer diagnose and repair the
behavior through the same review path.

### Stage 6: tagged platform release and final products

Publish stable platform components as an exact `rice-dsm` release. Final
products live in separate repositories, pin the designated release, and record
its tag and commit. They must not copy algorithm source or depend on a moving
course branch.

## Coordination automation

The reviewed configuration in `.github/course/coordination.json` is disabled
until an opt-in GitHub-handle roster is ready. The task manifest seeds the
shared backlog. Once enabled:

- the task factory previews manifest issues and creates them only through a
  maintainer-triggered protected workflow;
- an active participant comments `/claim` or `/release` to manage one bounded
  task assignment;
- a pull-request workflow requests two load-balanced reviewers while excluding
  authors, linked-issue collaborators, and final-product teammates;
- a weekly digest reports unclaimed, stale, and review-waiting work without
  publishing grades; and
- every automated mutation leaves a visible GitHub timeline event.

Automation coordinates attention; it does not assess intellectual quality,
merge code, or replace maintainer judgment. Review the generated selection and
override it when expertise, accessibility, conflict of interest, or workload
requires a different assignment.

## Instructor issue triage

Before approving a proposal, check:

- Is the slug valid, unique, problem-oriented, and stable enough for imports?
- Can the first vertical slice be reviewed in roughly a few hundred changed
  lines, including tests and prose?
- Does the public interface name units, shapes, invalid input, and exceptions?
- Can important claims be tested without a network service or private data?
- Are data sources, licenses, transformations, and split boundaries available?
- Does the work duplicate a core feature or another active contribution?
- Does it request a dependency that can be avoided or deferred?
- Is the proposed reviewer free of an obvious authorship or grading conflict?

Record scope decisions in the issue so later review evaluates an explicit
contract rather than an unwritten recollection.

## Pull-request intake

For a first-time fork PR:

1. inspect changed workflows, scripts, dependencies, and configuration before
   approving the CI run;
2. confirm the base is `main` and the head belongs to the expected fork;
3. confirm no private information, generated artifacts, credentials, or large
   unexplained data files are present;
4. confirm two eligible peer-review requests, or record why an independent
   exception is necessary, while retaining final maintainer review;
5. require all `CI gate` jobs, conversation resolution, and current-base
   integration before merge; and
6. prefer a coherent squash merge when intermediate commits are only learning
   or correction steps, while preserving the PR discussion as process evidence.

Do not approve workflow execution merely because the author is enrolled. A
compromised student account remains an untrusted identity at the automation
boundary.

## Review rubric without premature point weights

Evaluate six dimensions and publish any eventual grading weights separately:

1. **Problem contract:** users, assumptions, interface, and scope are precise.
2. **Correctness:** implementation matches mathematical and software claims.
3. **Verification:** tests cover normal behavior, boundaries, failures, and
   relevant properties rather than mirroring implementation details.
4. **Reproducibility:** data, models, randomness, dependencies, and commands are
   controlled and documented.
5. **Communication:** names, docstrings, README, examples, and limitations make
   the feature reviewable and usable.
6. **Collaboration:** commits are scoped; reviews are substantive; responses are
   professional; conflicts and follow-up defects are handled responsibly.

## Throughput controls

- Approve proposals in cohorts so CI and review demand remain observable.
- Set a soft changed-line budget and split large work by behavior, not file type.
- Establish review windows and a merge freeze before major lecture releases.
- Avoid having every student edit `rice_dsm/__init__.py`, `pyproject.toml`, or a
  shared registry; those are integration bottlenecks, not evidence of teamwork.
- Use the controlled conflict stage to teach reconciliation deliberately rather
  than relying on accidental lockfile or notebook conflicts.
- Track stalled states: awaiting scope, author work, peer review, CI repair,
  maintainer review, or merge. Each state should have one clear owner.

## Risk register

| Risk | Early signal | Control |
| --- | --- | --- |
| Duplicate package scopes | Similar open issues or slugs | Approve issues and slugs before implementation. |
| Review bottleneck | Many large PRs awaiting instructor | Cohorts, vertical slices, peer review, and size limits. |
| Superficial tests | Assertions repeat constants or implementation | Require boundaries, failures, and domain properties. |
| Environment churn | Frequent independent lockfile edits | Prior approval and maintainer-owned dependency batches. |
| Unsafe automation | PR adds privileged trigger or secret use | CODEOWNERS, security contract tests, and manual inspection before CI approval. |
| Public-data exposure | Notebook output or fixture contains records | Privacy checklist, focused diff review, and private incident route. |
| Cross-platform failure | Paths or shell commands assume one OS | Matrix CI and platform-neutral `pathlib`/Python commands. |
| Abandoned merged code | Author disengages after merge | Small contracts, explicit maintainers, follow-up repair exercise, promotion criteria. |
| Conflict as spectacle | Students lose work or select one side blindly | Backups, teaching branches, `git merge --abort`, and controlled pairs. |

## One-time repository settings after merge

1. Create the labels documented in `.github/README.md`, including
   `area: student contribution`.
2. Create a protected `course-coordination` environment before enabling task
   creation and require instructor approval for its deployment job.
3. Confirm the `main` ruleset requires PRs, `CI gate`, resolved conversations,
   and blocks force pushes and deletion.
4. Retain approval for workflows from first-time outside contributors.
5. Confirm GitHub Pages is restricted to `main` and the release environment
   retains its maintainer approval boundary.
6. Test a PR from a fork and verify that it has read-only permission and no
   repository secrets.
7. Add only opt-in GitHub handles to the public roster through a reviewed PR;
   validate a dry run before changing `enabled` to `true`.
8. Create a public GitHub Project with one auto-add filter,
   `label:"course: work"`, and views for ready tasks, active work, peer review,
   maintainer review, and completed integration. Do not place grades or private
   feedback in the Project.

Recheck these settings at the start and end of the contribution unit. Settings
are external state; repository tests can document the intended contract but
cannot prove the live GitHub configuration remains unchanged.

## End-of-semester disposition

Because students use forks, routine access revocation is unnecessary. Decide
which contributions remain experimental, which need deprecation, and which
meet the stronger bar for promotion into core `rice_dsm`. Preserve merged PRs
and releases as technical history, but do not imply that course completion
guarantees indefinite maintenance or production fitness.

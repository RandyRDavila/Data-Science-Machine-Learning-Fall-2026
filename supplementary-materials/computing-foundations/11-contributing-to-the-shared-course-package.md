# Contributing to the shared course package

This course uses a real public repository to practice the social and technical
work surrounding professional data-science software. A contribution is not a
file uploaded for grading. It is a proposed change that must be understood,
tested, reviewed, integrated, and maintained.

This guide assumes no prior open-source experience. Read the shorter [Git and
GitHub workflow](git-and-github-workflow.md) first if commits, branches, forks,
or pull requests are unfamiliar. Participation also follows the repository
[collaboration standard](../../CODE_OF_CONDUCT.md).

## The collaboration model

Students contribute from personal GitHub forks. They do **not** need write
access to the course repository.

```text
course repository (upstream)
           |
           | fork once on GitHub
           v
your GitHub fork (origin)
           |
           | clone once
           v
your computer
           |
           | branch -> commit -> push
           v
pull request to upstream/main
           |
           | peer review + CI + maintainer review
           v
reviewed merge into the shared package
```

These objects have different jobs:

- The **upstream repository** is the instructor-maintained source of truth.
- A **fork** is a GitHub repository in your account, connected to upstream.
- A **clone** is a local Git repository on your computer.
- A **remote** is a local name for another Git repository's URL.
- A **branch** isolates one coherent line of work inside a repository.
- A **commit** records a local snapshot with authorship and history.
- A **pull request** asks maintainers to review and integrate a branch.
- A **review** evaluates correctness, clarity, risk, and evidence.
- **CI** independently runs encoded checks on the proposed revision.
- A **merge** integrates the accepted history into `main`.

Passing CI is necessary but not sufficient. Tests cannot decide whether the
scientific question is meaningful, documentation is comprehensible, data use
is responsible, or an interface is well designed. Human review owns those
judgments.

## How this work reaches the final project

The `rice_dsm.contrib` scaffold is the first toolchain and review exercise. It
is not a permanent personal territory. Approved, mature algorithms and platform
components converge on the common `rice_dsm.ml` interfaces and are published in
a tagged class release.

Final products live in separate repositories and pin that release. A solo
student or team therefore builds on the class's joint implementation without
copying shared files or depending on a moving branch. The product's provenance
record links the exact package tag, commit, originating issues, and relevant
pull requests.

## Public work, privacy, and academic integrity

The repository, issues, pull requests, commits, and reviews are public. You may
use a GitHub handle that does not expose your legal name. Never include a
student ID, grade, accommodation, private communication, credential, secret,
restricted dataset, or identifiable student record.

Contact the instructor privately if public contribution creates a privacy,
accessibility, employment, safety, or legal concern. An equivalent private
route can assess the same learning objectives. Public participation must not be
the price of receiving an equitable course experience.

This shared package is collaborative work. Individually graded assessments may
have different collaboration rules. A public implementation is not permission
to submit another person's work without attribution or contrary to the stated
assessment policy.

## Phase 1: propose before implementing

Search existing issues and inspect `src/rice_dsm/contrib/` for related work.
When proposing new work, open the **Student package contribution** issue form.
When selecting work from the instructor-reviewed platform backlog, use an open
issue labeled `course: task` and `status: ready`. In either route, define or
confirm:

1. the problem and intended users;
2. a unique package slug such as `graph_statistics`;
3. the proposed functions, classes, inputs, outputs, units, and exceptions;
4. data and model provenance;
5. normal cases, boundaries, expected failures, and domain properties to test;
6. new dependencies or shared files, if any; and
7. one or more possible peer reviewers.

Wait for scope and slug approval before building a large feature. Early design
review is cheaper than discarding a polished solution to the wrong problem.

### Claiming a generated course task

After the public opt-in roster and coordination system are enabled, comment the
following exact command by itself on a ready task:

```text
/claim
```

The bot verifies that you are an active participant, the task has team
capacity, and you do not already own the configured maximum number of active
tasks. Because you have commented, GitHub permits the maintainer-controlled bot
to add you as a native issue assignee. The bot updates status labels and leaves
a visible explanation.

If you cannot continue, do not leave the task silently occupied. Comment:

```text
/release
```

Automation coordinates attention; it does not grant credit, judge quality, or
replace a conversation about scope. Ask the instructor to correct an assignment
when expertise, access, workload, or conflict of interest makes the generated
state inappropriate.

Package slugs use lowercase letters, digits, and underscores, begin with a
letter, and describe the problem rather than an author. Each contribution will
be imported as:

```python
from rice_dsm.contrib.PROJECT_SLUG import public_name
```

## Phase 2: fork and configure remotes

On the course repository's GitHub page, select **Fork** and create a fork in
your account. Clone your fork, replacing `YOUR-GITHUB-NAME` below:

```text
git clone https://github.com/YOUR-GITHUB-NAME/Data-Science-Machine-Learning-Fall-2026.git
cd Data-Science-Machine-Learning-Fall-2026
git remote add upstream https://github.com/RandyRDavila/Data-Science-Machine-Learning-Fall-2026.git
git remote -v
code .
```

The intended remote configuration is:

```text
origin    your fork; you push branches here
upstream  the course repository; you fetch accepted changes here
```

If you already cloned the course repository directly, do not delete work. Read
`git remote -v`, create your GitHub fork, and ask for help reassigning the
remote names safely.

Prepare the project:

```text
uv run python scripts/setup_course.py
uv run pytest tests/test_course_setup.py tests/test_repository.py -q
```

## Phase 3: synchronize before branching

Begin from a clean local `main`:

```text
git status
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
git status -sb
```

`fetch` retrieves remote history without changing working files.
`merge --ff-only` moves local `main` forward only when no divergent local
commit would need reconciliation. Stop and ask for help when Git refuses; do
not add `--force` or invent a merge merely to silence the message.

Create one feature branch that references the approved issue or describes one
outcome:

```text
git switch -c student/graph-statistics
```

Never develop directly on `main`.

## Phase 4: create the passing scaffold

From the repository root, run:

```text
uv run python scripts/scaffold_student_package.py graph_statistics
```

The command creates:

```text
src/rice_dsm/contrib/graph_statistics/
├── __init__.py
├── core.py
└── README.md

tests/contrib/graph_statistics/
└── test_core.py
```

It refuses to overwrite an existing source or test directory. That refusal is
a safeguard: inspect the collision and coordinate with its author rather than
renaming or deleting another contribution.

Run the focused test:

```text
uv run pytest tests/contrib/graph_statistics -q
```

The generated `contribution_name()` function is only an onboarding smoke test.
It demonstrates that the package can be imported and that pytest discovers its
tests. Replace it only alongside the first meaningful behavior and tests.

## Phase 5: develop a vertical slice

A **vertical slice** is the smallest useful behavior crossing interface,
implementation, documentation, and verification. Prefer one complete behavior
over ten unfinished modules.

Use a red-green-refactor loop:

1. **Red:** write one test for missing behavior and observe the expected
   failure.
2. **Green:** write the simplest clear implementation that passes.
3. **Refactor:** improve names and structure while the test remains green.

The contribution contract requires:

- type hints and NumPy-style docstrings for public functions and classes;
- explicit validation and useful exceptions at interface boundaries;
- tests for normal behavior, boundaries, failures, and relevant mathematical
  properties;
- deterministic tests, including controlled random seeds when randomness is
  part of the method;
- a small public interface in the subpackage's `__init__.py`;
- a README explaining the question, interface, assumptions, provenance,
  verification, limitations, and responsible use; and
- no work at import time beyond defining and importing names.

Do not add your subpackage to `rice_dsm/__init__.py`. Explicit imports keep
contributions independent and prevent one project from breaking the entire
course package.

Ask in the issue before editing `pyproject.toml`, `uv.lock`, `.github/`, shared
core interfaces, deployments, or release machinery. A dependency affects every
student's environment and must solve more than one contributor's local
convenience.

## Phase 6: inspect and commit deliberately

Before staging, inspect exactly what changed:

```text
git status --short
git diff
```

Stage named paths rather than an uninspected `git add .`:

```text
git add src/rice_dsm/contrib/graph_statistics
git add tests/contrib/graph_statistics
git diff --staged
git commit -m "Add graph statistics contribution scaffold"
```

A commit message completes the sentence “If applied, this commit will ...”.
Keep generated data, notebook output, caches, `.venv`, and secrets out of the
commit.

## Phase 7: validate before requesting review

Run the narrow checks first, then the same broad gate CI will run:

```text
uv run pytest tests/contrib/graph_statistics -q
uv run ruff check src tests scripts
uv run pytest -q
git diff --check upstream/main...HEAD
```

Read a failure from its first causal error. Do not delete a test, weaken an
assertion, or skip a platform simply to make the status green. Determine
whether the implementation, test, environment, or documented contract is
wrong.

## Phase 8: push and open the pull request

Push the branch to your fork:

```text
git push -u origin student/graph-statistics
```

GitHub normally offers a link to open a pull request. Confirm these endpoints:

```text
base repository: RandyRDavila/Data-Science-Machine-Learning-Fall-2026
base branch:     main
head repository: YOUR-GITHUB-NAME/Data-Science-Machine-Learning-Fall-2026
compare branch: student/graph-statistics
```

Complete the pull-request template. Link the approved issue with `Closes #NN`,
describe the contract rather than listing files, and report exact validation
commands and results. Open a draft pull request when design feedback is useful
before the implementation is complete.

CI runs the proposed revision on Linux, macOS, and Windows with read-only
repository permission. A first-time contributor may need a maintainer to
approve the workflow run. CI does not receive deployment credentials from an
untrusted fork.

## Phase 9: review as an engineering activity

For a contribution pull request, the coordinator requests two eligible
classmates while excluding the author, linked-issue collaborators, and final
product teammates. It prefers reviewers outside the author's current platform
guild and balances open review requests. The maintainer may override any
selection.

A peer reviewer should ask:

- Can I explain the problem and public contract from the README?
- Do names, types, units, shapes, and exceptions agree across code and prose?
- Do tests cover a boundary and a meaningful failure, not only a happy path?
- Is data or model provenance sufficient to reproduce the claim?
- Does the implementation avoid hidden state, import-time work, and needless
  dependencies?
- Are limitations and responsible-use boundaries honest?
- Is the change small enough to review confidently?

Review the code, not the author. Classify comments when useful:

- **blocking:** correctness, security, privacy, reproducibility, or contract
  failure that must change before merge;
- **suggestion:** a concrete improvement worth considering; or
- **question:** missing context or an assumption to clarify.

The author responds with a change, evidence, or a reasoned technical
explanation. Do not mark a conversation resolved until both parties understand
the outcome. Maintainer approval remains the final integration boundary.

Students can review a public pull request without write access. Their review is
important course evidence, but it does not grant merge permission or replace
the protected maintainer and CI boundary.

The weekly coordination digest lists ready tasks, work without recent public
activity, and pull requests awaiting review. It is an operational queue, not a
leaderboard, grade, or inference about effort outside GitHub.

## Phase 10: synchronize and resolve conflicts

A conflict means Git cannot safely choose between overlapping histories. It is
not evidence that anyone made a mistake.

First commit or intentionally discard your current local changes. Then update
local `main` and merge it into the feature branch:

```text
git switch main
git fetch upstream
git merge --ff-only upstream/main
git switch student/graph-statistics
git merge main
```

When Git reports a conflict:

1. run `git status` and open each listed file;
2. locate `<<<<<<<`, `=======`, and `>>>>>>>` markers;
3. understand both versions and write the intended combined result;
4. remove every conflict marker;
5. run the focused tests;
6. stage the resolved files with `git add PATH`; and
7. complete the merge with `git commit`.

If you are uncertain, return to the pre-merge state with:

```text
git merge --abort
```

Do not resolve a conflict by automatically taking “ours” or “theirs” unless you
can explain why discarding the other side is correct. After resolution, rerun
the full gate and push normally. This course uses merge-based synchronization
for the introductory workflow so students do not need to force-push rewritten
history.

## Phase 11: after the pull request merges

Synchronize and remove the merged local branch:

```text
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
git branch -d student/graph-statistics
```

You may delete the fork's feature branch on GitHub. Do not delete a branch with
unmerged work you still need.

The merged commits and pull request preserve authorship. Contribution also
creates maintenance responsibility: when later changes reveal a bug or design
limit, participate in diagnosis and repair.

## A staged semester progression

The workflow becomes more demanding gradually:

1. **Onboarding PR:** create the scaffold and demonstrate the toolchain.
2. **Platform vertical slice:** add one useful, tested behavior for an approved
   algorithm or infrastructure issue.
3. **Independent verification:** test another implementation against
   hand-computable cases, mathematical properties, and trusted software.
4. **Peer review:** review another contribution using the rubric above.
5. **Integration change:** move stable behavior behind the common
   `rice_dsm.ml` contract.
6. **Conflict laboratory:** reconcile controlled overlapping changes.
7. **Release evidence:** write a changelog entry and verify an artifact.
8. **Final product:** consume the tagged class release in a separate repository.
9. **Operational follow-up:** diagnose a failure from CI, logs, or monitoring
   evidence and submit a repair.

This progression separates learning Git mechanics from designing substantial
software, then brings the two together under realistic integration pressure.

## Recovery table

| Symptom | Inspect first | Safe response |
| --- | --- | --- |
| `origin` points to the course repository | `git remote -v` | Stop before pushing; configure your fork and upstream names. |
| `main` has local commits | `git log --oneline --decorate -5` | Preserve the commits and ask for help moving them to a feature branch. |
| Scaffold says a path exists | Both source and test paths | Coordinate; never overwrite or delete another contribution. |
| Import fails locally | `uv run python scripts/setup_course.py` | Verify the repository root and active project environment. |
| CI fails on one operating system | First causal line in that job | Reproduce when possible; remove platform-specific path or shell assumptions. |
| PR says branch is behind | Upstream history and clean status | Merge current upstream `main` into the feature branch. |
| Merge markers are confusing | `git status` and the two intended behaviors | Use `git merge --abort`, ask the other author, and retry deliberately. |
| A secret was committed | `SECURITY.md` | Revoke or rotate it first and report privately; deleting one line is insufficient. |

## Check your understanding

1. Why is a fork different from both a branch and a clone?
2. Why does every student package live below `rice_dsm.contrib` without being
   imported from the root package?
3. What can passing CI establish, and what still requires human review?
4. Why should dependency changes be agreed on before editing the lockfile?
5. What information is public after a pull request is merged?
6. Why is `git merge --abort` sometimes safer than selecting one side of a
   conflict quickly?

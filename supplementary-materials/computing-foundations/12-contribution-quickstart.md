# Contribution quickstart

Use this page at the keyboard. The complete reasoning, recovery steps, and
review rubric are in [Contributing to the shared course
package](11-contributing-to-the-shared-course-package.md).

## Before you begin

- Read `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `SECURITY.md`.
- GitHub issues, commits, pull requests, and reviews are public. Never include a
  grade, student ID, accommodation, credential, private message, restricted
  data, or identifiable student record.
- You may use a GitHub handle that does not reveal your legal name. Contact the
  instructor privately if you need an equivalent private contribution route.
- Do not begin implementation until your proposal is approved or the
  instructor assigns an open task.
- If the contribution comes from a textbook problem, preserve its stable ID
  (for example, `GD-PR1`) in the issue field, branch name, and pull request.
- Do not use `/claim` until the instructor announces that course coordination
  is enabled.

## 1. Fork and clone once

On GitHub, fork
`RandyRDavila/Data-Science-Machine-Learning-Fall-2026` into your account. Clone
your fork, not the instructor's repository:

```text
git clone https://github.com/YOUR-GITHUB-NAME/Data-Science-Machine-Learning-Fall-2026.git
cd Data-Science-Machine-Learning-Fall-2026
git remote add upstream https://github.com/RandyRDavila/Data-Science-Machine-Learning-Fall-2026.git
git remote -v
code .
```

Check the output carefully:

```text
origin    your fork; push your branches here
upstream  the course repository; fetch accepted work from here
```

Then prepare the environment in VS Code's integrated terminal:

```text
uv run python scripts/setup_course.py
uv run pytest tests/test_course_setup.py tests/test_repository.py -q
```

Stop and ask for help if `origin` points to the instructor's repository. Do not
delete an existing clone or uncommitted work to repair a remote.

## 2. Claim or receive one bounded task

When the instructor announces that coordination is enabled, claim a ready task
by placing this exact text by itself in the issue:

```text
/claim
```

If coordination is not yet enabled, use the assignment procedure announced in
class. In either case, confirm the issue defines the package slug, public
interface, assumptions, expected failures, evidence, and allowed files before
writing substantial code. Use an issue title such as
`[GD-PR1] Add optimizer result records` for a textbook contribution.

If you cannot continue with an automatically claimed task, comment:

```text
/release
```

Do not silently occupy work that another contributor could advance.

## 3. Synchronize and create a branch

Begin each contribution from current upstream `main`:

```text
git status
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
git switch -c student/PROBLEM-ID-SHORT-DESCRIPTION
```

Stop if `git status` shows work you do not recognize or the fast-forward merge
fails. Never solve uncertainty with `--force`.

## 4. Create the first scaffold

Use the approved lowercase slug:

```text
uv run python scripts/scaffold_student_package.py PROJECT_SLUG
uv run pytest tests/contrib/PROJECT_SLUG -q
```

The command creates source, test, and README files. It refuses to overwrite an
existing contribution. Coordinate when a name collides; do not rename or
delete somebody else's work.

Keep reusable code in `src/rice_dsm/contrib/PROJECT_SLUG/`, tests in
`tests/contrib/PROJECT_SLUG/`, and experimental analysis in a notebook. Do not
edit `pyproject.toml`, `uv.lock`, `.github/`, shared core interfaces, or
deployment files unless the approved issue explicitly permits it.

## 5. Inspect, test, and commit

```text
git status --short
git diff
uv run pytest tests/contrib/PROJECT_SLUG -q
uv run ruff check src tests scripts
uv run pytest -q
```

Stage only the intended paths and inspect the staged patch:

```text
git add src/rice_dsm/contrib/PROJECT_SLUG
git add tests/contrib/PROJECT_SLUG
git diff --staged
git commit -m "Add SHORT DESCRIPTION contribution scaffold"
```

Never commit `.venv`, credentials, private data, generated caches, or sensitive
notebook output.

## 6. Push and open the pull request

```text
git push -u origin student/PROBLEM-ID-SHORT-DESCRIPTION
```

On GitHub, open a pull request with these endpoints:

```text
base: RandyRDavila/Data-Science-Machine-Learning-Fall-2026 main
head: YOUR-GITHUB-NAME/Data-Science-Machine-Learning-Fall-2026 student/PROBLEM-ID-SHORT-DESCRIPTION
```

Complete every applicable part of the template. Include the textbook problem
ID, `Closes #ISSUE-NUMBER`, the contract and limitations, and the exact checks
you ran. A
first-time external contribution may wait for a maintainer to approve its CI
run; this is expected.

## 7. Participate in review

When coordination is enabled, it requests two eligible classmates. Otherwise,
follow the instructor's announced review assignment. Reviewers examine the
contract, scientific assumptions, types and units, boundary and failure cases,
tests, provenance, and limitations. A passing check is evidence, not automatic
approval.

Respond to each comment with a code or documentation change, supporting
evidence, or a reasoned technical explanation. Push follow-up commits to the
same branch; the pull request updates automatically. The maintainer makes the
final merge decision.

## 8. Synchronize after merge

```text
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
git branch -d student/PROBLEM-ID-SHORT-DESCRIPTION
```

The merged pull request preserves your authorship and discussion. It also
creates maintenance responsibility: participate when later integration reveals
a defect or limitation.

## Fast recovery

| Problem | Safe first action |
| --- | --- |
| Wrong directory or import failure | Confirm the terminal contains `pyproject.toml`; rerun the setup command. |
| `origin` is not your fork | Stop before pushing and ask for help repairing remotes without deleting work. |
| Scaffold path already exists | Stop and coordinate with the issue owner. |
| CI fails | Read the first causal error; decide whether code, test, contract, or environment is wrong. |
| Upstream changed | Merge current upstream `main` into your feature branch and rerun tests. |
| Merge becomes confusing | Run `git merge --abort`, preserve your work, and ask for help. |
| A secret was committed | Revoke or rotate it immediately, then report privately using `SECURITY.md`. |

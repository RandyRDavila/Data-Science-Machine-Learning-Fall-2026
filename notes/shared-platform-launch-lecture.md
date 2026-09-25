# Instructor runbook: launching the shared machine-learning platform

This lesson introduces the semester-long contribution workflow without asking
students to learn Git, package design, testing, review, and machine learning in
one unstructured leap. It is designed as a 75- to 90-minute block inside a
longer class meeting. The first student change is deliberately small: a passing
subpackage scaffold. Scientific complexity arrives only after the toolchain is
understood.

## Learning outcomes

By the end of the block, students should be able to:

1. distinguish the course repository, a GitHub fork, a local clone, a branch,
   a commit, a pull request, a review, CI, and a merge;
2. explain why reusable algorithms belong in package modules rather than only
   in lecture notebooks;
3. create and test a contribution scaffold without changing shared core files;
4. describe what CI can verify and what still requires scientific human review;
5. locate the boundary between the shared platform and the separate final
   product; and
6. identify information that must never be placed in a public repository.

## Before class

Use the merged `main` branch for the demonstration. From the repository root,
run:

```text
git switch main
git pull --ff-only
uv run python scripts/setup_course.py
uv run python scripts/course_coordination.py validate
uv run pytest tests/test_student_contribution_scaffold.py tests/test_course_coordination.py -q
```

The validation command should report `enabled=False` until the opt-in GitHub
handle roster, protected environment, labels, and dry-run rehearsal are ready.
Do not advertise `/claim` as live before that activation announcement. Collect
GitHub handles through a private course system, with an explicit public opt-in;
never create a public roster from the enrollment list.

Have these pages ready:

- `STUDENT_START_HERE.md`;
- the student [contribution quickstart](../supplementary-materials/computing-foundations/12-contribution-quickstart.md);
- the complete [fork-to-review guide](../supplementary-materials/computing-foundations/11-contributing-to-the-shared-course-package.md);
- `src/rice_dsm/contrib/README.md` and `src/rice_dsm/ml/README.md`;
- `notes/final-project-architecture.md`; and
- one successful and one failed GitHub Actions run, if available.

Use a disposable demonstration branch and slug. Do not create the demo directly
on `main`, and remove only the branch you deliberately created after class.

## Teaching sequence

### 0-10 minutes: begin with the product

State the semester objective in one sentence:

> We will jointly build a tested machine-learning package, publish stable
> releases, and use an exact release inside independently designed final
> products.

Draw the dependency direction:

```text
lecture laboratory -> reviewed package contribution -> tagged class release
                                                     -> team or solo product
```

Emphasize that notebooks remain valuable experimental laboratories. They are
not the sole source of reusable behavior, a production service, or a durable
deployment system. Package modules make behavior importable; tests make claims
repeatable; releases give products a stable dependency.

### 10-25 minutes: establish the Git and GitHub mental model

Use the topology diagram in the full guide. Ask students to supply the verb for
each transition:

```text
course repository --fork--> personal GitHub repository
personal repository --clone--> local repository
working tree --commit--> local history
feature branch --push--> personal GitHub repository
feature branch --pull request--> proposed change to course main
```

Correct three common misconceptions explicitly:

- a fork is a repository on GitHub, not a local branch;
- a commit is local until it is pushed; and
- a pull request proposes integration but does not itself merge or prove
  correctness.

### 25-45 minutes: perform one complete local change

In a clean demonstration clone, show `git remote -v` and identify `origin` as
the personal fork and `upstream` as the course repository. Then run:

```text
git switch main
git fetch upstream
git merge --ff-only upstream/main
git switch -c student/demo-scalar-baseline
uv run python scripts/scaffold_student_package.py demo_scalar_baseline
uv run pytest tests/contrib/demo_scalar_baseline -q
git status --short
git diff
```

Open the generated module, test, and README in VS Code. Explain that the
scaffold is intentionally trivial: today it proves package discovery, imports,
test discovery, and repository placement. Later work replaces the smoke-test
behavior with a small scientifically meaningful vertical slice.

Show deliberate staging rather than `git add .`:

```text
git add src/rice_dsm/contrib/demo_scalar_baseline
git add tests/contrib/demo_scalar_baseline
git diff --staged
git commit -m "Add scalar baseline contribution scaffold"
```

### 45-60 minutes: connect tests, CI, and review

Run the narrow test first and then explain the broad gate:

```text
uv run pytest tests/contrib/demo_scalar_baseline -q
uv run ruff check src tests scripts
uv run pytest -q
```

Separate the responsibilities:

| Mechanism | Evidence it can provide | What it cannot decide alone |
| --- | --- | --- |
| Unit and property tests | Encoded examples, boundaries, failures, invariants | Whether the scientific question or assumptions are appropriate |
| Cross-platform CI | The committed revision passes automated checks in clean environments | Whether documentation is understandable or a model is responsibly used |
| Peer review | An independent reader can challenge the contract, tests, and assumptions | Permission to merge |
| Maintainer review | The change fits the shared architecture and release boundary | Permanent absence of future defects |

If a failed Actions run is available, read the first causal error rather than
the final cascade. Model the question: “Is the contract, implementation, test,
or environment wrong?” Never teach students to delete evidence merely to make
a check green.

### 60-75 minutes: explain the collaboration lifecycle

Walk through the public state sequence:

```text
ready issue -> /claim -> branch -> draft PR -> CI and peer review
            -> maintainer review -> merge -> maintenance -> tagged release
```

Until coordination is activated, replace `/claim` with the instructor's
announced assignment process. Once active, the automation requests two eligible
peer reviewers. It excludes the author, linked-issue collaborators, and known
final-product teammates; the instructor can always correct the assignment.

Make the privacy and authority boundaries explicit:

- students contribute from forks and do not need write access to the course
  repository;
- automation coordinates work but neither assigns grades nor merges code;
- only maintainers merge and publish releases;
- grades, student IDs, accommodations, credentials, private messages, and
  restricted data never belong in public GitHub artifacts; and
- an equivalent private route is available when public participation creates a
  legitimate barrier.

### 75-90 minutes: rehearse and check understanding

In pairs, have students identify the safe next action in three scenarios:

1. `origin` points to the course repository instead of their fork;
2. the scaffold refuses because its slug already exists; and
3. CI passes, but a reviewer finds that the README never defines the input
   units.

Expected answers: stop and fix the remote configuration without deleting work;
coordinate rather than overwrite; and revise the contract and evidence before
merge because passing CI is not sufficient.

Use this exit ticket:

1. What is the difference between a fork and a branch?
2. Why do products depend on a tagged release rather than `main`?
3. Name one claim a test can support and one judgment a human must still make.
4. Where would you put reusable code, its tests, and an exploratory analysis?

## Student action after class

Ask students to complete only the announced stage:

1. read the quickstart and collaboration standard;
2. create a GitHub account or privacy-preserving handle if needed;
3. opt into the public roster through the private course form;
4. fork and clone the repository, configure `upstream`, and run setup; and
5. wait for an approved issue or ready task before creating a contribution.

The first submitted pull request should be the scaffold plus its generated
README and test unless a different scope is explicitly approved. Do not ask the
whole class to improvise substantial algorithms simultaneously.

## After class

Record points of confusion and repair the documentation before enabling the
coordinator. Follow the protected activation checklist in
`notes/student-contribution-program.md`: create labels and the
`course-coordination` environment, add only opt-in handles through review, run
the task factory in dry-run mode, rehearse with a small cohort, and only then
change `enabled` to `true` in a pull request.

# Git and GitHub workflow

Git records project history on your computer. GitHub hosts a related remote
repository and adds accounts, issues, pull requests, reviews, Actions, and
releases. Saving a file, committing it with Git, and pushing its branch to
GitHub are three different events.

The textbook's Git and GitHub appendix contains the full worked lessons,
including staging, coherent commits, branches, synchronization, conflicts,
recovery, and CI. This page is the daily course route.

## Before changing anything

```text
git status
git switch main
git pull --ff-only
git status -sb
```

Stop if `git status` reports work you do not understand. `pull --ff-only`
updates a clean local branch only when Git can do so without inventing a merge.

## Create one branch for one purpose

```text
git switch -c student/describe-one-change
```

A branch is a movable name for a line of commits, not a duplicate directory.
Use a short name that describes the intended outcome. Do not combine unrelated
notebook, package, and formatting changes simply because they happened on the
same day.

## Inspect, select, and commit

```text
git status --short
git diff
git add path/to/file.py path/to/test_file.py
git diff --staged
git commit -m "Validate the probability boundary"
```

The working tree contains current files. The staging area selects exact content
for the next commit. A commit records the staged snapshot in the local Git
repository. Named paths make accidental generated files and secrets easier to
notice than an uninspected `git add .`.

## Verify before publishing

Run the checks appropriate to the change:

```text
uv run ruff check src tests scripts
uv run pytest -q
git diff --check main...HEAD
```

For textbook changes, also compile and visually inspect the PDF. For a focused
change, run the narrow relevant test first and the complete gate before merge.

## Push and open a pull request

```text
git push -u origin student/describe-one-change
```

Pushing transfers commits and a branch reference to GitHub. It does not merge
the branch. Open a pull request with your branch as the compare branch and
`main` as the base. Complete the template with intent, evidence, limitations,
and risky review areas.

If you do not have write access, create a GitHub fork, clone your fork, and open
a pull request from the fork's branch to the course repository's `main`. A fork
is a GitHub repository relationship; it is not the same object as a branch.

## Read CI as evidence

GitHub Actions starts checks for the pull request. A red status is a symptom.
Open the failed job, find the first causal error, reproduce it locally when
possible, and make a new commit that repairs the stated contract. Do not erase
a test or weaken an assertion merely to make the status green.

Passing CI establishes only the claims encoded by its checks. It does not prove
that prose is clear, a plot is honest, a model is scientifically valid, or a
deployment is usable. Human review owns those judgments.

## After merge

```text
git switch main
git pull --ff-only
git branch -d student/describe-one-change
```

Deleting the merged local branch removes a movable name, not the commits now
reachable from `main`. Do not delete a branch with unmerged work unless you have
inspected and intentionally preserved or abandoned that work.

## Sensitive information

Never commit API keys, tokens, passwords, private student records, restricted
research data, or secrets hidden in notebook output. Removing a secret from the
latest file does not remove it from Git history or workflow logs. Revoke or
rotate an exposed credential first and follow `SECURITY.md` privately.

## Check your understanding

1. How do `git diff`, `git diff --staged`, and a GitHub pull-request diff differ?
2. Why can a clean working tree still be behind `origin/main`?
3. What does passing CI establish, and what does it leave for human review?
4. Why are a fork, branch, and pull request three distinct objects?

# Data Science and Machine Learning

*A Systems Approach*

This repository is the source and executable companion for a developing
graduate text used in **CMOR 438 / INDE 577: Data Science & Machine Learning**
at Rice University.

# Repository automation and governance

This directory contains the repository-facing contracts that GitHub applies to
issues, pull requests, dependencies, ownership, and automation.

## Workflows

- **Course CI** runs the complete locked environment, coordination-manifest
  validation, build, lint, and test suite on Ubuntu, macOS, and Windows. `CI
  gate` is the single stable required check.
- **Textbook** compiles relevant LaTeX changes without warnings and uploads the
  generated PDF for review. Because the workflow is path-limited, do not make it
  a universally required status check.
- **Dependency Review** rejects newly introduced high- or critical-severity
  vulnerable dependencies on relevant pull requests. It is also path-limited.
- **Pull Request Labels** applies area labels from base-branch configuration. It
  uses `pull_request_target` only to write labels and deliberately never checks
  out or executes pull-request code.
- **Course Site Delivery** compiles the text, builds one bounded static artifact,
  deploys it to GitHub Pages from `main`, and then verifies the public revision,
  manifest, and textbook checksum.
- **Course Release** reruns the full verification suite for `course-v*` tags,
  assembles the PDF and Python distributions with checksums and provenance, and
  stops at the protected `course-release` environment before publication.
- **Course Contribution Coordination** processes exact `/claim` and `/release`
  commands and requests balanced peer reviewers. Privileged events execute only
  the reviewed default-branch coordinator, never fork code.
- **Course Task Factory** previews the reviewed task manifest and creates
  missing issues only after an explicit maintainer request and the protected
  `course-coordination` environment boundary.
- **Course Coordination Digest** updates one public operational queue each week
  after coordination is enabled. The digest reports workflow state, not grades
  or contribution quality.

Actions are pinned to immutable commits. Dependabot proposes updates to the
human-readable versions recorded in comments.

## Student contribution security boundary

Students contribute from public forks and do not need collaborator or write
access to this repository. Package extensions remain isolated below
`rice_dsm.contrib` and enter `main` only through the ordinary pull-request and
review path.

Workflows that build or test pull-request code use the `pull_request` event and
top-level `contents: read` permission. GitHub withholds repository secrets from
untrusted fork runs. The labeler is the sole `pull_request_target` workflow; its
contract test prevents checkout or `run` steps, so it can label a PR without
executing contributor-controlled code with its write token. Site deployment
runs only for a reviewed push to `main`, and course-release publication runs
only for a maintainer-created version tag through its protected environment.

Do not add a workflow that checks out or otherwise executes pull-request code
under `pull_request_target`, `workflow_run`, `issue_comment`, or another
privileged event. Do not expose a secret merely to make an untrusted test pass.
Separate untrusted verification from trusted publication and promote only the
reviewed artifact or revision.

The coordination engine is disabled in
`.github/course/coordination.json` until an opt-in GitHub-handle roster is
reviewed. Its default-branch scripts may assign issue commenters, request public
peer reviews, and update labels with narrowly scoped tokens. They never merge,
deploy, publish grades, or decide whether a review is substantive.

## Recommended `main` ruleset

Configure these settings in GitHub after the files reach the default branch:

1. Require changes through pull requests.
2. Require the `CI gate` status check.
3. Require conversation resolution before merge.
4. Block force pushes and branch deletion.
5. Require linear history if the repository will use squash or rebase merges.
6. Require code-owner approval only after at least one independent reviewer is
   consistently available; otherwise the owner would be unable to merge a solo
   maintenance pull request.
7. Optionally require signed commits after every contributor has a documented
   signing workflow.

Do not require path-limited checks globally: GitHub may have no matching check to
report on a pull request that does not touch those paths.

Under **Settings → Actions → General → Fork pull request workflows**, retain
approval for first-time outside contributors. Approval permits a bounded CI run;
it is not approval of the code or permission to merge. Review the changed
workflow, dependency, and script files before authorizing execution.

## Delivery environments

After this configuration reaches `main`, make these one-time repository-setting
changes:

1. In **Settings → Pages**, select **GitHub Actions** as the publishing source.
2. In **Settings → Environments**, restrict `github-pages` to `main`.
3. Create `course-release`, restrict it to tags matching `course-v*`, and add a
   required reviewer. If the repository has only one maintainer, do not prevent
   that maintainer from approving their own deployment.
4. Create `course-coordination` with a required instructor reviewer before
   enabling the public roster or applying task creation. Keep task previews
   outside the protected environment so the exact proposed issues remain
   inspectable without mutation.

The site path is continuous deployment: a relevant, reviewed change on `main`
is published automatically. The tagged-release path is continuous delivery: a
verified artifact reaches a human approval boundary before publication.

The release version has one source of truth. If `pyproject.toml` contains
`version = "0.1.0"`, publish it with an annotated tag named `course-v0.1.0`:

```bash
git tag -a course-v0.1.0 -m "Course release 0.1.0"
git push origin course-v0.1.0
```

Do not move a published tag. Correct a release with an incremented patch version.
To correct the course site, use a focused revert or repair pull request and let
the ordinary `main` workflow deploy the new revision. This keeps rollback
observable and preserves the same controls as forward changes.

The build and publish jobs are separate deliberately. Publication downloads the
exact verified artifact; it does not rebuild after approval. No personal token
or cloud secret is required because permissions are scoped to the individual
job that deploys Pages or creates a release.

The worked student-facing explanation is [From CI to delivery and
deployment](../supplementary-materials/computing-foundations/08-continuous-delivery-and-deployment.md).

## Labels expected by automation

The path labeler expects these repository labels:

```text
area: automation
area: package
area: tests
area: notebooks
area: textbook
area: syllabus
area: data
area: deployment
area: student contribution
```

The coordination workflow also creates these operational labels when task
automation is deliberately enabled:

```text
course: task
course: work
course: coordination
status: ready
status: claimed
review: peer-requested
family: <manifest family>
```

For a GitHub Project, use its single broad auto-add rule with the filter
`label:"course: work"`. The task factory applies that label to generated issues,
and the peer-review coordinator applies it to relevant pull requests. Use
Project views for workflow state and workload; never add grades or private
feedback to the public Project.

The issue forms use GitHub's standard `bug`, `documentation`, `enhancement`, and
`question` labels. Labels must exist before GitHub can apply them automatically.

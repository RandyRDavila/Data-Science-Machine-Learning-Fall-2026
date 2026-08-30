# From CI to delivery and deployment

Software is not deployed merely because it works on one computer. A deployed
system is a particular, identifiable artifact running in a particular
environment under an explicit release policy. This repository provides two
small but real examples:

1. a course website that is continuously deployed from reviewed changes on
   `main`; and
2. a versioned course release that is continuously delivered to an approval
   boundary before GitHub publishes it.

The examples are intentionally static and inexpensive. The control flow is the
same one used for APIs, model services, documentation sites, containers, and
mobile applications.

## The vocabulary is the architecture

**Source** is the version-controlled input: Python, LaTeX, HTML, configuration,
and tests.

**Continuous integration (CI)** automatically combines a proposed change with
the rest of the project and tests their contracts. CI answers, “Is this revision
a valid candidate?” It does not make the candidate public.

**Build** transforms source into an **artifact**. An artifact is a bounded file
or collection of files intended to move between stages without being rebuilt.
Examples include a wheel, source distribution, PDF, container image, and static
site archive.

**Environment** is a named execution or publication boundary with its own
policy. Development, staging, and production are environments. In this
repository, `github-pages` and `course-release` are GitHub environments.

**Continuous delivery** automatically produces a verified, releasable artifact
and stops at a deliberate decision boundary. A human may inspect evidence and
approve promotion.

**Continuous deployment** automatically promotes every qualifying revision
without a manual approval. The absence of a button press does not mean the
absence of controls: review, CI, branch protection, scoped permissions, and
post-deployment verification are the controls.

**Release** is a named, immutable statement that particular artifacts represent
a version of the project. **Deployment** places an artifact into an environment.
One release may be deployed to several environments, and an environment may
receive many releases over time.

**Smoke test** is a small post-deployment test of the most important public
contract. It asks whether the deployed system is reachable and recognizably
correct. It is not a substitute for the full pre-deployment suite.

**Rollback** restores a previously acceptable state. In a version-controlled
workflow, rollback normally means a new, reviewed change that reverses a bad
change, not deleting history or silently moving a version tag.

## The two pipelines

```text
pull request
    |
    +--> CI on Linux, macOS, Windows --> CI gate --> review --> merge
                                                            |
                                                            v
main --> compile textbook --> build one site artifact --> GitHub Pages
                                      |                          |
                                      +-- manifest               +-- smoke test

course-vX.Y.Z tag --> full tests --> PDF + wheel + source archive
                                      |
                                      +-- checksums + provenance
                                      |
                                      v
                              course-release approval
                                      |
                                      v
                               GitHub Release
```

The direction matters. The release stage downloads the artifact created by the
build stage. It does not check out the repository and rebuild. This property is
often summarized as **build once, promote the same artifact**. Rebuilding after
approval could produce different bytes because of a changed dependency, clock,
compiler, or configuration.

## Pipeline 1: a small production deployment

`.github/workflows/course-pages.yml` runs after a relevant change reaches
`main`. It performs these stages:

1. Check out the exact `main` commit without preserving write credentials.
2. Compile the textbook and reject unresolved references and layout warnings.
3. Run `scripts/build_course_site.py` to create `build/course-site/`.
4. Upload that directory as the one GitHub Pages artifact.
5. Give only the deployment job permission to request an identity token and
   write to Pages.
6. Deploy the uploaded artifact to the `github-pages` environment.
7. Fetch the public page, manifest, and PDF with
   `scripts/smoke_test_course_site.py`.
8. Confirm that the public revision is the expected commit and that the PDF's
   byte count and SHA-256 digest match the manifest.

The build refuses to write into a nonempty output directory. This small guard
prevents a stale file from a previous build from entering a new deployment.
The manifest makes the deployed state observable:

```json
{
  "revision": "complete Git commit SHA",
  "generated_at": "UTC timestamp",
  "artifacts": {
    "textbook": {
      "path": "textbook/data-science-machine-learning-textbook.pdf",
      "bytes": 123456,
      "sha256": "..."
    }
  }
}
```

The hash is a content identity. If one byte changes, the digest is expected to
change. A matching hash does not prove that the textbook is correct; it proves
that the public file is the file described by this deployment.

## Pipeline 2: an approved immutable release

The package version in `pyproject.toml` is the authoritative software version.
A maintainer creates an annotated tag with exactly the corresponding name:

```bash
git tag -a course-v0.1.0 -m "Course release 0.1.0"
git push origin course-v0.1.0
```

`.github/workflows/course-release.yml` rejects a mismatched tag such as
`course-v0.2.0` when the project still declares version `0.1.0`. It reruns the
Python checks, builds the wheel and source archive, compiles the PDF, and creates:

- `data-science-machine-learning-textbook.pdf`;
- the `rice_dsm` wheel;
- the `rice_dsm` source archive;
- `release-manifest.json`; and
- `SHA256SUMS`.

GitHub records build provenance for the bundle. The publish job then waits at
the protected `course-release` environment. After approval, it downloads the
same workflow artifact and attaches those files to the tag's GitHub Release.
The workflow can safely repair a partially published release by replacing its
attachments with the verified artifact.

A release tag is not a scratch label. Do not delete it and point the same name
at different source. Correct a defect with a new patch version, such as
`course-v0.1.1`, so users can identify what they received.

## Repository configuration after merge

The workflow files describe automation, but repository settings define the
trust boundaries. A maintainer configures:

1. **Pages source:** GitHub Actions.
2. **`main` ruleset:** changes through pull requests, the stable `CI gate`,
   resolved conversations, and no force pushes or branch deletion.
3. **`github-pages` environment:** deployment branches limited to `main`.
4. **`course-release` environment:** tag pattern `course-v*` and a required
   reviewer. Leave self-review possible if only one maintainer is available.

The workflows use the short-lived repository token supplied to each run. They
do not require a personal access token, cloud credential, or checked-in secret.
Permissions are declared at the smallest useful job boundary: the build can
read source, the Pages job can deploy Pages, and the release job can write a
release. A compromised build step therefore does not automatically inherit
every publication permission.

## Run the artifact locally

Compile the textbook, build the site with a known revision, and serve the static
directory:

```bash
make -C textbook
uv run python scripts/build_course_site.py \
  --revision local-preview \
  --textbook textbook/textbook.pdf
uv run python -m http.server 8000 --directory build/course-site
```

Visit `http://localhost:8000`. Stop the server with `Ctrl+C`. The local server is
only a preview; it does not grant deployment authority or simulate GitHub's
environment policy.

To rebuild, remove only the generated `build/course-site/` directory and run the
builder again. Its refusal to merge outputs is part of the artifact contract.

## Failure and rollback drills

Practice the control decisions, not merely the happy path.

### A CI failure

Read the first causal failure, reproduce it locally, change source or tests, and
push another commit to the same pull request. Do not weaken an accurate test
merely to obtain a green check.

### A site build failure

The previous Pages deployment remains the known public version. Fix the source
through a new pull request. Do not manually edit generated files on the server;
the next deployment would erase such an unreviewed change.

### A bad public deployment

Open a focused revert pull request, run CI, merge it, and let the normal pipeline
deploy the corrective revision. This preserves the incident and recovery in
history. For an urgent safety or privacy incident, first disable the affected
surface using repository controls, then perform the same reviewed repair.

### A bad tagged release

Do not move the old tag. Document the defect, increment the patch version, merge
the fix, and publish a new tag. Consumers can then distinguish the defective and
corrected artifacts.

## Questions for technical review

1. Which stage first creates each artifact, and can a later stage rebuild it?
2. Which job can write to Pages? Which job can write a GitHub Release?
3. What evidence connects a public PDF to a source revision?
4. Which failures prevent publication, and which occur only after deployment?
5. Where would a database migration fit, and why would its rollback be harder
   than replacing static files?
6. Which additional controls would be required before deploying a service that
   processes credentials, research data, or student records?

The final question marks the limit of the example. A static public site is an
appropriate real deployment for this course repository. It demonstrates the
mechanism without pretending that it carries the operational risk of a model
API, database, or regulated data system.

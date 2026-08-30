# Security policy

## Supported version

The current `main` branch is the supported course version. Historical branches,
old lecture exports, and local modifications are not maintained as security
releases.

## Report a vulnerability privately

Do not open a public issue for a suspected vulnerability, exposed credential,
private student information, restricted data, or a path to unauthorized access.
Use GitHub private vulnerability reporting when it is enabled. If it is not
available, contact the repository owner privately through the institutional
contact listed in the course materials. Include the affected revision, impact,
minimal reproduction, and suggested mitigation without including real secrets
or private records.

Public issues are appropriate for ordinary correctness bugs that do not expose
sensitive information or access.

## Course-specific security boundaries

- API keys and cloud credentials belong in ignored local environment files,
  GitHub Actions secrets, or an approved secret manager.
- Notebooks, logs, screenshots, fixtures, and model artifacts must not contain
  student records, credentials, tokens, or restricted research data.
- Treat untrusted serialized Python objects as executable code. Load model and
  data artifacts only from controlled, integrity-checked sources.
- GitHub Actions use least-privilege token permissions and immutable action
  references. Workflows triggered by untrusted pull requests must not execute
  code with write credentials.
- Dependency updates remain ordinary pull requests and must pass review and CI.
- If a secret is exposed, revoke or rotate it first; removing it from the latest
  commit is not sufficient because Git history and logs may retain it.

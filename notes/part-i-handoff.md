# Part I handoff: completion and second-pass plan

**Recorded:** August 29, 2026
**Course:** CMOR 438 / INDE 577, Data Science & Machine Learning, Fall 2026
**Status:** Part I is structurally complete; it needs one deliberate editorial
and terminology pass before being treated as finished.

## Provisional Part I identity

Working title:

> **Part I — Foundations of Professional Data Science Systems**

The end-to-end data-product notebook is the natural endpoint. Part I begins
with a student opening the repository and learning what a Python value is. It
ends with the student tracing a scientific value through validated software,
storage, an HTTP interface, a client, deployment, testing, and monitoring.

This is more than a Python introduction. The intended arc is:

```text
values and native data
  → functions, classes, and data models
  → reusable modules and packages
  → tests, automation, and CI/CD
  → NumPy, pandas, visualization, and simulation
  → databases and larger-than-memory/cloud workflows
  → bounded LLM tools and agents
  → an observable end-to-end data product
```

Probability, mathematics, physics, chemistry, measurement, and industrial
engineering examples are the means of teaching transferable Python and
software-engineering ideas. They should not obscure the primary concept in a
notebook.

## Current Part I sequence

### Lecture 1 — Python foundations I

1. Cross-platform environment, VS Code, and Jupyter kernel
2. Values, types, and objects
3. Strings and text data
4. Lists, tuples, and sequences
5. Dictionaries, sets, and structured data
6. Iteration, comprehensions, and generators

### Lecture 2 — Python foundations II and native data

1. Functions and functional patterns
2. Classes and data modeling
3. Lambdas, `*args`, and `**kwargs`
4. Native CSV and JSON data loaded into a custom knowledge graph

### Lecture 3 — Professional data-science systems

1. Projects, environments, packaging, and versions
2. Scripts, modules, packages, and public interfaces
3. Testing and automation, including CI/CD
4. NumPy and pandas foundations
5. Visualization and simulation
6. Local, remote, cloud, and larger-than-memory data systems
7. LLM tools and agents for scientific software
8. End-to-end data products: database to device

Lecture 3 currently has the historical directory name
`lecture-03-packages-numpy-pandas`. Its content is now much broader. Consider
renaming the lecture during the second pass, but only with a careful update of
all tests, links, workflows, and documentation.

## Decisions already made

- Assume no prior terminal, PowerShell, VS Code, Jupyter, packaging, API, or
  professional software-engineering knowledge.
- Use VS Code as the student editor and navigator. Course setup must not launch
  JupyterLab.
- Keep setup cross-platform across Windows, macOS, and Linux.
- Use a repository-local virtual environment and the named **Rice DSM** kernel.
- Explain mechanisms before relying on commands or jargon.
- Teach NumPy-style docstrings, type hints, deliberate exceptions, and public
  compatibility contracts.
- Treat tests as both engineering safeguards and instructional examples.
- Execute every notebook from top to bottom in CI and test on all three major
  operating systems.
- Move reusable code into the `rice_dsm` package instead of allowing notebooks
  to become disconnected scripts.
- Use serious science and mathematics examples while keeping the programming
  idea explicit.
- For LLM systems, the model proposes; schemas, ordinary code, deterministic
  policy, accountable humans, and durable orchestrators validate and execute.
- Keep API credentials outside notebooks, source, browser code, logs, and Git.
- Core notebooks must be deterministic and usable without credentials, paid
  accounts, GPUs, downloads, or network access.
- Treat free chat access, API free tiers, downloadable weights, licenses, and
  total operating cost as different concepts.
- The end-to-end notebook should remain the final synthesis of Part I.

## API terminology pass completed

A first focused pass was completed after noticing that many students may not
know what “API” means.

- Lecture 1 now defines the acronym at first use.
- Lecture 2 formalizes a Python function/package API as a supported calling and
  compatibility contract.
- Lecture 3 distinguishes in-process Python APIs from HTTP web APIs.
- The LLM lesson explains the client → authenticated request → provider
  inference → response → validation path.
- The end-to-end lesson defines method, path, query parameter, endpoint,
  headers, request body, status, and response.
- The supplementary guide
  [`What is an API?`](../supplementary-materials/computing-foundations/07-what-is-an-api.md)
  provides the zero-assumption explanation, diagrams, misconceptions, and
  exercises.
- Regression tests protect these explanations in
  `tests/test_api_teaching.py`.

Validation at this checkpoint: **304 tests passed**, including execution of
every notebook from top to bottom.

## Second-pass checklist for Part I

Begin the next design session here.

### 1. Establish a canonical Part I glossary

Inventory acronyms and technical terms in order of first appearance. Likely
examples include CLI, API, SDK, IDE, kernel, environment, package, module,
distribution, dependency, lockfile, CI, CD, DBMS, SQL, HTTP, JSON, schema,
endpoint, client, server, frontend, backend, cloud, object storage, IAM, RAG,
LLM, MCP, DNS, TLS, CDN, WAF, telemetry, logs, metrics, traces, and SLO.

For each term:

1. define it in plain language before or at first use;
2. explain its purpose—not only the expanded acronym;
3. distinguish it from nearby concepts students may confuse;
4. show where it sits in a diagram or concrete workflow;
5. give one small example and one common misconception; and
6. link to a canonical glossary or supplementary explanation.

Do not make every later use verbose. Teach once carefully, reinforce briefly,
and preserve a navigable reference.

### 2. Audit prerequisite order

- Confirm that every notebook relies only on concepts introduced earlier or
  explicitly teaches the missing prerequisite.
- Check notebooks as standalone references as well as in lecture order.
- Add “you should already know” and “new in this notebook” boxes where useful.
- Verify that Lecture 3 does not retroactively explain essential behavior that
  confused students in Lecture 1.

### 3. Reassess the three-hour live route

- Mark the true live core, guided practice, independent practice, and extension
  material for each lecture.
- Ensure the advertised minute estimates are realistic.
- Preserve the long-form notebooks as references without implying every cell
  must be lectured live.
- Identify natural breakpoints if Lecture 3 must span multiple meetings.

### 4. Perform an editorial consistency pass

- Use one term consistently for each concept and call out genuine synonyms.
- Expand acronyms on first use.
- Correct spelling, grammar, duplicated prose, stale notebook numbers, links,
  and headings.
- Check that definitions are accurate without becoming circular.
- Ensure every diagram is introduced, interpreted, and accessible in prose.
- Ensure tables are readable in VS Code's notebook renderer.
- Keep examples varied across mathematics, science, and engineering.

### 5. Recheck the instructional arc

Each notebook should contain orientation, objectives, motivation, definitions,
worked examples, professional practice, guided and independent exercises,
common failures/debugging, retrieval practice, a takeaway, and further reading.
The code should progress from observation to explanation to modification rather
than presenting unexplained finished solutions.

### 6. Recheck professional and scientific practice

- Units, data provenance, assumptions, missingness, leakage, uncertainty, and
  scientific validity should be explicit where relevant.
- Type hints, NumPy docstrings, exceptions, resource ownership, safe paths,
  validation, tests, and observability should be demonstrated consistently.
- Separate “the code ran,” “the software contract holds,” and “the scientific
  conclusion is valid.”
- Maintain cross-platform and offline core behavior.

### 7. Resolve the Lecture 3 roadmap conflict

The Lecture 3 README still lists planned notebooks 08–11 for deeper NumPy,
pandas, feature matrices, and a capstone. This conflicts with the newer decision
that notebook 07 is the final Part I synthesis.

During the second pass, choose deliberately among:

- remove those planned rows because notebook 03 already supplies the Part I
  introduction;
- move advanced NumPy/pandas material into Part II; or
- retain it as optional supplementary practice outside the numbered Part I
  sequence.

Do not append those notebooks after the end-to-end synthesis without revisiting
the Part I narrative.

### 8. Publish the settled Part I structure

After the review:

- add the Part I title and purpose to the main README;
- update lecture names and roadmaps;
- create a student-facing Part I landing page or glossary;
- map Part I outcomes into the syllabus;
- state clearly what is live, assigned, optional, or reference material; and
- rerun the full CI-equivalent validation before declaring Part I complete.

## Questions intentionally left for the next session

- Is **Foundations of Professional Data Science Systems** the final Part I
  title?
- Should the broad current Lecture 3 remain one numbered lecture directory or
  be divided across several weekly lectures?
- Where should advanced NumPy and pandas depth live after the end-to-end
  synthesis?
- Should the canonical glossary be one student-facing document, notebook-local
  callouts backed by an index, or both?
- What is the conceptual opening of Part II: mathematical foundations,
  statistical learning, the supervised-learning workflow, or another arc?
- Which Part I artifacts become graded preparation, exercises, or assignments?

## Suggested resume instruction

Use this when work begins again:

> Resume the Part I second pass from `notes/part-i-handoff.md`. Start with the
> terminology and prerequisite-order audit. Preserve notebook 07 as the final
> Part I synthesis, and identify the smallest coherent changes before designing
> Part II.

# Tests as executable course material

The test suite protects the repository and demonstrates professional Python
development. Tests are intended to be read alongside the package source.

## Run the suite

From the repository root:

```text
uv run python scripts/setup_course.py
uv run pytest
```

Useful variations are:

```text
uv run pytest -q                              # compact output
uv run pytest -v                              # show every test name
uv run pytest tests/test_records.py           # run one file
uv run pytest tests/test_records.py::test_student_record_normalizes_name
uv run pytest -k "score"                      # run tests matching a name
uv run pytest -x                              # stop after the first failure
```

## How to read a test

```python
def test_student_record_normalizes_name() -> None:
    # Arrange and act
    record = StudentRecord("  grace   hopper ", 98)

    # Assert
    assert record.name == "Grace Hopper"
```

The function name states the behavior. The example constructs an object, then
checks an observable result. This pattern is often called
**Arrange–Act–Assert**. Arrange and Act may share one line when the example is
simple.

## What a failure means

A failed test is evidence that observed behavior differs from an expectation.
It does not automatically tell us whether the code or the expectation is wrong.
Read:

1. the failing test's name;
2. the values pytest reports;
3. the lowest relevant lines in the traceback; and
4. the source contract the test is intended to represent.

Avoid changing an assertion merely to make the suite green. First decide which
behavior is correct.

## Test scope in this repository

`test_records.py` and `test_metrics.py` contain focused **unit tests** for
`rice_dsm`. They show normal cases, boundaries, invalid inputs, exceptions,
immutability, one-pass iterables, numerical properties, metamorphic relations,
and executable docstring examples.

`test_knowledge_graph.py` combines unit and **integration tests**. It checks
domain-object invariants, then crosses JSON, CSV, graph, and command-line
boundaries. A test's category follows the boundary it exercises, not the name
of the file containing it.

`test_repository.py` protects the instructional structure. It validates every
notebook, checks the selected kernel, and confirms that essential entry points
exist. These tests prevent accidental repository changes from silently making
student instructions unreproducible.

`test_course_setup.py` checks the project-owned source-path registration, a
fresh import from outside the repository, and the named kernel's interpreter.
It includes the macOS hidden-file condition that originally caused the course
package import to fail.

`test_notebook_execution.py` starts the **Rice DSM** kernel and executes every
notebook from its first cell through its last. This catches missing imports,
stale filenames, bad working-directory assumptions, undefined names, and cells
that only work after an undocumented out-of-order execution.

The `*_teaching.py` files are **contract tests** for the curriculum. They make
important instructional promises—such as cross-platform paths, annotated
examples, and required conceptual distinctions—reviewable and executable.

The GitHub Actions workflow provides **continuous integration** rather than a
new kind of test. It rebuilds the locked environment and runs formatting,
packaging, and test checks on Linux, macOS, and Windows. Separate workflows use
the verified revision to demonstrate continuous deployment of the bounded
course site and continuous delivery of an approved, checksummed course release.
Those publication paths do not turn deployment into another test category.

## Several taxonomies coexist

Test vocabulary answers different questions:

- **Scope:** unit, component, integration, system, or end-to-end.
- **Purpose:** smoke, acceptance, regression, performance, or security.
- **Oracle strategy:** example, mathematical property, metamorphic relation,
  differential comparison, snapshot, golden file, or doctest.
- **Test construction:** parametrized examples, generated/property-based
  cases, fuzzing, or mutation analysis of the suite.

A single case can occupy several categories. A CLI regression test may also be
an end-to-end, acceptance, and snapshot test. Use the labels to communicate
risk and cost, not to force every test into one box.

## Core testing ideas

Read
[`02-testing-and-automation.ipynb`](../notebooks/lecture-03-projects-packages-testing/02-testing-and-automation.ipynb)
for the complete lesson, including fixtures, monkeypatching, mocks, data and ML
testing, flaky-test response, CI/CD, artifacts, approvals, monitoring, and
rollback.

### One behavior per test

A narrow test name makes failure informative. Several assertions are reasonable
when they describe one returned object or one coherent behavior.

### Boundaries deserve examples

For a score constrained to the closed interval `[0, 100]`, test `0` and `100`,
not only a typical value such as `85`. Also test values just outside the valid
range.

### Exceptions are part of the interface

Use `pytest.raises` when invalid input is expected to produce an exception:

```python
with pytest.raises(ValueError, match="must not be empty"):
    StudentRecord("   ", 80)
```

The test checks both the exception type and a stable part of its message.

### Parametrization separates examples from behavior

`@pytest.mark.parametrize` runs one test body with several inputs. It is useful
when the behavior is identical across boundary or invalid cases.

### Test observable behavior

Prefer public results over internal implementation details. A refactor should
not break tests when the public contract remains unchanged.

## Red–green–refactor

An incremental development loop is:

1. **Red:** write a small test describing missing behavior and observe it fail.
2. **Green:** implement the simplest clear change that makes it pass.
3. **Refactor:** improve structure while keeping all tests green.

Actually observing the red state matters: a test that passes before the feature
exists may not test what its author believes.

## Student exercise

Add a test for one new behavior before changing package code. Run only that test
and observe the failure. Implement the behavior, rerun the focused test, and
then run the full suite to check for regressions.

Good first examples include adding `median` to `summarize_scores` or adding a
letter-grade property to `StudentRecord`. State boundary behavior before writing
the implementation.

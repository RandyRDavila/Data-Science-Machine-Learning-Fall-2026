# Teaching Notebook Standard

This document defines the instructional standard for CMOR 438 / INDE 577
notebooks. A notebook should prepare students to reason about unfamiliar data
and code in an industry setting, not merely reproduce syntax demonstrated by an
instructor.

The standard will evolve with the course. A notebook opts into the current
automated checks by setting `metadata.rice_dsm.teaching_standard` to `1`.

## The student promise

Every standard-conforming notebook should tell students:

1. why the topic matters;
2. what they will be able to do;
3. how the central mechanism works;
4. how that mechanism fails or surprises people;
5. how to apply it to a realistic problem; and
6. how to verify their own understanding.

## Course identity: AI for science and mathematics

The notebooks should feel like preparation for scientific computing and modern
machine learning, even while teaching elementary Python. The recurring rhythm
is:

```text
scientific question
    → mathematical object
    → Python representation
    → computational experiment
    → invariant or test
    → interpretation
```

Use experiments, samples, measurements, graphs, vectors, transformations,
model scores, and uncertainty as recurring contexts. Make quantities, units,
dimensions, assumptions, and invariants explicit. When useful, place the
mathematical notation beside its Python representation so students learn to
move between the two.

The scientific theme must clarify rather than decorate. Do not invoke “AI” when
an example is only arithmetic, imply that a model score is certainty, or bury a
Python concept beneath unexplained domain terminology. Standard-library Python
comes first; NumPy, pandas, visualization, and machine-learning libraries enter
only after the underlying representation is understood.

## Dual professional lens

Every notebook must develop both data-science judgment and software-engineering
discipline. Include a section named **Professional practice** that makes the two
lenses explicit:

| Data scientist asks | Software engineer asks |
| --- | --- |
| What does this variable represent? | What interface and type represent it? |
| How was the observation produced? | Where is provenance recorded? |
| What assumptions make the analysis valid? | Where are those assumptions checked? |
| Could preprocessing leak information? | Which boundary owns the transformation? |
| How uncertain is this result? | Is the computation deterministic and testable? |
| Which metric matches the scientific cost? | How are behavior and edge cases specified? |

Do not postpone engineering until a deployment lecture. Students should see
clear naming, boundary validation, assertions, tests, version control,
dependency discipline, code review, and continuous integration accumulate from
the first week. Likewise, engineering machinery must serve scientific validity;
well-tested leakage is still leakage.

## Required instructional arc

### 1. Orientation

Start with a descriptive title, the notebook's place in the lecture, estimated
time, prerequisites, and a short explanation of how to use the notebook. Mark
sections as **Core**, **Practice**, or **Extension** when the complete reference
is longer than the live class route.

### 2. Observable learning objectives

Use actions that can be demonstrated: explain, predict, implement, diagnose,
compare, select, or justify. Avoid objectives such as “understand Python.”

### 3. Why this matters in industry

Motivate the lesson with an authentic data-science or machine-learning concern:
schema drift, dirty identifiers, reproducibility, memory use, interface design,
testing, leakage, deployment, or collaboration. Avoid artificial examples when
a small realistic example is equally clear.

### 4. Conceptual model before convenience syntax

Introduce each major idea in this order:

1. a plain-language mental model;
2. the smallest useful example;
3. a prediction or tracing question;
4. the observed result and explanation; and
5. a failure mode, tradeoff, or boundary case.

Students should encounter the reason for a construct before an exhaustive list
of its methods.

### 5. One coherent worked example

Use a single scenario across multiple sections so the notebook accumulates into
a recognizable workflow. Preserve raw input, validate at boundaries, separate
calculation from presentation, choose explicit names, and use assertions to
make important expectations executable.

Whenever an example represents a scientific quantity or model output, state
its domain and interpretation. A value constrained to `[0, 1]` still requires a
decision threshold and does not become a calibrated probability merely because
code names it `probability`.

### 6. A practice ladder

Include all three levels:

- **Guided practice:** scaffold the reasoning and identify the next step.
- **Independent practice:** state behavior and checks without prescribing the
  implementation.
- **Extension:** introduce ambiguity, a tradeoff, or a design decision with more
  than one defensible answer.

Exercises must include success criteria. A provided solution should explain a
decision, not only display finished code.

### 7. Debugging and professional judgment

Include a repeatable diagnostic procedure and common failure modes. Explicitly
distinguish language guarantees from local conventions. Discuss when *not* to
use the featured technique and name assumptions that would need confirmation in
production.

### 8. Close the loop

End with retrieval questions, a concise takeaway, the connection to the next
notebook, and links to authoritative documentation. Retrieval questions should
be answerable without executing code.

## Code-cell requirements

- The notebook executes from top to bottom in a fresh **Rice DSM** kernel.
- Examples are deterministic and do not require network access.
- Every imported name is introduced where it first appears.
- Variables use meaningful domain names rather than unexplained `x`, `y`, and
  `foo`.
- Important results are checked with assertions, not only displayed.
- Deliberate errors are shown without breaking full-notebook execution.
- Type hints, docstrings, and validation appear when they improve the interface;
  they are not added as decoration.
- Examples do not normalize, discard, or silently impute data without naming
  that policy.

## Public Python interface standard

Nontrivial reusable functions, classes, and methods use **NumPy-style
docstrings**. PEP 257 supplies the baseline docstring conventions; NumPy style
adds a predictable structure familiar across scientific Python. Use only the
sections that add information, typically `Parameters`, `Returns` or `Yields`,
`Raises`, `Notes`, and `Examples`. A one-line docstring remains appropriate for
a genuinely obvious local helper.

Type annotations and docstrings are complementary. Annotations state the
machine-readable interface for editors and static checkers. Docstrings explain
semantics that types do not capture: units, shapes, ordering, valid intervals,
mutation, calibration assumptions, and numerical policy. Runtime validation
enforces important boundary properties because Python does not enforce type
annotations at runtime.

Exceptions are part of the public contract. Raise a specific built-in or custom
exception when a function cannot honor its return contract, document
caller-relevant failures in `Raises`, and write an actionable message naming the
parameter and expected domain. Library code should not print an error or return
an ambiguous sentinel when failure requires caller action. Catch errors only at
a layer that can recover or add useful context; preserve causes with exception
chaining when translating an error.

## Notebook-writing conventions

- Use short paragraphs and define a term before relying on it.
- Do not use color alone to communicate meaning.
- Give every diagram a textual explanation.
- Use paths and commands that work in PowerShell, macOS, and Linux.
- Prefer standard-library examples before introducing a third-party dependency.
- Link to official Python, PyPA, NumPy, pandas, scikit-learn, Jupyter, or VS Code
  documentation for reference material.
- Avoid presenting a personal or team convention as a universal rule.

## Review rubric

Score each category from 0 to 2 before marking a notebook ready.

| Category | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Purpose | unclear | topic stated | authentic motivation and scope |
| Mental model | syntax only | partial explanation | mechanism and boundaries explained |
| Examples | toy or disconnected | coherent but narrow | realistic, cumulative, and verified |
| Practice | absent | one exercise type | guided, independent, and extension |
| Failure modes | absent | warnings listed | students diagnose and explain failures |
| Professional judgment | absent | conventions shown | tradeoffs and assumptions discussed |
| Reproducibility | hidden state | mostly linear | fresh top-to-bottom execution tested |
| Closure | abrupt | summary present | retrieval, takeaway, next step, references |

A release-ready notebook should score at least 14 of 16, with no zero in
reproducibility, mental model, or practice.

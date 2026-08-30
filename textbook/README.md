# Data Science and Machine Learning

*A Systems Approach*

This directory contains the LaTeX source for a developing graduate text. The
book studies data science and machine learning as the construction of
evidence-bearing software systems: mathematical and statistical claims must
survive representation, implementation, evaluation, deployment, and revision.

The prose carries the definitions, arguments, and compact examples. Lecture
notebooks act as computational laboratories; the `rice_dsm` package contains
reusable implementations; tests preserve executable contracts. The book is
therefore the organizing artifact for the repository rather than a transcript
of its lectures.

## Build

From this directory:

```bash
make
```

Or from the repository root:

```bash
make -C textbook
```

The final PDF is written to:

```text
output/pdf/data-science-machine-learning-textbook.pdf
```

Temporary LaTeX files remain under `textbook/build/` and are ignored by Git.

## Source map

```text
textbook.tex                book structure and metadata
style/rice-dsm-book.sty     typography, colors, boxes, code, headers
frontmatter/                preface and how to use the book
chapters/                   numbered textbook chapters
appendices/                 setup, Git/GitHub lessons, and glossary
```

## Editorial status

Part I is a complete graduate-course draft with a connected systems argument,
worked examples, exercises, appendices, a glossary, and executable companions.
It is ready for classroom review but remains open to corrections, citations,
additional figures, solutions, and revisions from use. Later parts should be
added only after their mathematical and computational arc is designed.

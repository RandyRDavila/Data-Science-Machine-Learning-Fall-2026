# Lecture 2 native-file data

This directory contains a small, course-authored scientific knowledge graph for
`03-native-data-files.ipynb`.

## Files

- `scientific_concepts.json` stores graph metadata and 20 typed concept nodes.
- `scientific_relationships.csv` stores 25 directed, labeled relationships.

The split is intentional: JSON naturally represents nested node records and
alias lists, while CSV is convenient for uniformly shaped edge records. The
notebook treats both files as untrusted input, validates their schemas, and
combines them only after constructing domain objects.

## Scope and provenance

This teaching dataset was written for CMOR 438 / INDE 577 in August 2026. Its
concise descriptions, relationship directions, confidence values, and evidence
notes are pedagogical choices. They are not an authoritative ontology,
literature review, or benchmark dataset. `confidence` records the course
author's strength of assertion for the teaching graph; it is not an empirical
probability.

If this graph were used for research, every relationship would also need
durable source identifiers, curation policy, version history, and expert
review. Those omissions are discussed explicitly in the notebook rather than
hidden from students.

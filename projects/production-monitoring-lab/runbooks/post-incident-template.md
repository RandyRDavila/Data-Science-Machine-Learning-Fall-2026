# Post-incident review: concise template

## Summary

- UTC start and end:
- Client-visible symptom:
- Impact and scope:
- Detection source:
- Mitigation:

## Timeline

Record observations, decisions, actions, and their owners in UTC order. Separate
facts known at the time from later conclusions.

## Technical cause

State the failed contract and the mechanism that produced the symptom. Avoid
assigning the cause to a person.

## Evidence

- Metric or alert that established scope:
- Trace that localized the operation:
- Structured event that explained the failure:
- Data/model/outcome evidence:
- Competing hypothesis rejected:

## Recovery and verification

Explain the reversible mitigation, permanent repair, and evidence that the
original client symptom no longer occurs.

## Follow-up actions

| Action | Owner | Due date | Verification |
| --- | --- | --- | --- |
| | | | |

Include changes to code, tests, telemetry, runbooks, ownership, or policy. “Be
more careful” is not a verifiable action.

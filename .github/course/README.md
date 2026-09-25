# Course coordination configuration

This directory contains public, reviewable input to the course-coordination
automation. It must never contain grades, student IDs, legal names, email
addresses, accommodations, or private course information.

## `coordination.json`

Automation is committed with `"enabled": false`. Before enabling it, the
instructor adds only the GitHub handles of students who opted into the public
workflow and verifies the configuration through a pull request.

Participant records use this shape:

```json
{
  "login": "github-handle",
  "active": true,
  "reviewer": true,
  "guild": "trees",
  "product_team": null
}
```

`guild` represents temporary shared-platform work. `product_team` represents a
later final-project team; the two should not be conflated. Reviewer selection
excludes the pull-request author, linked-issue collaborators, and members of the
same product team when that field is present.

## `tasks.json`

The task manifest defines the initial platform backlog. Creating issues is a
maintainer-triggered, dry-run-first operation. Editing the manifest does not
silently create, assign, or grade work.

Complexity is a planning signal, not a grade or a promise of equal difficulty.
The instructor reviews task scope and dependencies before opening each cohort.
The issue remains the authoritative record of any later scope adjustment.

## Automation boundary

Coordination workflows may assign issues, request reviews, apply labels, and
maintain an operational digest. They may not:

- execute code from a fork with write credentials;
- merge a pull request;
- publish grades or private feedback;
- infer contribution quality from activity counts; or
- expose repository secrets to make a student check pass.

Every automated decision must leave a visible issue or pull-request event and
permit maintainer correction.

The common `course: work` label supports one GitHub Project auto-add rule for
both generated tasks and relevant pull requests. Project fields and views may
describe public workflow state and workload, but must not contain grades,
private feedback, or inferred measures of contribution quality.

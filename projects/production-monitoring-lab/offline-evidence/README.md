# Offline incident evidence

This committed evidence bundle is the accessibility fallback for students who
cannot run Docker locally. It represents two equal-sized windows from the
battery-risk service: a healthy reference window and a later window in which
HTTP availability and latency remain acceptable while prediction semantics
change.

The bundle contains:

- `case-manifest.json`: evidence identity, capture windows, and limitations;
- `client-summary.json`: client-visible status, latency, and decisions;
- `prometheus-snapshot.txt`: selected aggregate metric samples;
- `application-events.jsonl`: representative structured events;
- `trace.json`: representative spans from the changed window; and
- `quality-summary.json`: delayed outcome evidence.

Validate and summarize the files from the repository root:

```text
uv run python projects/production-monitoring-lab/scripts/summarize_offline_evidence.py
```

Then complete the same incident record and post-incident template used by the
live route. Cite filenames and fields instead of screenshots. The bundle is
small and deliberately selected; it cannot establish service startup,
collector behavior, alert timing, live mitigation, or recovery. Record those
limitations rather than pretending the offline route exercised them.

Do not begin with the scenario label in the event file. First state the client
symptom, compare aggregate windows, and form at least two hypotheses. Then use
the trace and structured event to distinguish feature semantics from ordinary
service failure.

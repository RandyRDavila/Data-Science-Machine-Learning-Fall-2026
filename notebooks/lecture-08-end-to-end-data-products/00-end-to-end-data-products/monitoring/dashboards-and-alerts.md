# Monitoring contract

The primary dashboard connects release and user experience to the service:

| Layer | Signals |
| --- | --- |
| Browser/RUM | page load, API duration/failure, Web Vitals, JS errors, device/browser class, release |
| Edge | requests, cache hit ratio, TLS/DNS failures, status and latency |
| API | request rate, error rate, duration distribution, saturation, release |
| Database | pool use, query latency, errors, locks, storage and replication health |
| Data/ML | freshness, schema failures, null/range violations, drift, model version and outcomes |
| Delivery | artifact digest, deployment event, migration, canary traffic and rollback |

Every client and server event uses a route template, release identifier, outcome,
and trace/request correlation where available. It excludes credentials, request
bodies, raw scientific records, full query-bearing URLs, and direct personal
identifiers.

Alert on user-centered SLO burn, sustained error/latency change, freshness
breach, queue age, or dependency saturation. Each alert links to a runbook and
owner. Do not page on every log line.

Investigation order:

1. Identify client release, approximate time, route, and request/trace ID.
2. Check RUM/synthetic impact by browser, device class, region, and release.
3. Follow the trace through edge, API, database, and queue.
4. Use metrics to determine scope and structured logs for reviewed details.
5. Mitigate, preserve evidence, and add a regression test after root cause.

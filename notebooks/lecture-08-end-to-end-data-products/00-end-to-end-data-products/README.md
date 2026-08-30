# Companion vertical-slice project

This directory maps the executable `rice_dsm.data_product` example to the
artifacts a production team commonly owns. It is a teaching reference, not a
turnkey production deployment.

Here an HTTP API—application programming interface—is the documented contract
through which a browser, instrument, or other program sends a request and
receives a response. It is separate from the database and from the frontend.
See [`What is an API?`](../../../supplementary-materials/computing-foundations/07-what-is-an-api.md)
for the zero-assumption introduction.

```text
00-end-to-end-data-products/
├── backend/app.py                    # Uvicorn import target and runtime config
├── browser/
│   ├── playwright.config.ts          # desktop/mobile browser projects
│   └── critical-journey.spec.ts      # illustrative deployed browser journey
├── deployment/
│   ├── Containerfile                 # immutable backend image example
│   ├── compose.yaml                  # local multi-process topology
│   └── production-cicd.example.yml   # build-once/promote workflow sketch
└── monitoring/
    ├── client-event.schema.json      # bounded, privacy-reviewed RUM contract
    ├── dashboards-and-alerts.md      # signals, SLOs, and investigation path
    └── otel-collector.example.yaml   # telemetry pipeline shape
```

Canonical application code lives in
`src/rice_dsm/data_product.py`; canonical frontend HTML/CSS/JavaScript lives in
`src/rice_dsm/static/dashboard.html`; package tests live in
`tests/test_data_product.py`. Deployment assets refer to those sources instead
of copying their behavior.

The notebook uses FastAPI `TestClient` and never opens a port. The optional
local server target is:

```bash
uv run uvicorn app:app --app-dir notebooks/lecture-08-end-to-end-data-products/00-end-to-end-data-products/backend
```

That command is for deliberate local exploration. It is not run by notebook
execution or CI. Production still requires a managed database, authentication
and authorization, TLS/edge configuration, secrets, migrations, telemetry,
capacity policy, backups, and an owned incident process.

## Diagram legend

- Solid arrows are request or data flow.
- Dotted arrows are telemetry.
- Parentheses denote stateful services.
- Files ending in `.example.*` contain placeholders and must not be deployed
  without review.

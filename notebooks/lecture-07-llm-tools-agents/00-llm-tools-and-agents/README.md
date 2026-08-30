# LLM tools and agents: companion reference

This directory turns notebook 06's architecture into reviewable artifacts. It
is a teaching reference, not a deployment-ready autonomous agent.

An API—application programming interface—is a documented way for one program to
request data or behavior from another. In this lesson a hosted model API accepts
an authenticated request from Python, runs inference on provider-operated
computers, and returns response data. The installed client library only helps
construct that request; it is not the hosted model. See
[`What is an API?`](../../../supplementary-materials/computing-foundations/07-what-is-an-api.md)
for the complete introduction.

## The boundary that matters

The language model may classify, summarize, draft, or propose a typed action.
Ordinary software validates that proposal. Policy determines whether it is
allowed. A named person approves consequential work. A durable orchestrator
owns time, retries, idempotency, execution state, and recovery.

```text
untrusted request/context
        ↓
model proposes typed data
        ↓
schema + semantic checks + policy
        ↓
human approval when required
        ↓
small allowlisted adapter
        ↓
scheduler/service performs and records the action
```

The model never receives a general shell, arbitrary file access, ambient cloud
credentials, or direct ownership of the training scheduler in this example.

## Artifact map

| Path | Purpose |
| --- | --- |
| `.env.example` | Names configuration variables without containing credentials |
| `prompts/docstring-review.md` | Versioned, testable instructions and data boundary |
| `schemas/training-run-proposal.schema.json` | Machine-readable output contract |
| `policies/tool-policy.yaml` | Human-readable least-privilege policy example |
| `evals/cases.jsonl` | Small versioned evaluation seed set |
| `orchestration/training_workflow.py` | Offline proposal → policy → approval → scheduling example |

## Trying a hosted model safely

The core notebook makes no network request and needs no key. For an optional
provider lab, copy `.env.example` to an ignored `.env`, enter the variables for
the provider you selected, and load them only into the process that makes the
request. Never place a real key in a notebook, source file, screenshot, issue,
chat, log, or committed environment file. Prefer a managed secret store and
short-lived workload identity in production.

Free chat access, API free tiers, and downloadable model weights are different
things. Confirm current quotas, billing, privacy terms, model license, and
hardware requirements before use. The course architecture remains the same for
OpenAI, Claude, Grok, Kimi, Gemini, Llama, Qwen, Gemma, Mistral, or another
approved model; only a narrow model-gateway adapter should change.

## Run the offline workflow

From the repository root in VS Code's integrated terminal:

```bash
uv run python notebooks/lecture-07-llm-tools-agents/00-llm-tools-and-agents/orchestration/training_workflow.py
```

It records one approved in-memory job and deliberately performs no training,
cloud operation, API call, or file mutation.

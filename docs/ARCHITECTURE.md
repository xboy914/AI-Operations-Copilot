# Architecture

AI Operations Copilot is a human-controlled agent execution platform.

## Request path

1. FastAPI authenticates the operator and enforces RBAC.
2. The configured planner selects one registered tool.
3. LangGraph checkpoints execution before risky tools.
4. Approvers inspect arguments and approve or reject the action.
5. The tool runner applies bounded retries only to explicit transient failures.
6. Audit events, live run projections, SSE updates, and Prometheus metrics expose the outcome.

## Components

- **API:** FastAPI contracts, JWT authentication, RBAC, SSE, and metrics.
- **Agent runtime:** LangGraph state machine and interrupt/resume semantics.
- **Planner:** deterministic offline mode or OpenAI-compatible providers including Ollama.
- **Tools:** risk-labelled local tools and transport-neutral MCP adapters.
- **Data:** PostgreSQL for workflows and audit records; Redis is prepared for durable event transport.
- **Workspace:** Next.js approval inbox and live execution timeline.

## Trust boundaries

Planner output is untrusted. Tool names are validated against the registry, arguments must be JSON
objects, and side-effect metadata cannot bypass the approval node. The execution layer retries only
`RetryableToolError`; validation, policy, and programming failures fail immediately.

## Current durability

Workflow and audit data are persisted in PostgreSQL. LangGraph checkpoints and live projections are
process-local in v1.0; a production multi-replica deployment should replace them with durable
PostgreSQL/Redis-backed implementations.

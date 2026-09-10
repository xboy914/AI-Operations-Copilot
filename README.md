# AI Operations Copilot

A production-oriented control plane for agentic business workflows with human approval, role-aware actions, and immutable audit trails.

## Foundation milestone

- Explicit workflow state machine with guarded transitions
- PostgreSQL models for workflow runs, approvals, and audit events
- FastAPI contracts and interactive documentation
- Black-and-gold responsive Next.js operations workspace
- PostgreSQL, Redis, API, and web Docker Compose stack
- Persistent PostgreSQL workflow commands and audit events
- JWT authentication with operator, approver, and admin RBAC
- Alembic database migrations
- LangGraph execution with checkpointed human approval interrupts
- Risk-aware tool registry that auto-runs read-only tools and gates side effects
- OpenAI/Ollama-compatible intelligent tool planning
- MCP transport adapters with explicit approval policy metadata
- Approval inbox with protected approve/reject actions
- Live authenticated agent-run event stream
- Prometheus metrics for runs, latency, tool outcomes, and retries
- Exponential retry policy restricted to explicit transient failures
- Deterministic planner and approval-policy evaluation suite
- Backend and frontend CI quality gates

## Run

```bash
cp .env.example .env
docker compose up --build
```

- Workspace: http://localhost:3000
- API docs: http://localhost:8000/docs

## Roadmap

- E2E tests, deployment hardening, and v1.0 release

## License

MIT

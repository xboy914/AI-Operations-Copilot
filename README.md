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
- Backend and frontend CI quality gates

## Run

```bash
cp .env.example .env
docker compose up --build
```

- Workspace: http://localhost:3000
- API docs: http://localhost:8000/docs

## Roadmap

- Human approval inbox UI
- Live execution events
- Observability, E2E tests, and v1.0 release

## License

MIT

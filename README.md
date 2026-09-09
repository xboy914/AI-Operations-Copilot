# AI Operations Copilot

A production-oriented control plane for agentic business workflows with human approval, role-aware actions, and immutable audit trails.

## Foundation milestone

- Explicit workflow state machine with guarded transitions
- PostgreSQL models for workflow runs, approvals, and audit events
- FastAPI contracts and interactive documentation
- Black-and-gold responsive Next.js operations workspace
- PostgreSQL, Redis, API, and web Docker Compose stack
- Backend and frontend CI quality gates

## Run

```bash
cp .env.example .env
docker compose up --build
```

- Workspace: http://localhost:3000
- API docs: http://localhost:8000/docs

## Roadmap

- JWT authentication and RBAC enforcement
- Persistent workflow commands and audit service
- LangGraph orchestration
- MCP tool registry
- Human approval inbox
- Live execution events
- Observability, E2E tests, and v1.0 release

## License

MIT

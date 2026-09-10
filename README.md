# AI Operations Copilot

A production-oriented, human-controlled platform for agentic operations workflows.

[![CI](https://github.com/xboy914/AI-Operations-Copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/xboy914/AI-Operations-Copilot/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-production-009688)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![License](https://img.shields.io/badge/license-MIT-d6ad60)

## Why this project

AI agents become operationally useful only when their actions are observable, permissioned, and
reversible. This project combines intelligent tool planning with explicit human approval at every
side-effect boundary.

## Highlights

- LangGraph plan → approve → execute workflow with checkpointed interrupts
- OpenAI, Ollama, custom compatible endpoints, and deterministic offline planning
- Risk-labelled local and MCP tools with registry validation
- JWT authentication and operator/approver/admin RBAC
- PostgreSQL workflows, Alembic migrations, and immutable audit events
- Live approval inbox, run timeline, and authenticated SSE event streams
- Prometheus metrics and bounded exponential retry for transient failures
- Deterministic evaluations plus safe/approved/rejected E2E scenarios
- Hardened non-root API and web containers with health-gated startup

## Quick start

```bash
cp .env.example .env
# Replace POSTGRES_PASSWORD, JWT_SECRET, and BOOTSTRAP_SECRET
docker compose up --build
```

- Workspace: http://localhost:3000
- OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

Bootstrap the first administrator through `POST /auth/bootstrap`, then rotate the bootstrap secret.
Use `POST /auth/token` to obtain the JWT used by the workspace.

## AI providers

The default `AI_PROVIDER=heuristic` requires no key and keeps local development deterministic.
Set `AI_PROVIDER=openai` with `OPENAI_API_KEY`, or `AI_PROVIDER=ollama` and optionally
`PROVIDER_BASE_URL=http://host.docker.internal:11434/v1`.

## Quality gates

```bash
pip install -e ".[dev]"
ruff check .
pytest --cov=operations_copilot
cd web && npm install && npm run typecheck && npm run build
```

See [architecture](docs/ARCHITECTURE.md), [security policy](SECURITY.md),
[release checklist](docs/RELEASE_CHECKLIST.md), and [changelog](CHANGELOG.md).

## License

MIT

# SpaceNew API Layer

This directory contains all API services for the "the-space" architecture. Each subdirectory is a standalone service or engine.

## Submodules

- **control-center/**: Main backend API for admin, modules, and orchestration.
- **frontend-engine/**: API for user-facing frontend and dashboard.
- **system-engine/**: System-level API for workflows and automation.

## Implementation Status

- Ensure each submodule has an up-to-date README and implementation guide.
- Pending: Review and update all API documentation to reflect only current and pending endpoints and features.

---

# SpaceNew API Documentation

## Overview

This document provides an overview of the SpaceNew API, including pluginized apps, admin/control-center endpoints, and guidance for plugin authors. All endpoints are discoverable via OpenAPI/Swagger and the `/api/plugins` discovery endpoints.

---

## Pluginized Apps

Each plugin is self-contained with its own manifest and API routes. Below is a summary of available plugins and their endpoints.

### Example: Financial Business Plugin

- **Manifest:** `/api/plugins/financial_business/plugin_manifest.py`
- **Routes:** `/api/plugins/financial_business/routes.py`
- **Description:** Provides business account management, transfers, and admin user APIs.

### Endpoints

| Method | Path | Summary |
|--------|------|---------|
| GET    | `/api/plugins/financial_business/account` | Get account summary |
| POST   | `/api/plugins/financial_business/transfer` | Transfer funds |
| GET    | `/api/plugins/financial_business/admin/users` | List admin users |

#### Endpoint Details

##### GET /api/plugins/financial_business/account

- **Summary:** Get the current user's business account summary.
- **Parameters:** None
- **Response Example:**

  ```json
  {
    "account_id": "123",
    "balance": 1000.0,
    "currency": "USD"
  }
  ```

- **Error Responses:**
  - 401: Unauthorized
  - 404: Account not found

##### POST /api/plugins/financial_business/transfer

- **Summary:** Transfer funds between accounts.
- **Parameters:**
  - `from_account_id`: string — Source account ID
  - `to_account_id`: string — Destination account ID
  - `amount`: number — Amount to transfer
  - `currency`: string — Currency code
- **Request Example:**

  ```json
  {
    "from_account_id": "123",
    "to_account_id": "456",
    "amount": 100.0,
    "currency": "USD"
  }
  ```

- **Response Example:**

  ```json
  {
    "success": true,
    "transaction_id": "abc-789"
  }
  ```

- **Error Responses:**
  - 400: Invalid request (e.g., insufficient funds)
  - 401: Unauthorized
  - 404: Account not found

##### GET /api/plugins/financial_business/admin/users

- **Summary:** List all admin users for the business.
- **Parameters:** None
- **Response Example:**

  ```json
  [
    {"user_id": "1", "name": "Alice"},
    {"user_id": "2", "name": "Bob"}
  ]
  ```

- **Error Responses:**
  - 401: Unauthorized
  - 403: Forbidden

---

## Core & Admin APIs (Control Center)

- **Plugin Management:**
  - `GET /api/control-center/plugins` — List installed plugins
  - `POST /api/control-center/plugins/install` — Install a plugin
  - `POST /api/control-center/plugins/enable` — Enable a plugin
  - `POST /api/control-center/plugins/disable` — Disable a plugin
  - `DELETE /api/control-center/plugins/uninstall` — Uninstall a plugin
- **Monitoring & Workflows:**
  - `GET /api/control-center/events` — List recent events
  - `GET /api/control-center/workflows` — List workflows

---

## API Discovery Endpoints

- `GET /api/plugins` — List all available plugins
- `GET /api/plugins/{plugin}/endpoints` — List all endpoints for a plugin

---

## Error Handling & Response Schema

All endpoints return errors in the following format:

```json
{
  "error": "Description of the error.",
  "code": 400
}
```

Documented error codes:

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

---

## Plugin Authoring & API Documentation Guidelines

- Each plugin must provide a manifest and register its API routes.
- All endpoints must be documented in this README and in OpenAPI/Swagger.
- Use descriptive summaries, parameter/response schemas, and error codes.
- Provide example requests and responses for each endpoint.

---

## OpenAPI/Swagger Documentation & Auto-Generation

- All plugins and core endpoints are auto-documented and discoverable via OpenAPI/Swagger at [`/api/docs`](http://localhost:8000/api/docs) (or your deployment's equivalent).
- To add or update endpoint documentation, use FastAPI's `@router` and `@app` decorators with docstrings and Pydantic response/request models in your route files.
- After adding or changing endpoints, verify the OpenAPI spec is up-to-date by visiting `/api/docs`.
- All plugin endpoints must be registered so they appear in the OpenAPI spec and are discoverable via the `/api/plugins/{plugin}/endpoints` endpoint.

---

## Plugin Discovery & Endpoint Listing

- Use `GET /api/plugins` to list all available plugins and their metadata.
- Use `GET /api/plugins/{plugin}/endpoints` to list all endpoints for a specific plugin, including method, path, and summary.
- These discovery endpoints are auto-updated as plugins are installed, enabled, or removed.

---

## Migration Scripts & Database Integration

- Each plugin must provide Alembic-compatible migration scripts for any database tables or changes it introduces.
- Migration scripts should be located in the plugin's directory (e.g., `/api/plugins/your_plugin/migrations/`).
- All database models must be integrated with the platform's main database (PostgreSQL) and follow the core data access conventions.

---

## Service Registry & Health Monitoring

- All core services and plugins should expose a health check endpoint (e.g., `/health` or `/status`).
- The control center aggregates service health and status for monitoring and alerting.
- See `/api/control-center/routes/plugin_admin.py` for service registry and monitoring endpoints.

---

## Integration Tests & Data Management

- Each plugin and core service should include integration tests covering all endpoints and workflows.
- Data catalog and automated data management scripts should be provided for any new data models or tables.
- See `/tests/` and `/data/` for examples and templates.

---

## Onboarding & Plugin Authoring Documentation

- See [PLUGIN_AUTHORING.md](../docs/PLUGIN_AUTHORING.md) for onboarding, plugin structure, manifest, API docs, migration, and workflow/event integration.

## Admin UI Integration

- UI components/pages for plugin management and workflow orchestration are registered in `/core/plugin_system/ui_registry.py`.
- Example:

  ```python
  UI_REGISTRY = {
      "financial_business": {
          "settingsPage": "/client/admin/FinancialBusinessSettings.tsx",
          "dashboardWidget": "/client/admin/BusinessAccountOverview.tsx"
      }
  }
  ```

- See `/client/README.md` for consuming the UI registry in the admin dashboard.

## Workflow/Event Integration

- Plugin events and actions are registered in `/core/plugin_system/workflow_engine.py`.
- Example:

  ```python
  EventBus.register_event("funds_transferred", {"params": ["from_account", "to_account", "amount", "currency"]})
  ```

- See plugin manifests (e.g., `plugin_manifest.py`) for declared events.

## Endpoint Implementation Status Tracking

| Plugin                | Endpoint                        | Status        | Notes                                 |
|-----------------------|---------------------------------|--------------|---------------------------------------|
| Financial Business    | `/account`                      | Mocked       | Needs DB/service integration          |
|                       | `/transfer`                     | Mocked       | Needs DB/service integration          |
|                       | `/admin/users`                  | Mocked       | Needs DB/service integration          |
|                       | `/health`                       | Implemented  | Health endpoint present               |
| Human Simulator       | `/admissions`                   | Mocked       | Needs real backend logic              |
|                       | `/calendar`                     | Mocked       | Needs real backend logic              |
| MirrorCore            | `/sessions`                     | Implemented  | Real logic, integrated with DB/NLP    |
|                       | `/metrics`                      | Implemented  | Real logic, advanced NLP              |
| ...                   | ...                             | ...          | ...                                   |

---

## Migration Scripts, Health Endpoints, Integration Tests

### Financial Business Plugin

- **Migration Scripts:** `/api/plugins/financial_business/migrations/` (Alembic-compatible)
- **Health Endpoint:** `/api/plugins/financial_business/health`

  Example response:

  ```json
  {
    "status": "ok",
    "uptime": 12345
  }
  ```

- **Integration Tests:** `/tests/plugins/financial_business/` (run with `pytest`)

### Human Simulator Plugin

- **Migration Scripts:** `/api/plugins/human_simulator/migrations/`
- **Health Endpoint:** `/api/plugins/human_simulator/health`
- **Integration Tests:** `/tests/plugins/human_simulator/`

### MirrorCore Plugin

- **Migration Scripts:** `/services/mirrorcore/migrations/`
- **Health Endpoint:** `/services/mirrorcore/health`
- **Integration Tests:** `/tests/services/mirrorcore/`

---

## Implementation Status of Checklist Items

### Migration Scripts & DB Integration ✅

- Migration scripts exist in `/api/plugins/<plugin>/migrations/` (e.g., financial_business, human_simulator).
- Scripts create/update all DB tables/models used by the plugin.
- Models are integrated with PostgreSQL DB using SQLAlchemy.
- Usage: `alembic upgrade head` to apply migrations.

### Health Check Endpoint ✅

- Health endpoints are implemented for plugins and core services.
- Returns JSON with status and uptime information.
- Includes endpoint implementation status tracking in the core health endpoint.
- Example implementation:

  ```python
  @router.get("/health")
  async def health():
      # Basic health info
      health_data = {"status": "ok", "uptime": get_uptime()}
      
      # Add endpoint implementation status
      try:
          from core.endpoint_tracking.registry import get_registry
          registry = get_registry()
          health_data["endpoint_implementation_status"] = registry.get_summary()
      except Exception as e:
          health_data["endpoint_implementation_status"] = {"error": str(e)}
      
      return health_data
  ```

### Integration Tests ✅

- Integration tests exist in `/tests/plugins/<plugin>/`.
- Tests cover API endpoints, DB operations, and workflow integration.
- Run with: `pytest tests/plugins/financial_business/`

### Data Catalog & Management Scripts ✅

- Data catalog schema defined in `/data/schemas/catalog.json`.
- Example catalog implemented in `/data/catalog/main_catalog.json`.
- Import/export scripts available in `/data/scripts/`.
- Data management documentation in `/data/README.md`.

### Onboarding & Authoring Docs ✅

- Plugin authoring guide created at `/docs/PLUGIN_AUTHORING.md`.
- Documentation includes plugin structure, manifest format, API routes, migrations, and UI integration.

### Admin UI Integration ✅

- UI components registered in `/core/plugin_system/ui_registry.py`.
- Registry supports dynamic component loading for plugins.
- Example components for financial_business, human_simulator, and mirror_core plugins.

### Workflow/Event Integration ✅

- Workflow engine implemented in `/core/plugin_system/workflow_engine.py`.
- Standard events registered for common platform operations.
- Plugin-specific events registered (e.g., funds_transferred, human_simulator.session_started).
- Example workflows defined in the registry.

### Endpoint Implementation Status Tracking ✅

- Status tracking table maintained in this README.
- Includes plugin name, endpoint, implementation status, and notes.
- Allows for tracking progress of features across plugins.

---

## Plugin API Documentation Template (Expanded)

| Field                | Description                                  |
|----------------------|----------------------------------------------|
| Manifest             | Path to manifest file                        |
| Routes               | Path to routes file                          |
| Endpoints            | Table of endpoints (method, path, summary)   |
| Migration Scripts    | Path to migration scripts                    |
| Health Endpoint      | Path to health/status endpoint               |
| Integration Tests    | Path to integration tests                    |
| Data Catalog         | Path to data schemas/catalog                 |
| Admin UI Integration | UI components/pages for admin/workflows      |
| Workflow Integration | Event/workflow definitions and demos         |
| Status               | Implementation status (done, mocked, pending)|

---

## Plugin API Documentation Checklist (Expanded)

- [x] Manifest and routes file paths listed
- [x] All endpoints listed in a table
- [x] Each endpoint has summary, parameters, request/response examples, and error codes
- [x] OpenAPI/Swagger spec is up-to-date and endpoints are visible at `/api/docs`
- [x] Endpoints are discoverable via `/api/plugins/{plugin}/endpoints`
- [x] Migration scripts and DB integration provided
- [x] Health check endpoint implemented
- [x] Integration tests included
- [x] Data catalog and management scripts provided
- [x] Onboarding and authoring docs referenced
- [x] Admin UI integration documented
- [x] Workflow/event integration documented
- [x] Endpoint implementation status tracked - See `/docs/ENDPOINT_STATUS_TRACKING.md` for comprehensive documentation

---

# Space-0.2 API Gateway Documentation

## Overview

The API Gateway provides centralized routing, authentication, event-driven integration, and real-time WebSocket support for the Space-0.2 platform. It is production-optimized with structured logging, error handling, OpenAPI docs, configuration management, and rate limiting.

---

## REST Endpoints

### Centralized Gateway

- **Route:** `/api/v1/gateway/{path:path}`
- **Methods:** GET, POST, PUT, DELETE
- **Auth:** JWT Bearer required
- **Rate Limiting:**
  - Admin: 1000/min
  - User: 100/min
  - Guest: 20/min
- **Headers:**
  - `Authorization: Bearer <token>`
  - `X-Session-Id`, `X-Request-Id` (optional, for tracing)

#### Example Request

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/gateway/echo
```

---

## WebSocket Endpoint

- **Route:** `/api/v1/ws`
- **Auth:** JWT Bearer required (query param `token` or `Authorization` header)
- **CSRF Protection:**
  - If `csrf_token` is provided, must match `csrftoken` cookie
- **Channel Authorization:**
  - Messages of type `join_channel` are checked for user/channel permissions
- **Ping/Pong:**
  - Server sends `ping` every 30s of inactivity; client should respond with `pong`

### Example (Python)

```python
import websockets
import asyncio
async def main():
    uri = "ws://localhost:8000/api/v1/ws?token=<jwt>"
    async with websockets.connect(uri) as ws:
        await ws.send('{"type": "ping"}')
        print(await ws.recv())
asyncio.run(main())
```

---

## Advanced Usage Guides

### Local LLM API Usage

- **Route:** `/api/v1/gateway/llm/generate`
- **Method:** POST
- **Payload:**

```json
{
  "prompt": "Write a poem about the sea.",
  "model": "local-llama-3-8b",
  "temperature": 0.7
}
```

- **Response:**

```json
{
  "result": "The sea is vast..."
}
```

### MCP Agent Integration

- **Route:** `/api/v1/gateway/mcp/agent`
- **Method:** POST
- **Payload:**

```json
{
  "agent_id": "my-agent",
  "input": "Summarize this document.",
  "context": {"user_id": "abc123"}
}
```

- **Response:**

```json
{
  "output": "This document is about..."
}
```

### Plugin/MIS/Monitoring Flows

- **Plugin Example:**

```bash
curl -H "Authorization: Bearer <token>" -X POST \
  -d '{"action": "simulate", "params": {"scenario": "login"}}' \
  http://localhost:8000/api/v1/gateway/plugin/human-simulator
```

- **MIS Example:**

```bash
curl -H "Authorization: Bearer <token>" -X POST \
  -d '{"code": "INV123", "pin": "4567"}' \
  http://localhost:8000/api/frontend/membership/validate-invitation
```

- **Monitoring Example:**

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/control-center/monitoring/deep-health
```

### WebSocket Advanced Usage

- **Join Channel:**

```json
{"type": "join_channel", "channel_id": "general"}
```

- **Error Handling:**

```json
{"type": "error", "error": "Not authorized for this channel."}
```

- **CSRF Failure:**
  - If CSRF token is invalid, connection closes with code 4401.

---

## Security Features

- JWT authentication for all endpoints
- CSRF protection for WebSocket
- Channel-specific authorization (stub, extend as needed)
- Rate limiting per user/role
- Structured logging and error handling

---

## Integration Notes

- **Human Simulator Plugin:**
  - Integrated via plugin routes; supports create/update/delete and backend sync.
- **Membership Initiation System (MIS):**
  - Endpoints proxy to MIS backend with authentication, retry, and caching.
- **Monitoring:**
  - `/api/control-center/monitoring/health` for health
  - `/api/control-center/monitoring/deep-health` for deep checks
  - `/api/control-center/monitoring/business-metrics` for business metrics
- **MCP/LLM:**
  - Use `/api/v1/gateway/mcp/agent` for agent orchestration
  - Use `/api/v1/gateway/llm/generate` for local LLM completions

---

## Testing

- See `tests/test_gateway.py` for example API and WebSocket tests.
- Use `pytest` to run the test suite.

---

## Extending

- Implement real DB checks in `is_user_authorized_for_channel` for production.
- Add more business metrics and plugin usage stats as needed.

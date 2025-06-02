# Admin Dashboard & Control Center

## How to Run the Admin Dashboard Frontend

1. Navigate to the client directory:

   ```bash
   cd /Users/macbook/Desktop/y2.5 - ReDefination/space-proposed/Space-0.2/client
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Access the dashboard in your browser:
   - [http://localhost:3000/admin](http://localhost:3000/admin) (or as configured)

## Features

- Plugin management (install, enable/disable, uninstall)
- System monitoring (health, metrics, logs)
- Workflow orchestration
- User management

## API Endpoints

- The dashboard consumes endpoints from `/api/control-center/*` and related routes.
- See `api/control_center/` for backend implementation.

---

## Extending/Customizing

- Add new features by extending the React frontend and corresponding FastAPI endpoints.
- For plugin admin, see `/api/control_center/plugins`.
- For system health, see `/api/control_center/monitoring`.

## Advanced Integrations

### MCP (Model Context Protocol)

- Endpoints under `/api/mcp/*` provide tool/agent interoperability using MCP.
- Example endpoints:
  - `POST /api/mcp/context` — Handle MCP context requests
  - `POST /api/mcp/tool-invoke` — Invoke a tool/agent via MCP
  - `POST /api/mcp/context/update` — Update MCP context
- See `api/mcp_adapter.py` for extension and usage.

### mem0 Context Provider

- Endpoints under `/api/context/mem0/*` provide memory/context operations using mem0.
- Example endpoints:
  - `GET /api/context/mem0/memory` — Retrieve user context
  - `POST /api/context/mem0/memory/add` — Add a memory
  - `POST /api/context/mem0/memory/update` — Update a memory
  - `GET /api/context/mem0/memory/search` — Search memories
  - `DELETE /api/context/mem0/memory/clear` — Clear all memories for a user
- See `api/context_providers/mem0_provider.py` for extension and usage.

### Membership Initiation System (MIS)

- Endpoints under `/api/frontend/membership/*` proxy to the MIS backend for invitation and membership key logic.
- Example endpoints:
  - `POST /api/frontend/membership/validate-invitation` — Validate invitation code and pin
  - `POST /api/frontend/membership/issue-key` — Issue membership key
  - `POST /api/frontend/membership/validate-key` — Validate membership key
- Configure the MIS backend URL with the `MIS_BACKEND_URL` environment variable.
- See `api/frontend_engine/routes/membership.py` for details.

---

For further extension, see the respective Python modules and add new endpoints as needed for your use case.

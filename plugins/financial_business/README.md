# Financial Business Plugin API

This plugin provides API endpoints for managing financial accounts, transactions, and administrative users.

## Features

- Account management (create, read, list)
- Admin user management (create, read, list)
- Transaction processing with atomicity guarantees
- Transaction history and records
- Placeholder legacy endpoints for backwards compatibility

## API Endpoints

### Health Check

```
GET /api/plugins/financial_business/health
```

Returns comprehensive health status of the plugin API, including:

- Database connectivity
- API endpoint availability
- Service dependencies

Example response:

```json
{
  "status": "healthy",  // Can be "healthy", "degraded", or "unhealthy"
  "timestamp": "2025-05-16T12:34:56.789Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "up",  // Can be "up", "degraded", or "down"
      "latency": 0.0023,
      "query_test": "passed"
    },
    "api": {
      "status": "up",
      "endpoints": {
        "/accounts": "up",
        "/transfers": "up",
        "/admin_users": "up"
      }
    }
  }
}
```

### Metrics

```
GET /api/plugins/financial_business/metrics/metrics
```

Returns Prometheus-compatible metrics for monitoring. The plugin tracks:

- `financial_transfer_count`: Counter of financial transfers
- `financial_transfer_amount`: Summary of transfer amounts
- `financial_transfer_errors`: Counter of transfer errors, labeled by error type
- `db_query_latency_seconds`: Summary of database query latency

### Account Management

```
POST /api/plugins/financial_business/accounts/
```

Create a new account with the following payload:

```json
{
  "account_number": "ACC12345",
  "balance": 1000.0,
  "owner_id": 1
}
```

```
GET /api/plugins/financial_business/accounts/{account_id}
```

Get details of a specific account.

```
GET /api/plugins/financial_business/accounts/
```

List all accounts with pagination (query params: `skip`, `limit`).

### Admin User Management

```
POST /api/plugins/financial_business/admin_users/
```

Create a new admin user with the following payload:

```json
{
  "name": "New Admin",
  "email": "admin@example.com",
  "password": "secure_password"
}
```

```
GET /api/plugins/financial_business/admin_users/{user_id}
```

Get details of a specific admin user.

```
GET /api/plugins/financial_business/admin_users/
```

List all admin users with pagination (query params: `skip`, `limit`).

### Transaction Management

```
POST /api/plugins/financial_business/transfers/
```

Create a new transfer with the following payload:

```json
{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": 500.0,
  "description": "Monthly rent payment"
}
```

```
GET /api/plugins/financial_business/transactions/
```

List all transactions with optional filtering by account (query params: `account_id`, `skip`, `limit`).

```
GET /api/plugins/financial_business/transactions/{transaction_id}
```

Get details of a specific transaction.

### Legacy/Placeholder Endpoints

These endpoints are maintained for backwards compatibility:

- `GET /api/plugins/financial_business/account_summary`
- `POST /api/plugins/financial_business/transfer`
- `GET /api/plugins/financial_business/track_package`
- `POST /api/plugins/financial_business/book_delivery`
- `GET /api/plugins/financial_business/charity_campaigns`
- `POST /api/plugins/financial_business/donate`
- `POST /api/plugins/financial_business/appointments`
- `GET /api/plugins/financial_business/doctors`
- `POST /api/plugins/financial_business/admissions`
- `GET /api/plugins/financial_business/calendar`

## Models

The plugin uses the following key models:

- **Account**: Represents a financial account with a balance
- **AdminUser**: Manages the accounts
- **Transaction**: Records transfers between accounts

## Database Schema

The plugin creates and uses the following tables:

- `accounts`: Stores account information
- `admin_users`: Stores administrator user information
- `transactions`: Stores transaction records

## Error Handling

The API returns appropriate status codes:

- `200`: Successful operation
- `201`: Resource created
- `400`: Invalid input (e.g., insufficient funds)
- `404`: Resource not found
- `422`: Validation error
- `500`: Server error

## Development Notes

- Database migrations are managed via Alembic
- Tests are available in `tests/plugins/financial_business/`

## Monitoring and Logging

### Health Check Infrastructure

The plugin integrates with the SpaceNew control center's health check system. The control center aggregates health statuses from all plugins and provides a centralized dashboard.

The health check implementation:

- Tests database connectivity and query performance
- Verifies API endpoint availability
- Reports detailed status including latency measurements
- Provides component-level granularity for issue identification

### Logging

All API endpoints have proper logging with different log levels:

- `INFO`: Standard operation logs
- `WARNING`: Potential issues that don't impact functionality
- `ERROR`: Critical issues that affect functionality
- `DEBUG`: Detailed information for troubleshooting

Logs include contextual information like request IDs, account IDs, and timestamps.

### Metrics

The plugin exposes Prometheus-compatible metrics that can be visualized in Grafana dashboards. Key metrics include:

- Transfer counts and amounts
- Error rates by error type
- Database query latency
- Request latency by endpoint

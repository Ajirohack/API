# Financial Business Plugin API Documentation

This document provides comprehensive documentation for the Financial Business plugin API endpoints, including request/response formats, authentication requirements, and examples.

## Base URL

All API endpoints are relative to: `http://<host>:<port>/api/plugins/financial_business/`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Health Check

### GET `/health`

Returns the health status of the Financial Business service, including database connectivity and API availability.

**Response:**

```json
{
  "status": "ok",
  "timestamp": "2025-05-17T12:34:56.789Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "up",
      "latency": 0.0234,
      "query_test": "passed"
    },
    "api": {
      "status": "up",
      "endpoints": {
        "/accounts": "up",
        "/transactions": "up"
      }
    }
  }
}
```

**Status Codes:**

- `200 OK`: Service is operational (even if some components report degraded status)

## Account Management

### GET `/accounts`

Retrieve all accounts or filter by specific criteria.

**Parameters:**

- `owner_id` (optional): Filter accounts by owner
- `status` (optional): Filter by account status (active, suspended, closed)
- `type` (optional): Filter by account type (savings, checking, investment)
- `limit` (optional): Maximum number of accounts to return
- `offset` (optional): Number of accounts to skip

**Response:**

```json
{
  "accounts": [
    {
      "id": 1,
      "owner_id": "user123",
      "account_number": "1234567890",
      "type": "savings",
      "status": "active",
      "balance": 1250.75,
      "currency": "USD",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-05-17T14:20:00Z"
    },
    {
      "id": 2,
      "owner_id": "user123",
      "account_number": "0987654321",
      "type": "checking",
      "status": "active",
      "balance": 850.25,
      "currency": "USD",
      "created_at": "2025-01-15T10:45:00Z",
      "updated_at": "2025-05-17T09:15:00Z"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

**Status Codes:**

- `200 OK`: Accounts retrieved successfully
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server-side error

### POST `/accounts`

Create a new account.

**Request:**

```json
{
  "owner_id": "user123",
  "type": "savings",
  "initial_deposit": 500.00,
  "currency": "USD"
}
```

**Response:**

```json
{
  "id": 3,
  "owner_id": "user123",
  "account_number": "5678901234",
  "type": "savings",
  "status": "active",
  "balance": 500.00,
  "currency": "USD",
  "created_at": "2025-05-17T15:30:00Z",
  "updated_at": "2025-05-17T15:30:00Z"
}
```

**Status Codes:**

- `201 Created`: Account created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server-side error

### GET `/accounts/{account_id}`

Retrieve a specific account by ID.

**Parameters:**

- `account_id`: Unique identifier for the account

**Response:**

```json
{
  "id": 1,
  "owner_id": "user123",
  "account_number": "1234567890",
  "type": "savings",
  "status": "active",
  "balance": 1250.75,
  "currency": "USD",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-05-17T14:20:00Z"
}
```

**Status Codes:**

- `200 OK`: Account retrieved successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Account not found
- `500 Internal Server Error`: Server-side error

## Transaction Management

### POST `/transactions`

Create a new transaction.

**Request:**

```json
{
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount": 250.00,
  "currency": "USD",
  "description": "Monthly transfer"
}
```

**Response:**

```json
{
  "id": "trans_abcdef123456",
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount": 250.00,
  "currency": "USD",
  "description": "Monthly transfer",
  "status": "completed",
  "timestamp": "2025-05-17T15:45:00Z"
}
```

**Status Codes:**

- `201 Created`: Transaction created successfully
- `400 Bad Request`: Invalid transaction data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient funds or permissions
- `500 Internal Server Error`: Server-side error

### GET `/transactions`

Retrieve transactions with optional filtering.

**Parameters:**

- `account_id` (optional): Filter by source or destination account
- `status` (optional): Filter by transaction status
- `start_date` (optional): Filter by start date (ISO format)
- `end_date` (optional): Filter by end date (ISO format)
- `limit` (optional): Maximum number of transactions to return
- `offset` (optional): Number of transactions to skip

**Response:**

```json
{
  "transactions": [
    {
      "id": "trans_abcdef123456",
      "source_account_id": 1,
      "destination_account_id": 2,
      "amount": 250.00,
      "currency": "USD",
      "description": "Monthly transfer",
      "status": "completed",
      "timestamp": "2025-05-17T15:45:00Z"
    },
    {
      "id": "trans_ghijkl789012",
      "source_account_id": 3,
      "destination_account_id": 1,
      "amount": 1000.00,
      "currency": "USD",
      "description": "Salary deposit",
      "status": "completed",
      "timestamp": "2025-05-15T09:00:00Z"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

## Admin Operations

### GET `/admin/metrics`

Retrieve financial business metrics for administrative dashboards.

**Response:**

```json
{
  "total_accounts": 1250,
  "active_accounts": 1100,
  "total_balance": 2500000.75,
  "average_balance": 2272.73,
  "transaction_volume_last_30_days": 1500000.50,
  "new_accounts_last_30_days": 87
}
```

**Status Codes:**

- `200 OK`: Metrics retrieved successfully
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server-side error

## Workflow Integration

The Financial Business plugin integrates with SpaceNew's workflow engine through event subscriptions and publications. It publishes events such as:

- `account_created`
- `account_closed`
- `transaction_completed`
- `funds_transferred`

And subscribes to events like:

- `user_registered`
- `user_verified`
- `session_completed` (from MirrorCore plugin)

See the `FinancialBusinessWorkflowHooks` class for implementation details and the workflow definition files for complete workflow configurations.

## Database Integration

Financial Business plugin uses PostgreSQL for data storage. The database schema includes tables for accounts, transactions, admin_users, audit_log, and metrics.

## Error Handling

All API endpoints return appropriate HTTP status codes and error messages in a consistent format:

```json
{
  "error": true,
  "message": "Error message explaining what went wrong",
  "code": "ERROR_CODE",
  "details": { "additional": "error details" }
}
```

## Production Deployment

For production deployment, see the deployment configuration documentation which includes Docker container specifications, environment variable requirements, and infrastructure recommendations.

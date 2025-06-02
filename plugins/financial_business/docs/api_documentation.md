# Financial Business Plugin API Documentation

This document provides comprehensive documentation for the Financial Business plugin API endpoints, including request/response formats, authentication requirements, and examples.

## Base URL

All API endpoints are relative to:

```
http://<host>:<port>/api/plugins/financial_business
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Authentication

Authentication is handled by the SpaceNew API Gateway. All requests to the Financial Business API endpoints must include a valid authentication token in the Authorization header.

## Common Response Formats

All responses are returned in JSON format with the following structure:

### Success Response

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Descriptive error message"
  }
}
```

## Endpoints

### Health Check

#### GET `/health`

Checks the health status of the Financial Business plugin, including database connectivity and API status.

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-05-17T10:15:30.123456Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "up",
      "latency": 0.0123,
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

### Account Management

#### GET `/accounts`

Retrieves a list of financial accounts.

**Query Parameters**:

- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of items per page (default: 20)
- `status` (optional): Filter by account status (e.g., "active", "suspended")
- `owner_id` (optional): Filter by account owner ID

**Response**:

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "account_number": "ACC123456",
        "owner_id": 42,
        "balance": "1000.00",
        "account_type": "savings",
        "status": "active",
        "created_at": "2025-01-15T10:20:30Z"
      },
      {
        "id": 2,
        "account_number": "ACC789012",
        "owner_id": 43,
        "balance": "500.50",
        "account_type": "checking",
        "status": "active",
        "created_at": "2025-02-18T14:25:30Z"
      }
    ],
    "total": 42,
    "page": 1,
    "page_size": 20,
    "pages": 3
  }
}
```

#### GET `/accounts/{account_id}`

Retrieves details of a specific account by ID.

**Path Parameters**:

- `account_id`: ID of the account to retrieve

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "account_number": "ACC123456",
    "owner_id": 42,
    "owner_name": "Jane Smith",
    "balance": "1000.00",
    "available_balance": "900.00",
    "account_type": "savings",
    "status": "active",
    "interest_rate": "2.5",
    "created_at": "2025-01-15T10:20:30Z",
    "updated_at": "2025-05-17T08:15:30Z",
    "last_transaction_date": "2025-05-15T14:30:22Z"
  }
}
```

#### POST `/accounts`

Creates a new financial account.

**Request Body**:

```json
{
  "owner_id": 42,
  "account_type": "savings",
  "initial_deposit": "500.00",
  "currency": "USD"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 3,
    "account_number": "ACC345678",
    "owner_id": 42,
    "balance": "500.00",
    "account_type": "savings",
    "status": "active",
    "created_at": "2025-05-17T10:15:30Z"
  }
}
```

#### PUT `/accounts/{account_id}`

Updates an existing account.

**Path Parameters**:

- `account_id`: ID of the account to update

**Request Body**:

```json
{
  "status": "suspended",
  "reason": "Suspicious activity detected"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "account_number": "ACC123456",
    "status": "suspended",
    "updated_at": "2025-05-17T10:20:30Z"
  }
}
```

### Transaction Management

#### GET `/transactions`

Retrieves a list of transactions.

**Query Parameters**:

- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of items per page (default: 20)
- `account_id` (optional): Filter by account ID
- `transaction_type` (optional): Filter by transaction type (e.g., "deposit", "withdrawal", "transfer")
- `start_date` (optional): Filter by transactions after this date
- `end_date` (optional): Filter by transactions before this date

**Response**:

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 101,
        "transaction_ref": "TXN-ABC123",
        "account_id": 1,
        "amount": "100.00",
        "transaction_type": "deposit",
        "status": "completed",
        "created_at": "2025-05-15T14:30:22Z"
      },
      {
        "id": 102,
        "transaction_ref": "TXN-DEF456",
        "account_id": 1,
        "amount": "-50.00",
        "transaction_type": "withdrawal",
        "status": "completed",
        "created_at": "2025-05-16T09:45:12Z"
      }
    ],
    "total": 28,
    "page": 1,
    "page_size": 20,
    "pages": 2
  }
}
```

#### GET `/transactions/{transaction_id}`

Retrieves details of a specific transaction.

**Path Parameters**:

- `transaction_id`: ID of the transaction to retrieve

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 101,
    "transaction_ref": "TXN-ABC123",
    "account_id": 1,
    "account_number": "ACC123456",
    "amount": "100.00",
    "transaction_type": "deposit",
    "description": "Salary deposit",
    "status": "completed",
    "balance_before": "900.00",
    "balance_after": "1000.00",
    "recipient_account": null,
    "created_at": "2025-05-15T14:30:22Z"
  }
}
```

#### POST `/transactions`

Creates a new transaction.

**Request Body**:

```json
{
  "account_id": 1,
  "amount": "200.00",
  "transaction_type": "deposit",
  "description": "ATM deposit"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 103,
    "transaction_ref": "TXN-GHI789",
    "account_id": 1,
    "amount": "200.00",
    "transaction_type": "deposit",
    "description": "ATM deposit",
    "status": "completed",
    "balance_before": "1000.00",
    "balance_after": "1200.00",
    "created_at": "2025-05-17T10:25:30Z"
  }
}
```

### Admin User Management

#### GET `/admin/users`

Retrieves a list of admin users.

**Query Parameters**:

- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of items per page (default: 20)
- `role` (optional): Filter by role (e.g., "admin", "operator", "auditor")

**Response**:

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "role": "admin",
        "created_at": "2025-01-10T09:00:00Z"
      },
      {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "role": "operator",
        "created_at": "2025-02-15T14:30:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20,
    "pages": 1
  }
}
```

## Event Integration

Financial Business plugin integrates with the SpaceNew event system through the following events:

### Events Published

1. `financial_business.account.created` - When a new account is created
2. `financial_business.account.status_changed` - When an account status changes
3. `financial_business.transaction.completed` - When a transaction completes
4. `financial_business.transaction.failed` - When a transaction fails
5. `financial_business.funds_transferred` - When funds are transferred between accounts

### Events Subscribed

1. `user.registered` - When a new user registers, to create an initial account
2. `user.profile_updated` - When user profile information changes
3. `mirrorcore.session.complete` - When a simulation session completes
4. `mirrorcore.trust.threshold.reached` - When a trust threshold is reached in simulation

## Admin UI Integration

The Financial Business plugin includes Admin UI components for account management, transaction processing, and reporting.

### Admin Routes

- `/admin/financial/dashboard` - Financial operations dashboard
- `/admin/financial/accounts` - Account management
- `/admin/financial/transactions` - Transaction monitoring and management
- `/admin/financial/reports` - Financial reports and metrics
- `/admin/financial/settings` - Plugin configuration settings

# Design Note

## GitHub Issues Service API

Names: Pranith Varma, Bernie, Swaroop, Weihao Fu

---

## Overview

This project implements a production-style REST API using FastAPI that acts as a wrapper around the GitHub Issues REST API. Instead of interacting directly with GitHub, clients communicate with this service, which validates requests, forwards them to GitHub, and returns simplified responses.

The application also receives GitHub webhooks, validates HMAC signatures, stores webhook events locally, and exposes OpenAPI documentation.

---

## Architecture

The application is organized into modular components.

- app/main.py
  - Application entry point

- app/routes/
  - REST API endpoints

- app/github_client.py
  - GitHub REST API integration

- app/models.py
  - Request and response models

- app/storage.py
  - Local webhook event storage

- app/webhook.py
  - Signature verification

- tests/
  - Unit tests

---

## Error Mapping

GitHub responses are translated into FastAPI HTTPExceptions.

Examples include:

- 400 Bad Request
- 401 Unauthorized
- 404 Not Found
- 422 Validation Error

This provides consistent responses while preserving GitHub error messages.

---

## Pagination

The GET /issues endpoint forwards GitHub pagination parameters.

Supported query parameters include:

- page
- per_page
- state
- labels

GitHub Link headers are forwarded to the client whenever available.

---

## Webhook Processing

The webhook endpoint supports:

- issues
- issue_comment
- ping

Each incoming request is verified using HMAC SHA-256 with the configured WEBHOOK_SECRET.

Only valid webhook requests are processed.

---

## Idempotency

GitHub may retry webhook deliveries.

To avoid duplicate processing, delivery IDs are stored in memory.

If the same delivery ID is received again, it is ignored.

---

## Security

Security considerations include:

- Environment variables for secrets
- HMAC SHA-256 verification
- Constant-time signature comparison
- No secrets logged
- GitHub Personal Access Token stored outside source code

---

## Testing

The project includes unit tests covering:

- Request models
- Issue formatting
- Webhook signature verification
- Event storage

All tests pass successfully using pytest.

---

## Docker Support

The application can be started using Docker or directly with Uvicorn.

Docker Compose is also included for local development.

---

## Future Improvements

Possible enhancements include:

- SQLite event persistence
- GitHub rate-limit retry strategy
- Conditional GET using ETag
- GitHub Actions CI pipeline
- Request IDs for structured logging
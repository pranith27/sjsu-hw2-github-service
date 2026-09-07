# GitHub Issues Service

## CMPE 272 – Homework #2

A production-style REST API built with **FastAPI** that wraps the **GitHub REST API** for managing issues and comments within a single GitHub repository.

The application exposes its own REST endpoints while communicating with GitHub in the background. It also validates GitHub Webhooks using **HMAC SHA-256**, stores processed webhook events for debugging, and automatically generates an **OpenAPI 3.1** specification.

---

# Project Overview

This project was developed for **CMPE 272 – Enterprise Software Platforms**.

Instead of interacting directly with the GitHub Issues API, clients communicate with this service. The service performs validation, forwards requests to GitHub, translates responses, and verifies incoming webhook events.

The project follows common backend development practices including:

- RESTful API design
- Environment-based configuration
- OpenAPI documentation
- Webhook signature verification
- Request validation using Pydantic
- Docker containerization
- Automated unit testing
- Structured logging
- Modular project organization

---

# Features

The service implements the following functionality:

## GitHub Issues

- Create GitHub issues
- Retrieve repository issues
- Retrieve an individual issue
- Update issue title
- Update issue body
- Close issues
- Reopen issues

## GitHub Comments

- Create comments on existing issues

## Webhooks

- Verify HMAC SHA-256 webhook signatures
- Support GitHub **issues** events
- Support GitHub **issue_comment** events
- Support **ping** events
- Ignore duplicate webhook deliveries (idempotent processing)
- Store processed webhook events for debugging

## API Documentation

- FastAPI Swagger UI
- ReDoc documentation
- Generated OpenAPI 3.1 specification

## Development

- Docker support
- Docker Compose support
- Makefile
- Unit tests using Pytest

---

# Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.14 | Programming Language |
| FastAPI | REST API Framework |
| Uvicorn | ASGI Server |
| HTTPX | GitHub API Client |
| Pydantic | Request Validation |
| Pydantic Settings | Environment Configuration |
| Pytest | Unit Testing |
| Docker | Containerization |
| GitHub REST API | External API |
| OpenAPI 3.1 | API Documentation |

---

# Repository

GitHub Repository

https://github.com/pranith27/sjsu-hw2-github-service

Repository Owner

```
pranith27
```

Repository Name

```
sjsu-hw2-github-service
```

---

# Repository Structure

```
.
├── app
│   ├── config.py
│   ├── github_client.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   ├── webhook.py
│   └── routes
│       ├── health.py
│       ├── issues.py
│       └── webhook.py
│
├── tests
│   ├── test_issues.py
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_webhook.py
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── openapi.yaml
├── design-note.md
├── README.md
└── requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
GITHUB_TOKEN=your_fine_grained_personal_access_token
GITHUB_OWNER=pranith27
GITHUB_REPO=sjsu-hw2-github-service
WEBHOOK_SECRET=mySuperSecret123
PORT=8000
```

### Environment Variable Description

| Variable | Description |
|-----------|-------------|
| GITHUB_TOKEN | Fine-Grained GitHub Personal Access Token |
| GITHUB_OWNER | Repository owner |
| GITHUB_REPO | Repository name |
| WEBHOOK_SECRET | Shared secret used for webhook verification |
| PORT | Application port |

> **Important**
>
> - Never commit your `.env` file.
> - Never expose GitHub Personal Access Tokens.
> - Only `.env.example` is included in this repository.

---

# Running the Project

## Clone Repository

```bash
git clone https://github.com/pranith27/sjsu-hw2-github-service.git

cd sjsu-hw2-github-service
```

## Create Virtual Environment

```bash
python3 -m venv venv
```

## Activate Virtual Environment

macOS / Linux

```bash
source venv/bin/activate
```

Windows

```powershell
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start the Server

```bash
uvicorn app.main:app --reload
```

The API will start on

```
http://127.0.0.1:8000
```

---

# Interactive Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

Generated OpenAPI JSON

```
http://127.0.0.1:8000/openapi.json
```

Generated OpenAPI YAML

```
openapi.yaml
```

---

# Running with Docker

## Build the Docker Image

```bash
docker build -t github-issues-service .
```

## Run the Container

```bash
docker run \
-p 8000:8000 \
--env-file .env \
github-issues-service
```

## Using Docker Compose

```bash
docker compose up --build
```

The application will be available at

```
http://localhost:8000
```

---

# API Authentication

This service authenticates with GitHub using a **Fine-Grained Personal Access Token (PAT)**.

The token is loaded from the `.env` file and is never hard-coded into the source code.

GitHub requests automatically include the following headers:

```http
Authorization: Bearer <YOUR_GITHUB_TOKEN>
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

---

# API Endpoints

## 1. Create Issue

**POST /issues**

Creates a new GitHub Issue.

### Example Request

```bash
curl -X POST http://localhost:8000/issues \
-H "Content-Type: application/json" \
-d '{
  "title":"Homework Test",
  "body":"Created using FastAPI",
  "labels":[]
}'
```

### Successful Response

```json
{
  "number": 15,
  "title": "Homework Test",
  "state": "open",
  "html_url": "https://github.com/pranith27/sjsu-hw2-github-service/issues/15"
}
```

**HTTP Status**

| Status | Meaning |
|---------|---------|
|201|Issue created|
|400|Invalid request body|
|401|GitHub authentication failed|
|500|Unexpected server error|

---

## 2. List Issues

**GET /issues**

Returns repository issues.

### Example

```bash
curl "http://localhost:8000/issues?state=open&page=1&per_page=10"
```

### Query Parameters

| Parameter | Description |
|------------|-------------|
|state|open, closed, all|
|labels|Filter by labels|
|page|Page number|
|per_page|Maximum 100 results|

---

## 3. Retrieve Issue

**GET /issues/{number}**

### Example

```bash
curl http://localhost:8000/issues/15
```

### Response

```json
{
  "number":15,
  "title":"Homework Test",
  "state":"open"
}
```

**HTTP Status**

| Status | Meaning |
|---------|---------|
|200|Success|
|404|Issue not found|

---

## 4. Update Issue

**PATCH /issues/{number}**

Updates the issue title, body, or state.

### Example

```bash
curl -X PATCH http://localhost:8000/issues/15 \
-H "Content-Type: application/json" \
-d '{
  "title":"Updated Issue",
  "state":"closed"
}'
```

### Response

```json
{
  "number":15,
  "state":"closed"
}
```

---

## 5. Add Comment

**POST /issues/{number}/comments**

Creates a new GitHub comment.

### Example

```bash
curl -X POST http://localhost:8000/issues/15/comments \
-H "Content-Type: application/json" \
-d '{
  "body":"This comment was created through the FastAPI service."
}'
```

### Successful Response

```json
{
  "id":123456789,
  "body":"This comment was created through the FastAPI service."
}
```

---

## 6. GitHub Webhook

**POST /webhook**

Receives webhook events from GitHub.

Supported events

- ping
- issues
- issue_comment

GitHub automatically includes

```
X-GitHub-Event
```

```
X-GitHub-Delivery
```

```
X-Hub-Signature-256
```

The service verifies the webhook using **HMAC SHA-256** before processing the payload.

### Successful Response

```
HTTP 204 No Content
```

### Invalid Signature

```
HTTP 401 Unauthorized
```

### Unsupported Event

```
HTTP 400 Bad Request
```

---

## 7. List Processed Webhook Events

**GET /webhook/events**

Returns recently processed webhook events.

### Example

```bash
curl http://localhost:8000/webhook/events
```

### Example Response

```json
[
  {
    "delivery_id":"123abc",
    "event":"issues",
    "action":"opened",
    "issue_number":15,
    "timestamp":"2026-09-05T18:23:41+00:00"
  }
]
```

---

## 8. Health Check

**GET /healthz**

Returns the current application health.

### Example

```bash
curl http://localhost:8000/healthz
```

### Response

```json
{
  "status":"healthy",
  "service":"GitHub Issues Service",
  "version":"1.0.0"
}
```

---

# HTTP Status Codes

| Status Code | Description |
|--------------|-------------|
|200|Successful request|
|201|Resource created|
|204|Webhook processed successfully|
|400|Invalid request|
|401|Authentication or webhook signature failure|
|404|GitHub resource not found|
|500|Unexpected internal server error|

---

# Pagination

The **GET /issues** endpoint forwards GitHub pagination parameters directly to the GitHub REST API.

Supported parameters include

- state
- labels
- page
- per_page

GitHub pagination headers (such as `Link`) are preserved whenever available, allowing clients to navigate through multiple pages of results while maintaining GitHub's pagination semantics.

---

# Webhook Configuration

GitHub Webhooks were configured to notify this service whenever issue-related events occur.

## Configure the Webhook

Navigate to your GitHub repository.

```
Settings
    ↓
Webhooks
    ↓
Add Webhook
```

Configure the webhook as follows.

### Payload URL

```
https://<your-ngrok-domain>/webhook
```

### Content Type

```
application/json
```

### Secret

```
mySuperSecret123
```

This value must match the `WEBHOOK_SECRET` environment variable configured in the application.

### Events

Select

- Issues
- Issue Comments
- Ping

---

# Webhook Processing

Incoming webhook requests are validated before processing.

The application performs the following steps:

1. Receive the webhook payload.
2. Read the `X-Hub-Signature-256` header.
3. Generate a SHA-256 HMAC using the shared secret.
4. Compare the generated signature using `hmac.compare_digest()`.
5. Reject invalid requests.
6. Store valid webhook events in memory.
7. Return **HTTP 204 No Content** immediately.

Supported webhook events include

- ping
- issues
- issue_comment

Unsupported events return

```
HTTP 400 Bad Request
```

Invalid signatures return

```
HTTP 401 Unauthorized
```

---

# Idempotent Webhook Handling

GitHub may retry webhook deliveries if a previous delivery times out or fails.

To prevent duplicate processing, the application stores previously processed GitHub Delivery IDs.

If a duplicate delivery is received, it is ignored without creating another event.

This makes webhook processing **idempotent** and retry-safe.

---

# Webhook Redelivery

GitHub allows previously delivered webhooks to be resent.

To redeliver an event

```
Repository Settings
        ↓
Webhooks
        ↓
Recent Deliveries
        ↓
Select Delivery
        ↓
Redeliver
```

After redelivery, the application verifies the webhook signature again and ignores duplicate deliveries if they were already processed.

---

# Logging

Application logs include useful debugging information.

Examples include

- Application startup
- Incoming webhook events
- GitHub request status
- Webhook delivery IDs
- Issue numbers
- Event actions

Sensitive information such as GitHub tokens and webhook secrets are never logged.

---

# OpenAPI Specification

FastAPI automatically generates an OpenAPI 3.1 specification for the service.

The generated specification is included as

```
openapi.yaml
```

The specification documents

- Request models
- Response models
- HTTP status codes
- Endpoint descriptions
- Validation rules

Interactive documentation is available at

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# Testing

The project includes automated unit tests using **Pytest**.

Run all tests

```bash
pytest
```

or

```bash
python -m pytest
```

or

```bash
make test
```

Current test suite

```
9 tests passed
```

The tests verify

- Request model validation
- Issue formatting
- Webhook signature verification
- Invalid webhook signatures
- Duplicate webhook handling
- Event storage
- Route validation
- Health endpoint
- Utility functions

Example output

```
=========================
9 passed in 0.16s
=========================
```

---

# Docker Support

The application includes

- Dockerfile
- docker-compose.yml

The Docker image contains all required dependencies and can be started using

```bash
docker compose up --build
```

or

```bash
docker run \
-p 8000:8000 \
--env-file .env \
github-issues-service
```

---

# Security

The application follows several security best practices.

- Environment variables are used for configuration.
- GitHub Personal Access Tokens are never hard-coded.
- `.env` is excluded from Git.
- Webhook requests are verified using HMAC SHA-256.
- Constant-time comparison is performed using `hmac.compare_digest()`.
- Unsupported webhook events are rejected.
- Duplicate webhook deliveries are ignored.
- GitHub authentication uses a Fine-Grained Personal Access Token.
- Secrets are never logged.

---

# Design Highlights

The application follows a modular architecture to improve readability and maintainability.

## Configuration

Application configuration is centralized using Pydantic Settings.

## GitHub Client

A dedicated GitHub client manages all communication with the GitHub REST API.

## Routing

Endpoints are separated into dedicated FastAPI routers.

- Health
- Issues
- Webhook

## Validation

Request payloads are validated using Pydantic models before processing.

## Webhook Processing

Webhook verification and event storage are isolated from API routes to keep responsibilities separate.

## Documentation

FastAPI automatically generates the OpenAPI specification and interactive documentation.

## Deployment

The project supports both local execution and Docker deployment.

---

# Submission Artifacts

The repository includes all required submission files.

- README.md
- openapi.yaml
- Dockerfile
- docker-compose.yml
- Makefile
- design-note.md
- Unit tests
- OpenAPI documentation

---

# Screenshots

The `Documentation/Screenshots` directory contains screenshots demonstrating

- Swagger UI
- Health endpoint
- Issue creation
- List issues
- Retrieve issue
- Update issue
- Add comment
- GitHub webhook delivery
- Stored webhook events
- Successful test execution
- Docker execution
- OpenAPI documentation

These screenshots are also included in the submitted report.

---

# Future Improvements

Possible future enhancements include

- SQLite database for webhook persistence
- GitHub OAuth authentication
- Support for multiple repositories
- Asynchronous background webhook processing
- Additional webhook event types
- CI/CD deployment pipeline
- Integration test automation using GitHub Actions

---

# Students

**Pranith Varma, Bernie, Swaroop, Weihao Fu**

CMPE 272 – Enterprise Software Platforms

Department of Software Engineering

San José State University

---
# GitHub Issues Service
### CMPE 272 – Homework #2

A RESTful GitHub Issues Service built using **FastAPI** that wraps the GitHub REST API for managing issues in a single repository. The service provides CRUD operations for GitHub Issues, issue comments, webhook handling with HMAC verification, OpenAPI documentation, Docker support, and automated testing.


---

# Project Overview

This project acts as a lightweight gateway between clients and the GitHub REST API.

Instead of directly calling GitHub APIs, clients communicate with this service, which:

- Creates GitHub Issues
- Retrieves Issues
- Updates Issues
- Closes/Reopens Issues
- Creates Issue Comments
- Receives GitHub Webhooks
- Validates webhook signatures
- Stores processed webhook events
- Provides OpenAPI documentation
- Includes Docker support
- Includes automated tests

---

# Features

## GitHub Issues

- Create Issues
- List Issues
- Retrieve Individual Issues
- Update Issue Title
- Update Issue Body
- Close Issues
- Reopen Issues

## Comments

- Create Issue Comments

## GitHub Webhooks

Supports:

- issues
- issue_comment
- ping

Features:

- HMAC SHA-256 Signature Verification
- Constant-Time Signature Comparison
- Duplicate Delivery Protection
- Local Event Storage
- Event Logging

## API Documentation

Swagger UI

```
http://localhost:8000/docs
```

OpenAPI JSON

```
http://localhost:8000/openapi.json
```

---

# Technology Stack

- Python 3.14
- FastAPI
- Uvicorn
- HTTPX
- GitHub REST API
- Docker
- Docker Compose
- Pytest

---

# Project Structure

```
sjsu-hw2-github-service/
│
├── app/
│   ├── config.py
│   ├── github_client.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   ├── webhook.py
│   ├── routes/
│   │     ├── issues.py
│   │     └── webhook.py
│   │
│   └── services/
│
├── tests/
│   ├── conftest.py
│   ├── test_issues.py
│   ├── test_utils.py
│   └── test_webhook.py
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── openapi.yaml
├── design-note.md
├── requirements.txt
├── README.md
└── .env.example
```

---

# Environment Variables

Create a `.env` file.

Example:

```env
GITHUB_TOKEN=YOUR_GITHUB_TOKEN
GITHUB_OWNER=YOUR_GITHUB_USERNAME
GITHUB_REPO=YOUR_REPOSITORY_NAME
WEBHOOK_SECRET=YOUR_SECRET
PORT=8000
```

| Variable | Description |
|-----------|-------------|
| GITHUB_TOKEN | GitHub Fine-Grained Personal Access Token |
| GITHUB_OWNER | GitHub Username |
| GITHUB_REPO | Repository Name |
| WEBHOOK_SECRET | Secret used for GitHub Webhook Signature Validation |
| PORT | Server Port |

---

# GitHub Token Permissions

The Fine-Grained Personal Access Token requires:

- Repository Access
- Issues → Read and Write

No additional permissions are required.

---

# Installation

Clone the repository

```bash
git clone https://github.com/pranith27/sjsu-hw2-github-service.git
```

Enter the project

```bash
cd sjsu-hw2-github-service
```

Create virtual environment

```bash
python3 -m venv venv
```

Activate

Mac/Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Application

Start FastAPI

```bash
uvicorn app.main:app --reload
```

Application

```
http://localhost:8000
```

Swagger

```
http://localhost:8000/docs
```

---

# Running with Docker

Build

```bash
docker build -t github-service .
```

Run

```bash
docker run \
-p 8000:8000 \
--env-file .env \
github-service
```

Or

```bash
docker compose up --build
```

---

# API Endpoints

---

## Create Issue

POST

```
/issues
```

Example

```bash
curl -X POST http://localhost:8000/issues \
-H "Content-Type: application/json" \
-d '{
"title":"Test Issue",
"body":"Created using FastAPI",
"labels":[]
}'
```

---

## List Issues

GET

```
/issues
```

Example

```bash
curl "http://localhost:8000/issues?state=open"
```

---

## Get Issue

GET

```
/issues/{issue_number}
```

Example

```bash
curl http://localhost:8000/issues/1
```

---

## Update Issue

PATCH

```
/issues/{issue_number}
```

Example

```bash
curl -X PATCH http://localhost:8000/issues/1 \
-H "Content-Type: application/json" \
-d '{
"title":"Updated Title",
"body":"Updated Body",
"state":"open"
}'
```

---

## Create Comment

POST

```
/issues/{issue_number}/comments
```

Example

```bash
curl -X POST http://localhost:8000/issues/1/comments \
-H "Content-Type: application/json" \
-d '{
"body":"This is a comment"
}'
```

---

## Receive GitHub Webhook

POST

```
/webhook
```

Supported Events

- ping
- issues
- issue_comment

Returns

```
204 No Content
```

---

## View Stored Events

GET

```
/webhook/events
```

Returns

```json
[
  {
    "delivery_id":"...",
    "event":"issues",
    "action":"opened",
    "issue_number":5,
    "timestamp":"..."
  }
]
```

---

# GitHub Webhook Configuration

Create an ngrok tunnel

```bash
ngrok http 8000
```

Copy the forwarding URL

Example

```
https://example.ngrok-free.app
```

Open GitHub Repository

Settings

→ Webhooks

→ Add Webhook

Payload URL

```
https://example.ngrok-free.app/webhook
```

Content Type

```
application/json
```

Secret

```
Same value as WEBHOOK_SECRET
```

Events

```
Issues

Issue Comments

Ping
```

Save.

---

# Testing Webhooks

1. Create an Issue directly on GitHub

2. Observe the FastAPI logs

Example

```
WEBHOOK RECEIVED

Event: issues

Action: opened

Issue: Homework Test
```

Retrieve stored events

```
GET /webhook/events
```

---

# Running Tests

Run all tests

```bash
pytest
```

Run a specific file

```bash
pytest tests/test_webhook.py
```

Run with verbose output

```bash
pytest -v
```

---

# OpenAPI

The project includes an OpenAPI 3.1 specification.

```
openapi.yaml
```

The specification documents:

- Request Models
- Response Models
- Error Models
- Examples
- Security Schemes

---

# Security

The application follows several security best practices:

- Environment Variables for Secrets
- No Hardcoded Credentials
- Fine-Grained GitHub PAT
- HMAC SHA-256 Webhook Validation
- Constant-Time Signature Comparison
- Duplicate Delivery Protection
- Request Validation using FastAPI

---

# Error Handling

The service returns meaningful HTTP responses.

Examples:

| Status | Description |
|---------|-------------|
| 200 | Success |
| 201 | Resource Created |
| 204 | Webhook Accepted |
| 400 | Invalid Request |
| 401 | Authentication Failed |
| 404 | Resource Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# Design Decisions

- FastAPI selected for high performance and automatic OpenAPI generation.
- GitHub REST API is accessed through a dedicated client module.
- Webhook signature verification uses HMAC SHA-256 with constant-time comparison.
- Processed webhook deliveries are stored locally and duplicate deliveries are ignored.
- Environment variables are used for all sensitive configuration values.
- Docker support enables consistent deployment across environments.

---

# Future Improvements

- SQLite database for persistent webhook storage
- GitHub Actions CI/CD pipeline
- Rate-limit retry logic
- ETag conditional GET support
- Authentication middleware
- Structured logging with request IDs
- Metrics and monitoring

---

# References

- GitHub REST API Documentation
- FastAPI Documentation
- Docker Documentation
- Pytest Documentation


---

## Author

Pranith Varma

Course: CMPE 272 – Enterprise Software Platforms

San Jose State University
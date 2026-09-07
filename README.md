# GitHub Issues Service
### CMPE 272 – Homework #2

A RESTful GitHub Issues Service built with **FastAPI** that wraps the GitHub REST API for managing issues and comments for a single GitHub repository. The service also validates GitHub webhooks using HMAC SHA-256 signatures and exposes its own API documented with OpenAPI 3.1.


---

# Project Overview

This project provides a simplified REST API that communicates with the GitHub Issues API.

Features include:

- Create GitHub Issues
- List repository issues
- Retrieve a single issue
- Update existing issues
- Close/Reopen issues
- Add comments to issues
- Verify GitHub Webhook signatures
- Receive GitHub Issue events
- OpenAPI documentation
- Docker support
- Automated unit tests

---

# Technology Stack

- Python 3.14
- FastAPI
- Uvicorn
- HTTPX
- Pydantic
- Pytest
- Docker
- GitHub REST API

---

# Repository Used

Repository Owner

```
pranith27
```

Repository

```
sjsu-hw2-github-service
```

---

# Environment Variables

Create a `.env` file.

```
GITHUB_TOKEN=<your_fine_grained_token>

GITHUB_OWNER=pranith27

GITHUB_REPO=sjsu-hw2-github-service

WEBHOOK_SECRET=mySuperSecret123

PORT=8000
```

**Important**

- Never commit `.env`
- Never commit GitHub tokens
- Only `.env.example` is included in the repository.

---

# Project Structure

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
│   ├── services
│   └── routes
│       ├── issues.py
│       └── webhook.py
│
├── tests
│   ├── test_issues.py
│   ├── test_utils.py
│   ├── test_webhook.py
│   └── conftest.py
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

# Running Locally

Clone repository

```bash
git clone https://github.com/pranith27/sjsu-hw2-github-service.git

cd sjsu-hw2-github-service
```

Create virtual environment

```bash
python3 -m venv venv
```

Activate

macOS/Linux

```bash
source venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

Start server

```bash
uvicorn app.main:app --reload
```

The API will be available at

```
http://127.0.0.1:8000
```

Swagger UI

```
http://127.0.0.1:8000/docs
```

OpenAPI JSON

```
http://127.0.0.1:8000/openapi.json
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

Or use Docker Compose

```bash
docker compose up --build
```

---

# API Endpoints

## POST /issues

Creates a GitHub issue.

Request

```json
{
  "title":"Webhook Test",
  "body":"Testing GitHub webhook",
  "labels":[]
}
```

Successful Response

```json
{
  "number":4,
  "title":"Webhook Test",
  "state":"open",
  "html_url":"https://github.com/pranith27/sjsu-hw2-github-service/issues/4"
}
```

---

## GET /issues

Returns all repository issues.

Optional query parameters

```
state
page
per_page
labels
```

---

## GET /issues/{number}

Returns a specific GitHub issue.

Example

```
GET /issues/4
```

---

## PATCH /issues/{number}

Updates

- title
- body
- state

Example

```json
{
    "title":"Updated Title",
    "state":"closed"
}
```

---

## POST /issues/{number}/comments

Adds a GitHub issue comment.

Request

```json
{
    "body":"This issue was created through my FastAPI service."
}
```

---

## POST /webhook

Receives GitHub webhook events.

Supported events

- ping
- issues
- issue_comment

Webhook signatures are validated using

```
X-Hub-Signature-256
```

using

```
HMAC SHA-256
```

Invalid signatures return

```
401 Unauthorized
```

Successful requests return

```
204 No Content
```

---

## GET /webhook/events

Returns recently processed webhook events stored by the application.

---

## GET /healthz

Returns application health status.

---

# Webhook Configuration

GitHub Repository

```
Settings

↓

Webhooks

↓

Add Webhook
```

Payload URL

```
https://<your-ngrok-domain>/webhook
```

Content Type

```
application/json
```

Secret

```
mySuperSecret123
```

Events

Select

```
Issues

Issue Comments

Ping
```

---

# Successful Webhook Example

Console Output

```
========== WEBHOOK RECEIVED ==========
Event: issues
Action: opened
Issue: Webhook Test 2
======================================
```

GitHub also successfully delivered

```
POST /webhook

HTTP 204
```

---

# API Authentication

The service authenticates to GitHub using a Fine-Grained Personal Access Token.

GitHub REST API requests include

```
Authorization: Bearer <TOKEN>

Accept: application/vnd.github+json
```

Secrets are loaded using environment variables.

---

# Testing

Run all tests

```bash
pytest
```

Or

```bash
make test
```

Current test directory

```
tests/

├── test_issues.py
├── test_utils.py
├── test_webhook.py
└── conftest.py
```

Tests include

- Route validation
- Webhook signature verification
- GitHub API request testing
- Utility functions

---

# OpenAPI

The project includes

```
openapi.yaml
```

containing

- Request schemas
- Response schemas
- Error models
- Endpoint definitions

Swagger UI is automatically available through FastAPI.

---

# Security

This project follows several security best practices.

- GitHub token stored in environment variables
- Webhook HMAC SHA-256 verification
- Constant-time signature comparison using `hmac.compare_digest`
- `.env` excluded from Git
- Fine-Grained GitHub PAT used
- No secrets committed into the repository

---

# Design Notes

The project design focuses on

- Separation of routes and business logic
- GitHub API wrapper
- Central configuration
- Reusable request models
- HMAC webhook verification
- Lightweight webhook event storage
- Docker deployment
- FastAPI automatic OpenAPI generation

More details are provided in

```
design-note.md
```

---

# Documentation

The repository also includes

- README.md
- openapi.yaml
- Dockerfile
- docker-compose.yml
- Makefile
- design-note.md
- Unit Tests
- Swagger Documentation

---

# Screenshots

The `Documentation/Screenshots` folder contains screenshots demonstrating

- Swagger UI
- GitHub Issue Creation
- GitHub Webhook Delivery
- GitHub Webhook Events
- Terminal Output
- API Testing

These screenshots are also included in the submitted report.

---

# Author

Pranith Varma

Course: CMPE 272 – Enterprise Software Platforms

San José State University.
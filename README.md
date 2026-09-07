# GitHub Issues Service

CMPE 272 Homework 2: a FastAPI gateway for issues and comments in one configured GitHub repository. It verifies signed GitHub webhooks, keeps a process-local event log, and ships an OpenAPI 3.1 contract, offline regression tests, opt-in live integration tests, and Docker startup checks.

Original implementation: Pranith Varma. Requirements remediation and review: Bernie Miao using AI coding assistance. Team members: Pranith Varma, Bernie Miao, Swaroop, Weihao Fu. Each member should confirm their actual contribution in the final report.

## Run locally

Use Python 3.12 or later. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env locally with your own credentials; do not print or screenshot them.
make run
```

The default server is http://127.0.0.1:8000, with Swagger at `/docs`, the live schema at `/openapi.json`, and health at `/healthz`. To use a different port, export PORT before `make run` and set the same value in `.env`.

| Variable | Purpose |
|---|---|
| GITHUB_TOKEN | Fine-grained GitHub token restricted to the test repository, Issues read/write |
| GITHUB_OWNER | Owner of that repository |
| GITHUB_REPO | Repository name |
| WEBHOOK_SECRET | A new random shared secret also configured in GitHub's webhook |
| PORT | Server port, default 8000 |

`pydantic-settings` loads the application configuration. `.env` and local environments are excluded from Git and Docker build context. If a token or webhook secret appeared in a screenshot or shared file, its owner must rotate it; removing the image does not revoke a credential.

## Docker

```sh
docker build -t github-issues-service .
docker run --rm --name github-issues-service \
  -p 127.0.0.1:8000:8000 --env-file .env github-issues-service
```

This example uses PORT=8000. For another port, change both port numbers and the environment value. Docker Compose reads PORT from `.env` and provides a health check:

```sh
docker compose up --build
```

A successful build is not a startup test: verify `/healthz` and `/openapi.json` from the running container. The image runs as a non-root user and copies only the application and schema, not local credentials.

## Authentication and exposure

The service authenticates **outbound GitHub requests** with the server's GITHUB_TOKEN. It does not accept or implement caller bearer authentication. The OpenAPI `GitHubBearer` scheme and `x-upstream-security` extension document that distinction; they are not claims that incoming requests require bearer authentication.

Keep the API on localhost. For a webhook demo, expose only POST `/webhook`, not the issue-management or event-inspection routes. With the current ngrok agent:

```sh
ngrok http 8000 --traffic-policy-file ngrok-webhook-policy.yml
```

The supplied [ngrok traffic policy](https://ngrok.com/docs/gateway/traffic-policy/actions/deny) denies requests outside the webhook path/method. Verify it with your ngrok version and plan before exposing a real-token service. No tunnel is started automatically by the application or tests.

## API examples

Set BASE to your local server. Substitute a real returned issue number for 123; GitHub does not delete issues, so the delete-equivalent operation closes them.

```sh
BASE=http://127.0.0.1:8000

# Create: 201, JSON issue, Location header
curl -i -X POST "$BASE/issues" -H 'Content-Type: application/json' \
  -d '{"title":"HW2 example","body":"Created through the service","labels":[]}'

# List: preserves GitHub Link pagination header
curl -i "$BASE/issues?state=open&page=1&per_page=10"

# Retrieve
curl -i "$BASE/issues/123"

# Update title and body
curl -i -X PATCH "$BASE/issues/123" -H 'Content-Type: application/json' \
  -d '{"title":"Updated example","body":"Updated body"}'

# Close and reopen
curl -i -X PATCH "$BASE/issues/123" -H 'Content-Type: application/json' -d '{"state":"closed"}'
curl -i -X PATCH "$BASE/issues/123" -H 'Content-Type: application/json' -d '{"state":"open"}'

# Create and fetch comments
curl -i -X POST "$BASE/issues/123/comments" -H 'Content-Type: application/json' \
  -d '{"body":"Comment from the service"}'
curl -i "$BASE/issues/123/comments?page=1&per_page=10"

# Local event inspection and health
curl -i "$BASE/webhook/events"
curl -i "$BASE/healthz"

# Local validation error: 400, without a GitHub call
curl -i -X POST "$BASE/issues" -H 'Content-Type: application/json' -d '{}'
```

Issue list state must be open/closed/all, page must be positive, and per_page must be 1–100. Titles/comments reject empty or whitespace-only content. Errors use `{ "error": "code", "detail": ... }`; all responses include X-Request-ID. Invalid local inputs and GitHub validation failures return 400; authentication/permission/not-found statuses are preserved; rate limits return 429 with Retry-After; transport failures return 503.

## Webhook setup and redelivery

In the test repository's Settings → Webhooks, add the tunnel URL followed by `/webhook`, select `application/json`, configure the same new WEBHOOK_SECRET, and subscribe to Issues and Issue comments. GitHub also sends a ping when testing the configuration.

The receiver verifies HMAC SHA-256 over the **exact raw bytes** with constant-time comparison before parsing JSON. It requires a delivery ID, validates event/action/payload, and acknowledges success with 204. Invalid signatures return 401; malformed payloads or unsupported events/actions return 400; bodies over 25 MiB return 413.

To check redelivery, choose a successful delivery in GitHub's Recent Deliveries and select Redeliver. Verify another 204 and that `/webhook/events` contains no duplicate for that delivery ID/action pair. Only inspect response/summary fields in screenshots; never show tokens, secrets or raw signature values.

The in-memory event store and dedupe set are shared within one process and lost on restart. This matches the assignment's permitted in-memory store, but is not durable multi-worker processing. The event endpoint returns recent entries; run one worker for the demo.

## Reliability and logging

GET requests use bounded retries: at most three attempts. Short Retry-After waits of at most one second can be honored; longer waits are returned to the caller rather than tying up the worker. GitHub rate-limit 403 responses are classified separately from ordinary permission failures. GET server errors use bounded backoff.

Writes are not automatically retried, and transport errors are not automatically retried. A timed-out issue/comment creation might already have succeeded upstream; inspect the repository before repeating it. This avoids creating duplicate resources merely to hide an uncertain response.

Logs are JSON records with a correlation request ID. Webhook records include delivery ID, event, action and issue number. Raw payloads, signatures, credentials and exception contents are excluded from application log messages.

## Offline checks and OpenAPI

```sh
make lint
make test
make openapi
```

`make test` excludes live tests, uses dummy settings, blocks external HTTP in offline tests, and enforces at least 80% application line coverage. It covers real routes with the external HTTP boundary mocked: validation, issue/comment behavior, upstream errors/pagination/rate limits, HMAC checks, action validation, deduplication and request IDs.

`make openapi` explicitly exports YAML from the application's schema; FastAPI does not write that YAML file automatically. Lint, offline tests, schema consistency, and Docker startup were checked locally using dummy settings.

## Live integration verification

This is a separate test against an already running service configured with **your rotated credentials** and a working real GitHub webhook. It creates an issue and a comment, changes that issue's state, waits for actual webhook deliveries, and closes its own issue afterward. It never runs merely because GITHUB_TOKEN exists.

```sh
LIVE_SERVICE_URL=http://127.0.0.1:8000 make integration
```

The test explicitly enables RUN_LIVE_INTEGRATION. It checks create/get, updating title/body, close/reopen, comment creation/retrieval, and matching issue/comment events received by the service. A missing URL or missing webhook evidence fails rather than silently passing. Use only a dedicated test repository. Record the actual result; passing offline tests is not proof that this live flow has completed.

## Submission evidence

Submit a Word document with screenshots, repository URL, and a concise explanation of the implementation. Include the actual offline coverage output, a successful **running-container** health check, and the real integration result after rerunning with rotated credentials. Do not claim an unexecuted live test passed. Keep the design note within two pages when rendering it.

[Design note](design-note.md) · [OpenAPI contract](openapi.yaml) · [Tests](tests/)

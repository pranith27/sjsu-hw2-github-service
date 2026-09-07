# GitHub Issues Service design note

The service exposes issue and comment operations for one repository configured through environment variables. FastAPI handles routing and Pydantic validates inputs. A shared HTTPX client wrapper sends authenticated requests to GitHub. Original implementation: Pranith Varma. Remediation and review: Bernie Miao using AI coding assistance.

## HTTP contract and upstream failures

Response models describe Issue, Comment and Error payloads in the exported OpenAPI 3.1 contract. Missing/invalid inputs return 400, including upstream GitHub validation failures. Authentication, permission and not-found errors retain their useful status and message. Issue creation returns 201 with Location; accepted webhooks return 204. Pagination parameters are validated before forwarding, and GitHub's Link header is returned unchanged.

Rate-limited 403 responses are distinguished from ordinary permission failures. Rate-limit responses become 429 with Retry-After derived from provider headers or a conservative fallback. GET requests may retry up to three times with short bounded delays. A long provider wait is surfaced to the caller instead of sleeping inside a worker. Writes and transport failures are not retried automatically because an ambiguous timeout can occur after GitHub created an issue/comment. Such failures return 503 and require inspecting upstream state before another write.

## Webhook integrity and idempotency

The receiver limits the body to 25 MiB and verifies its raw bytes using HMAC SHA-256 and constant-time comparison. Only then does it parse JSON and validate event type, action, delivery ID and the required issue number. Ping has a separate minimal payload path. Unsupported or malformed requests return 400; signature failures return 401. An atomic in-memory update records each delivery-ID/action pair once, so concurrent retries do not append duplicates.

In-memory storage is explicitly allowed by the assignment. It keeps this single-process demonstration small but loses state on restart and does not synchronize multiple workers. A durable store with a unique delivery/action constraint would be needed if those deployment requirements changed. Read operations return snapshots rather than mutable references to the stored event data.

## Credentials and exposure

GITHUB_TOKEN is a server-managed bearer credential for outbound GitHub calls, scoped to Issues read/write in the test repository. The OpenAPI security scheme and upstream-security extension describe that role without pretending that the service implements caller authentication. Issue-management routes stay on localhost. The documented tunnel policy exposes only POST /webhook; the signature is its authentication boundary.

Credentials remain outside source and image layers. Docker copies only the application/schema, runs as a non-root user, and receives configuration at runtime. Exposed credentials must be rotated by their owner; editing a report cannot revoke them. JSON logs contain request IDs and safe webhook summary fields, not raw payloads, signatures or secrets. Validation errors omit reflected input and unexpected failures return a generic error.

## Verification

Offline tests run without real credentials and replace the external HTTP boundary, exercising validation, models, error mapping, pagination, retry decisions, signed webhook payloads, concurrent duplicate handling and correlation headers. Coverage is enforced at 80% or above. Local verification also checked lint, regenerated OpenAPI consistency, Docker build and a running-container health/schema smoke test.

The live suite is explicitly opt-in against an already running, GitHub-connected service. It exercises create/get/update/close/reopen, comment create/fetch, and actual matching webhook receipt, then closes its own test issue. Its result must be recorded separately after credentials and the webhook are configured; offline success does not establish live connectivity.

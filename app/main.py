"""Service composition and public HTTP contract. Remediation: Bernie Miao with AI assistance."""
from contextlib import asynccontextmanager
from http import HTTPStatus
import re
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.logger import logger, request_id_var
from app.routes.health import router as health_router
from app.routes.issues import router as issues_router
from app.routes.webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app):
    logger.info("GitHub Issues Service started")
    yield


app = FastAPI(
    title="GitHub Issues Service API",
    version="1.0.0",
    summary="A single-repository GitHub Issues gateway",
    description=("Issues, comments, signed webhooks and local event inspection. "
                 "GITHUB_TOKEN supplies the service's outbound GitHub bearer credential. "
                 "Caller authentication is not implemented: run on localhost and expose only /webhook through a tunnel."),
    lifespan=lifespan,
)
app.include_router(health_router)
app.include_router(issues_router)
app.include_router(webhook_router)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Do not reflect request bodies, inputs, or non-serializable validation context.
    errors = [{k: error[k] for k in ("loc", "msg", "type")} for error in exc.errors()]
    return JSONResponse(status_code=400, content={"error": "validation_error", "detail": errors})


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")
    return JSONResponse(status_code=exc.status_code, headers=exc.headers,
                        content={"error": code, "detail": exc.detail})


@app.middleware("http")
async def correlate_request(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    request_id = supplied if re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", supplied) else uuid4().hex
    token = request_id_var.set(request_id)
    started = time.monotonic()
    try:
        try:
            response = await call_next(request)
        except Exception:
            # Exception text may contain request or provider secrets.
            logger.error("Unhandled request error", extra={"status_code": 500})
            response = JSONResponse(status_code=500, content={"error": "internal_server_error", "detail": "Unexpected server error"})
        response.headers["X-Request-ID"] = request_id
        logger.info("Request completed", extra={"method": request.method, "path": request.url.path,
                    "status_code": response.status_code, "duration_ms": round((time.monotonic() - started) * 1000, 2)})
        return response
    finally:
        request_id_var.reset(token)


_original_openapi = app.openapi


def openapi_contract():
    schema = _original_openapi()
    # This bearer scheme describes upstream authentication, not caller auth.
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["GitHubBearer"] = {
        "type": "http", "scheme": "bearer",
        "description": "Server-managed GitHub token from GITHUB_TOKEN. It is not accepted from caller headers.",
    }
    for path, path_item in schema["paths"].items():
        for operation in path_item.values():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue
            responses = operation["responses"]
            if "422" in responses:
                responses.pop("422")
                responses.setdefault("400", {"description": "Invalid request", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}})
            for response in responses.values():
                response.setdefault("headers", {})["X-Request-ID"] = {"description": "Request correlation ID", "schema": {"type": "string"}}
            if path.startswith("/issues"):
                operation["x-upstream-security"] = [{"GitHubBearer": []}]
    return schema


app.openapi = openapi_contract

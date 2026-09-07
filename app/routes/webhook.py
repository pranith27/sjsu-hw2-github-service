import json
from datetime import datetime

from pydantic import BaseModel

from fastapi import APIRouter, Header, HTTPException, Request, Response

from app.logger import logger
from app.models import ErrorResponse
from app.storage import get_events, save_event
from app.webhook import verify_signature

router = APIRouter(prefix='/webhook', tags=['Webhook'])
MAX_BODY_BYTES = 25 * 1024 * 1024
# GitHub's documented action types, including issue field changes:
# https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#issues
ACTIONS = {
    'issues': frozenset({
        'opened', 'edited', 'deleted', 'transferred', 'pinned', 'unpinned',
        'closed', 'reopened', 'assigned', 'unassigned', 'labeled', 'unlabeled',
        'locked', 'unlocked', 'milestoned', 'demilestoned', 'typed', 'untyped',
        'field_added', 'field_removed',
    }),
    'issue_comment': frozenset({'created', 'edited', 'deleted'}),
}


class EventResponse(BaseModel):
    delivery_id: str
    event: str
    action: str | None
    issue_number: int | None
    timestamp: datetime


@router.post('', status_code=204, openapi_extra={
    'requestBody': {
        'required': True,
        'description': (
            'Raw GitHub JSON, at most 25 MiB. Sign the exact request bytes with '
            'HMAC-SHA256 in X-Hub-Signature-256; send X-GitHub-Event and a nonempty '
            'X-GitHub-Delivery. issues and issue_comment require a supported action '
            'and a positive issue.number; ping requires only a JSON object.'
        ),
        'content': {'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'action': {'type': 'string', 'enum': sorted(set().union(*ACTIONS.values()))},
                    'issue': {'type': 'object', 'properties': {
                        'number': {'type': 'integer', 'minimum': 1},
                    }, 'required': ['number']},
                },
            },
            'examples': {
                'issues_opened': {'summary': 'X-GitHub-Event: issues',
                                  'value': {'action': 'opened', 'issue': {'number': 1}}},
                'comment_created': {'summary': 'X-GitHub-Event: issue_comment',
                                    'value': {'action': 'created', 'issue': {'number': 1}}},
                'ping': {'summary': 'X-GitHub-Event: ping', 'value': {'zen': 'Keep it logically awesome.'}},
            },
        }},
    },
}, responses={
    400: {'model': ErrorResponse, 'description': 'Invalid event, delivery ID or payload'},
    401: {'model': ErrorResponse, 'description': 'Invalid or missing HMAC signature'},
    413: {'model': ErrorResponse, 'description': 'Webhook body exceeds 25 MiB'},
})
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
):
    if not x_hub_signature_256:
        raise HTTPException(401, 'Invalid webhook signature')
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_BODY_BYTES:
            raise HTTPException(413, 'Webhook payload too large')
        body.extend(chunk)
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(401, 'Invalid webhook signature')
    if x_github_event not in ('ping', 'issues', 'issue_comment'):
        raise HTTPException(400, 'Unsupported webhook event')
    if not x_github_delivery or not x_github_delivery.strip():
        raise HTTPException(400, 'X-GitHub-Delivery is required')
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise HTTPException(400, 'Malformed JSON payload') from None
    if not isinstance(payload, dict):
        raise HTTPException(400, 'Webhook payload must be an object')

    action = None
    issue_number = None
    if x_github_event != 'ping':
        action = payload.get('action')
        if not isinstance(action, str) or action not in ACTIONS[x_github_event]:
            raise HTTPException(400, 'Unsupported or missing webhook action')
        issue = payload.get('issue')
        if not isinstance(issue, dict) or type(issue.get('number')) is not int or issue['number'] <= 0:
            raise HTTPException(400, 'Webhook issue.number must be a positive integer')
        issue_number = issue['number']

    stored = save_event(x_github_delivery, x_github_event, action, issue_number)
    logger.info('Webhook received', extra={
        'delivery_id': x_github_delivery,
        'event': x_github_event,
        'action': action,
        'issue_number': issue_number,
        'duplicate': not stored,
    })
    return Response(status_code=204)


@router.get('/events', response_model=list[EventResponse])
def events():
    """Return recently processed webhook event summaries."""
    return get_events()

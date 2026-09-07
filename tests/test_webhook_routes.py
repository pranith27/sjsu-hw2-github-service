import hashlib
import hmac
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import settings
from app import storage
from app.routes.webhook import router
from app.webhook import verify_signature


@pytest.fixture
def client():
    storage.events.clear()
    storage.processed_deliveries.clear()
    app = FastAPI()
    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    storage.events.clear()
    storage.processed_deliveries.clear()


def deliver(client, payload, event='issues', delivery='delivery-1', signature=True):
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    headers = {'X-GitHub-Event': event, 'Content-Type': 'application/json'}
    if delivery is not None:
        headers['X-GitHub-Delivery'] = delivery
    if signature:
        headers['X-Hub-Signature-256'] = 'sha256=' + hmac.new(settings.WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return client.post('/webhook', content=body, headers=headers)


@pytest.mark.parametrize('payload', [b'{', b'\xff', [], None, 'text', {'action': []},
    {'action': 'opened'}, {'action': 'opened', 'issue': None},
    {'action': 'opened', 'issue': {'number': True}},
    {'action': 'opened', 'issue': {'number': -1}}])
def test_malformed_payload_returns_400_without_storage(client, payload):
    assert deliver(client, payload).status_code == 400
    assert storage.get_events() == []


@pytest.mark.parametrize('action', [None, '', 'not-an-action', ['opened']])
@pytest.mark.parametrize('event', ['issues', 'issue_comment'])
def test_unknown_or_missing_action_returns_400(client, action, event):
    assert deliver(client, {'action': action, 'issue': {'number': 3}}, event).status_code == 400


@pytest.mark.parametrize('delivery', [None, '', '   '])
def test_delivery_required(client, delivery):
    assert deliver(client, {}, event='ping', delivery=delivery).status_code == 400
    assert storage.get_events() == []


def test_signature_and_event_contract(client):
    assert deliver(client, {}, 'ping', signature=False).status_code == 401
    assert client.post('/webhook', content=b'{}', headers={'X-Hub-Signature-256': 'sha256=wrong'}).status_code == 401
    assert deliver(client, {}, 'push').status_code == 400
    assert deliver(client, {}, 'ping').status_code == 204
    assert storage.get_events()[0]['action'] is None
    assert verify_signature(b'{}', 'sha256=é') is False


@pytest.mark.parametrize('event,action', [('issues', x) for x in (
    'opened', 'edited', 'deleted', 'transferred', 'pinned', 'unpinned', 'closed',
    'reopened', 'assigned', 'unassigned', 'labeled', 'unlabeled', 'locked',
    'unlocked', 'milestoned', 'demilestoned', 'typed', 'untyped', 'field_added', 'field_removed')]
    + [('issue_comment', x) for x in ('created', 'edited', 'deleted')])
def test_documented_actions_and_deduplication(client, event, action):
    payload = {'action': action, 'issue': {'number': 9}}
    assert deliver(client, payload, event).status_code == 204
    assert deliver(client, payload, event).status_code == 204
    stored = client.get('/webhook/events').json()
    assert len(stored) == 1
    assert stored[0]['issue_number'] == 9 and stored[0]['action'] == action
    assert 'timestamp' in stored[0]


def test_same_delivery_different_action_is_stored(client):
    for action in ['opened', 'closed']:
        assert deliver(client, {'action': action, 'issue': {'number': 1}}).status_code == 204
    assert len(storage.get_events()) == 2


def test_body_limit(client, monkeypatch):
    import app.routes.webhook as module
    monkeypatch.setattr(module, 'MAX_BODY_BYTES', 16, raising=False)
    assert deliver(client, b' ' * 17, event='ping').status_code == 413


def test_openapi_describes_signed_payload_and_event_results(client):
    document = client.get('/openapi.json').json()
    post = document['paths']['/webhook']['post']
    assert 'requestBody' in post
    assert post['requestBody']['required'] is True
    content = post['requestBody']['content']['application/json']
    assert content['schema']['type'] == 'object'
    assert content['schema']['properties']['issue']['properties']['number']['minimum'] == 1
    assert set(content['examples']) == {'issues_opened', 'comment_created', 'ping'}
    assert {'400', '401', '413'} <= post['responses'].keys()
    response = document['paths']['/webhook/events']['get']['responses']['200']
    schema = response['content']['application/json']['schema']
    assert schema.get('type') == 'array'
    event = document['components']['schemas'][schema['items']['$ref'].split('/')[-1]]
    assert {'delivery_id', 'event', 'action', 'issue_number', 'timestamp'} <= set(event['required'])
    assert {'type': 'null'} in event['properties']['action']['anyOf']
    assert {'type': 'null'} in event['properties']['issue_number']['anyOf']
    assert event['properties']['timestamp']['format'] == 'date-time'
    assert deliver(client, {}, event='ping').status_code == 204
    stored = client.get('/webhook/events')
    assert stored.status_code == 200
    assert stored.json()[0]['action'] is None and stored.json()[0]['issue_number'] is None

"""Explicit opt-in live test: creates a REAL GitHub issue and comment.

Run only against an already running service configured with rotated GitHub
credentials and a webhook secret. Tests need no GitHub token. Configure the
repository webhook to deliver both issues and issue_comment events to that
service, exposing ONLY /webhook through an external URL/tunnel. Keep the REST
service local/private. Use one server process for its in-memory event store.

RUN_LIVE_INTEGRATION=1 LIVE_SERVICE_URL=http://127.0.0.1:8000 \
    pytest -m live tests/test_integration.py

The test verifies genuine GitHub webhook deliveries, never posts fabricated
webhook payloads, and closes only its newly created issue in cleanup. The issue
and comment remain in the repository as test artifacts; nothing is deleted.
"""
import os
import time
from urllib.parse import urlsplit
import uuid

import httpx
import pytest

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.getenv('RUN_LIVE_INTEGRATION') != '1',
                       reason='Set RUN_LIVE_INTEGRATION=1 to explicitly allow real GitHub writes'),
]


def test_live_issue_lifecycle_comments_and_real_webhooks():
    service_url = os.getenv('LIVE_SERVICE_URL', '').strip()
    if not service_url:
        pytest.fail('RUN_LIVE_INTEGRATION=1 requires LIVE_SERVICE_URL for an already running service')
    parsed = urlsplit(service_url)
    if (parsed.scheme not in {'http', 'https'} or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        pytest.fail('LIVE_SERVICE_URL must be an HTTP(S) service URL without credentials, query or fragment')

    unique = uuid.uuid4().hex
    title = f'CMPE 272 live integration {unique}'
    body = f'Test-created issue for service/webhook validation: {unique}'
    issue_number = None
    with httpx.Client(base_url=service_url.rstrip('/') + '/', timeout=10.0,
                      follow_redirects=False) as client:
        try:
            response = client.post('issues', json={'title': title, 'body': body, 'labels': []})
            assert response.status_code == 201, f'Create issue returned HTTP {response.status_code}'
            created = response.json()
            assert type(created.get('number')) is int and created['number'] > 0
            issue_number = created['number']
            issue_path = f'issues/{issue_number}'

            response = client.get(issue_path)
            assert response.status_code == 200
            fetched = response.json()
            assert fetched['number'] == issue_number
            assert fetched['title'] == title and fetched['body'] == body
            assert fetched['state'] == 'open'

            title += ' updated'
            body += '\nTitle and body updated through the service.'
            response = client.patch(issue_path, json={'title': title, 'body': body})
            assert response.status_code == 200
            assert response.json()['title'] == title and response.json()['body'] == body
            response = client.get(issue_path)
            assert response.status_code == 200
            assert response.json()['title'] == title and response.json()['body'] == body

            for state in ('closed', 'open'):
                response = client.patch(issue_path, json={'state': state})
                assert response.status_code == 200
                assert response.json()['state'] == state
                response = client.get(issue_path)
                assert response.status_code == 200 and response.json()['state'] == state

            comment_body = f'Live integration comment {unique}'
            response = client.post(f'{issue_path}/comments', json={'body': comment_body})
            assert response.status_code == 201
            comment = response.json()
            assert type(comment.get('id')) is int and comment['id'] > 0
            assert comment['body'] == comment_body
            response = client.get(f'{issue_path}/comments', params={'per_page': 100})
            assert response.status_code == 200
            assert any(row['id'] == comment['id'] and row['body'] == comment_body
                       for row in response.json())

            expected = {('issues', 'opened'), ('issue_comment', 'created')}
            observed = set()
            deadline = time.monotonic() + 30
            while expected - observed:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                response = client.get('webhook/events', timeout=min(3.0, remaining))
                assert response.status_code == 200
                for event in response.json():
                    if event.get('issue_number') == issue_number and event.get('delivery_id'):
                        observed.add((event.get('event'), event.get('action')))
                if expected - observed:
                    time.sleep(max(0, min(1, deadline - time.monotonic())))
            assert not expected - observed, (
                f'Missing genuine webhook deliveries for test issue {issue_number}: '
                f'{sorted(expected - observed)}. Check webhook URL, both event subscriptions, '
                'signature secret, and that the same single-process service receives deliveries.'
            )
        finally:
            if issue_number is not None:
                response = client.patch(f'issues/{issue_number}', json={'state': 'closed'})
                assert response.status_code == 200 and response.json().get('state') == 'closed', (
                    f'Cleanup could not close test-created issue {issue_number}; close it manually.'
                )

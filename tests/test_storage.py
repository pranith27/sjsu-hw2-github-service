import json
import logging
from concurrent.futures import ThreadPoolExecutor

import pytest
from app import storage


@pytest.fixture(autouse=True)
def empty_store():
    storage.events.clear()
    storage.processed_deliveries.clear()
    yield
    storage.events.clear()
    storage.processed_deliveries.clear()


def test_delivery_action_key_and_snapshot():
    storage.save_event('one', 'issues', 'opened', 1)
    storage.save_event('one', 'issues', 'closed', 1)
    storage.save_event('one', 'issues', 'opened', 1)
    rows = storage.get_events()
    assert len(rows) == 2
    rows[0]['action'] = 'corrupted'
    assert storage.get_events()[0]['action'] == 'opened'
    assert storage.get_events(0) == []


def test_concurrent_duplicate_delivery():
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _: storage.save_event('same', 'issues', 'opened', 1), range(100)))
    assert len(storage.get_events()) == 1


def test_logger_json_request_context_and_extra_allowlist():
    import app.logger as module
    assert hasattr(module, 'request_id_var')
    token = module.request_id_var.set('test-request')
    try:
        record = logging.LogRecord('github-service', logging.INFO, '', 0, 'Webhook received', (), None)
        record.delivery_id = 'delivery-1'
        record.authorization = 'secret-token'
        record.body = 'private body'
        record.signature = 'raw-signature'
        result = json.loads(module.JsonFormatter().format(record))
        assert result['request_id'] == 'test-request'
        assert result['delivery_id'] == 'delivery-1'
        assert result['message'] == 'Webhook received'
        assert not {'authorization', 'body', 'signature'} & result.keys()
    finally:
        module.request_id_var.reset(token)

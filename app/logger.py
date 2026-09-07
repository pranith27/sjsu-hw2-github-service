import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str | None] = ContextVar('request_id', default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            'timestamp': datetime.fromtimestamp(record.created, UTC).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'request_id': request_id_var.get(),
        }
        # Only explicitly safe summary fields; never serialize all LogRecord extras.
        for key in ('method', 'path', 'status_code', 'duration_ms', 'delivery_id',
                    'event', 'action', 'issue_number', 'duplicate'):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data)


logger = logging.getLogger('github-service')
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logger.propagate = False

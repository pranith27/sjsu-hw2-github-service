PYTHON ?= python

.PHONY: install test lint openapi integration run
install:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -m "not live" --cov=app --cov-report=term-missing --cov-fail-under=80

lint:
	$(PYTHON) -m ruff check app tests scripts

openapi:
	$(PYTHON) scripts/export_openapi.py

integration:
	RUN_LIVE_INTEGRATION=1 $(PYTHON) -m pytest -m live tests/test_integration.py -v

run:
	$(PYTHON) -m uvicorn app.main:app --host 127.0.0.1 --port $${PORT:-8000}

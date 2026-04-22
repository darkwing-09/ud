.PHONY: dev worker beat test lint typecheck migrate shell

# ── Local Development ─────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.workers.celery_app worker --loglevel=info --concurrency=4 -Q high,default,low

beat:
	celery -A app.workers.celery_app beat --loglevel=info

flower:
	celery -A app.workers.celery_app flower --port=5555

# ── Database ──────────────────────────────────────────────────
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"

downgrade:
	alembic downgrade -1

# ── Testing ───────────────────────────────────────────────────
test:
	pytest tests/ -v --cov=app --cov-report=term-missing

test-auth:
	pytest tests/test_auth.py -v

test-fast:
	pytest tests/ -v -x --no-header -q

# ── Code Quality ──────────────────────────────────────────────
lint:
	ruff check app/ tests/

fmt:
	ruff format app/ tests/

typecheck:
	mypy app/

check: lint typecheck
	@echo "✅ All checks passed"

# ── Docker ────────────────────────────────────────────────────
up:
	cd .. && docker compose up -d

down:
	cd .. && docker compose down

logs:
	cd .. && docker compose logs -f api

# ── Utilities ─────────────────────────────────────────────────
shell:
	ipython

seed:
	python -m app.db.seed

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete

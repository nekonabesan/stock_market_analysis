.PHONY: build start stop logs migrate seed test

COMPOSE := docker compose
MIGRATION_MSG ?= auto_migration
TEST_PATH ?= tests/

build:
	$(COMPOSE) down --rmi all --volumes --remove-orphans
	$(COMPOSE) build --no-cache

start:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

migrate:
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "$(MIGRATION_MSG)"
	$(COMPOSE) exec api uv run alembic upgrade head

seed:
	$(COMPOSE) exec api uv run python -m seeds.run

test:
	$(COMPOSE) exec api uv run --dev pytest $(filter-out $@,$(MAKECMDGOALS)) -v

%:
	@:

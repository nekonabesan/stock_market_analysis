.PHONY: build build-clean start stop logs migrate seed init test init-migration
init-migration:
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "init"

COMPOSE := docker compose
MIGRATION_MSG ?= auto_migration
TEST_PATH ?= tests/

build:
	$(COMPOSE) down --rmi all --remove-orphans
	$(COMPOSE) build --no-cache

build-clean:
	$(COMPOSE) down --rmi all --volumes --remove-orphans
	$(COMPOSE) build --no-cache

start:
	$(COMPOSE) up -d --no-build

stop:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

migrate:
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "$(MIGRATION_MSG)"
	$(COMPOSE) exec api uv run alembic upgrade head

seed:
	$(COMPOSE) exec api uv run python -m seeds.run

init:
	$(COMPOSE) exec api uv run python -m app.batch.init_market_data

test:
	$(COMPOSE) exec api uv run --dev pytest $(filter-out $@,$(MAKECMDGOALS)) -v

%:
	@:

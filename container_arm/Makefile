# Copied from container/Makefile and kept same behavior for ARM
.PHONY: build build-clean start stop logs migrate seed init test init-migration
init-migration:
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "init"

MIGRATION_MSG ?= auto_migration
TEST_PATH ?= tests/

# Pin project name so down/build-clean only affect this compose stack.
COMPOSE := $(shell (docker compose version >/dev/null 2>&1 && echo "docker compose -p stock_market_arm") || (docker-compose --version >/dev/null 2>&1 && echo "docker-compose -p stock_market_arm") || echo "docker-compose -p stock_market_arm")

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
	$(COMPOSE) exec api uv run alembic upgrade head
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "$(MIGRATION_MSG)"
	$(COMPOSE) exec api uv run alembic upgrade head

# Explicit alembic helpers
.PHONY: revision upgrade downgrade alembic-current alembic-history
revision:
	$(COMPOSE) exec api uv run alembic revision --autogenerate -m "$(MIGRATION_MSG)"

upgrade:
	$(COMPOSE) exec api uv run alembic upgrade head

downgrade:
	$(COMPOSE) exec api uv run alembic downgrade -1

alembic-current:
	$(COMPOSE) exec api uv run alembic current

alembic-history:
	$(COMPOSE) exec api uv run alembic history --verbose

seed:
	$(COMPOSE) exec api uv run python -m seeds.run

init:
	$(COMPOSE) exec api uv run python -m app.batch.init_market_data

test:
	$(COMPOSE) exec api uv run --dev pytest $(filter-out $@,$(MAKECMDGOALS)) -v

%:
	@:

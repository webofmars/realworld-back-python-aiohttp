prerequisites-check:
	@which docker
	@docker compose version

.env:
	@cp .env.default .env

check:
	@mypy
	@ruff format --check
	@ruff check

format:
	@ruff format

fix: format
	@ruff check --fix

db-up: prerequisites-check
	@docker compose up -d postgres

db-down: prerequisites-check
	@docker compose down

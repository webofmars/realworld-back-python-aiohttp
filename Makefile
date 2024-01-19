check:
	@which docker
	@docker compose version

.env:
	@cp .env.default .env

db-up: check
	@docker compose up -d postgres

db-down: check
	@docker compose down

.PHONY: check db-up db-down

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

e2e-tests: .env prerequisites-check
	docker compose run --rm --build e2e-tests

down: prerequisites-check
	docker compose down --rmi all

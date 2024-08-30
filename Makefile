.PHONY: format lint check test ci help

default: help

format:
	@echo "\n\033[1;34m==> Formatting code with Black...\033[0m"
	black src

lint:
	@echo "\n\033[1;34m==> Running lint checks with ruff...\033[0m"
	ruff check src
	@echo "\n\033[1;34m==> Running black check...\033[0m"
	black --check src
	@echo "\n\033[1;34m==> Running mypy checks...\033[0m"
	mypy --strict --disable-error-code=type-arg --disable-error-code=no-untyped-call --ignore-missing-import --disable-error-code=unused-ignore src

test:
	@echo "\n\033[1;34m==> Running tests...\033[0m"
	pytest

ci: lint test
	@echo "\n\033[1;32m==> All CI checks completed successfully.\033[0m"

help:
	@echo "\033[1;33mAvailable targets:\033[0m"
	@echo "  \033[1;32mformat\033[0m  - Format code with Black"
	@echo "  \033[1;32mlint\033[0m    - Run lint checks with ruff and black"
	@echo "  \033[1;32mtest\033[0m    - Run tests with tox"
	@echo "  \033[1;32mci\033[0m      - Run all CI checks (lint, check, test)"
	@echo "  \033[1;32mhelp\033[0m    - Display this help message"

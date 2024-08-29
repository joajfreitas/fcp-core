.PHONY: format lint check test ci help

default: help

# Formatting code with Black
format:
	@echo "\033[1;34m==> Formatting code with Black...\033[0m"
	black src

# Linting code with ruff and black
lint:
	@echo "\033[1;34m==> Running lint checks with ruff...\033[0m"
	ruff src
	@echo "\033[1;34m==> Running black check...\033[0m"
	black --check --verbose src

# Type checking with mypy
typecheck:
	@echo "\033[1;34m==> Running mypy checks...\033[0m"
	mypy --strict --disable-error-code=type-arg --disable-error-code=no-untyped-call src

# Run tests
test:
	@echo "\033[1;34m==> Running tests...\033[0m"
	tox -e py

# Run all CI checks (lint, check, test)
ci: lint typecheck test
	@echo "\033[1;32m==> All CI checks completed successfully.\033[0m"

# Display help message
help:
	@echo "\033[1;33mAvailable targets:\033[0m"
	@echo "  \033[1;32mformat\033[0m  - Format code with Black"
	@echo "  \033[1;32mlint\033[0m    - Run lint checks with ruff and black"
	@echo "  \033[1;32mtypecheck\033[0m   - Run mypy type checks"
	@echo "  \033[1;32mtest\033[0m    - Run tests with tox"
	@echo "  \033[1;32mci\033[0m      - Run all CI checks (lint, check, test)"
	@echo "  \033[1;32mhelp\033[0m    - Display this help message"

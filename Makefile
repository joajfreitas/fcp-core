SRC:=src
RUN_UNDER?=

.PHONY: format ruff format_check mypy lint check test ci help

default: help

format:
	@echo -e "\033[1;34m==> Formatting code with Black...\033[0m"
	$(RUN_UNDER) black $(SRC)

ruff:
	@echo -e "\033[1;34m==> Running lint checks with ruff...\033[0m"
	$(RUN_UNDER) ruff check $(SRC)

format_check:
	@echo -e "\033[1;34m==> Running black check...\033[0m"
	$(RUN_UNDER) black --check $(SRC)

mypy:
	@echo -e "\033[1;34m==> Running mypy checks...\033[0m"
	$(RUN_UNDER) mypy --strict --disable-error-code=type-arg --disable-error-code=no-untyped-call --ignore-missing-import --disable-error-code=unused-ignore $(SRC)

lint: ruff format_check mypy

test:
	@echo -e "\033[1;34m==> Running tests...\033[0m"
	$(RUN_UNDER) tox -e py

ci: lint test
	@echo -e "\n\033[1;32m==> All CI checks completed successfully.\033[0m"

help:
	@echo -e "\033[1;33mAvailable targets:\033[0m"
	@echo -e "\t\033[1;32mformat\033[0m  - Format code with Black"
	@echo -e "\t\033[1;32mlint\033[0m    - Run lint checks with ruff and black"
	@echo -e "\t\033[1;32mtest\033[0m    - Run tests with tox"
	@echo -e "\t\033[1;32mci\033[0m      - Run all CI checks (lint, check, test)"
	@echo -e "\t\033[1;32mhelp\033[0m    - Display this help message"

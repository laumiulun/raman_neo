.PHONY: help install install-dev lint format test cov build clean demo

help:
	@echo "install      install the package"
	@echo "install-dev  install with dev + test extras and pre-commit hooks"
	@echo "lint         run ruff lint checks"
	@echo "format       auto-format with ruff"
	@echo "test         run the test suite"
	@echo "cov          run tests with coverage report"
	@echo "build        build sdist + wheel"
	@echo "demo         run the bundled example fit"
	@echo "clean        remove build/cache artifacts"

install:
	python -m pip install .

install-dev:
	python -m pip install -e ".[dev]"
	pre-commit install || true

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

test:
	python -m pytest

cov:
	python -m pytest --cov=raman_neo --cov-report=term-missing

build:
	python -m build

demo:
	raman_neo -i test_inputs/test_raman.ini

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache htmlcov .coverage
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf result *.log

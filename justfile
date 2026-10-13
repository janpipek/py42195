_:
    @just --list

# Test for this version
test:
    uv run pytest

# Test for multiple version using nox
nox:
    uvx --with nox nox

# Test typing with mypy (we want this to succeed)
mypy:
    uv run mypy src/ tests/

# Test with pyright (we don't aim yet)
pyright:
    uv run --python 3.11 --with pyright pyright src/ tests/

# Run all the pre-commit checks on the whole code-base
pre-commit:
    uvx pre-commit run --all

# Build the package
build:
    rm -rf dist/
    uv build
    rm -rf src/physt.egg-info

# Publish to PyPI (via twine)
publish: build
    uvx twine upload dist/*

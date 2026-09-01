test:
    uv run pytest

mypy:
    # Test typing with mypy (we want this to succeed)
    uv run mypy src/ tests/

pyright:
    # Optionally test with pyright (we don't aim yet)
    uv run --python 3.12 --with pyright pyright

pre-commit:
    # Run all the pre-commit checks on the whole code-base
    uvx pre-commit run --all

build:
    rm -rf dist/
    uv build
    rm -rf src/physt.egg-info

publish: build
    uv publish

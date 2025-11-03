# Show the list of available commands
@help:
    just --list

# Lint and typecheck the codebase
[group("Code Quality")]
lint *paths:
    uv run ruff check {{ paths }}
    uv run ruff format --check {{ paths }}
    uv run ty check {{ paths }}

# Format the codebase
[group("Code Quality")]
format *paths:
    uv run ruff format {{ paths }}
    uv run ruff check --fix {{ paths }}
    just --fmt --unstable

# Run the test suite
[group("Tests")]
test:
    uv run pytest -v
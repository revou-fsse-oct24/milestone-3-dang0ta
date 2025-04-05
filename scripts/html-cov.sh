#!/bin/sh

uv run coverage run -m pytest -v && \
    uv run coverage report --show-missing && \
    uv run coverage html && open htmlcov/index.html   
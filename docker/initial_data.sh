#!/bin/bash
set -e  # exit on error

echo "Initializing database data..."
poetry run python src/initial_data.py

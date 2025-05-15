#!/bin/bash
set -e

echo "Starting test environment..."
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d --build

echo "Waiting for services to settle..."
sleep 1

echo "Running tests..."
docker compose -f docker-compose.test.yml exec -T app pytest -s --tb=short tests/
EXIT_CODE=$?

echo "Stopping test environment..."
docker compose -f docker-compose.test.yml down -v

exit $EXIT_CODE

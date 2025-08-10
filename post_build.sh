#!/bin/bash
set -e

echo "Installing form dependencies..."
pip install Flask-WTF WTForms email-validator

if [ -f tests/requirements-test.txt ]; then
  echo "Installing test dependencies..."
  pip install -r tests/requirements-test.txt
fi

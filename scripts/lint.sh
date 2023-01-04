#!/usr/bin/env bash

set -x
cd ..
mypy ./pynostr
black ./pynostr --check
isort --recursive --check-only ./pynostr
flake8 ./pynostr

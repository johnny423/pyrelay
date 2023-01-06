#!/usr/bin/env bash

set -x
cd ..
mypy ./pyrelay
black ./pyrelay --check
isort --recursive --check-only ./pyrelay
flake8 ./pyrelay

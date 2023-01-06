#!/bin/sh -e
set -x

cd ..
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ./pyrelay --exclude=__init__.py
black ./pyrelay
isort --recursive --apply ./pyrelay

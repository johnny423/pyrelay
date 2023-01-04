#!/bin/sh -e
set -x

cd ..
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ./pynostr --exclude=__init__.py
black ./pynostr
isort --recursive --apply ./pynostr

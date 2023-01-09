#!/usr/bin/env bash

set -e
set -x

pytest --cov=pyrelay --cov-report=term-missing ../tests "${@}"

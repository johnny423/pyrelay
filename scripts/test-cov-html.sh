#!/usr/bin/env bash

set -e
set -x

bash test.sh --cov-report=html "${@}"

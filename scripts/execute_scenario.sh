#! /usr/bin/env bash

# Exit in case of error
set -e

cd ..
python pynostr/relay/server.py &
sleep 3
python pynostr/client/producer_client.py &
python pynostr/client/watcher_client.py

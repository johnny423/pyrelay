#! /usr/bin/env bash

# Exit in case of error
set -e

cd ..

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
python pyrelay/relay/server.py &
sleep 3
python pyrelay/client/producer_client.py &
python pyrelay/client/watcher_client.py &
tail -f /dev/null


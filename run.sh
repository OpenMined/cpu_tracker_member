#!/bin/sh
set -e

# setup once
uv venv -p 3.12 .venv
uv pip install -U -r requirements.txt
. .venv/bin/activate

while true; do
    echo "Running 'cpu_tracker_member' with $(python3 --version) at '$(which python3)'"
    python3 main.py

    echo "Sleeping for 10 seconds..."
    sleep 10
done

deactivate

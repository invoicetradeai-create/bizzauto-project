#!/bin/bash

# This line ensures that all output from this script is sent to the logs.
exec > >(tee /dev/stdout) 2> >(tee /dev/stderr >&2)

echo "--- [DEBUG] run.sh script has started ---"

echo "--- [DEBUG] Starting Uvicorn in the foreground... ---"
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}

echo "--- [DEBUG] This line should not be reached if Uvicorn starts correctly. ---"

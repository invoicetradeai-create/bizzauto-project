#!/bin/bash
# Start the worker in the background (&)
python worker.py &

# Start the main web server in the foreground
uvicorn main:app --host 0.0.0.0 --port $PORT

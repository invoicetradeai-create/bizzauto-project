#!/bin/bash
# Start the worker in the background (&)
python worker.py &
uvicorn main:app --host 0.0.0.0 --port $PORT

#!/bin/bash
# Start the worker in the background (&)
python worker.py &
python scheduler_worker.py &
uvicorn main:app --host 0.0.0.0 --port $PORT

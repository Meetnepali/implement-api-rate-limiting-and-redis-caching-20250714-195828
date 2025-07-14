#!/bin/bash
set -e
bash install.sh
source .venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 1
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "SUCCESS: FastAPI server is running at http://localhost:8000"
else
    echo "ERROR: FastAPI server failed to start."
    exit 1
fi

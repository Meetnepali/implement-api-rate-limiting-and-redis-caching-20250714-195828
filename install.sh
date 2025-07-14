#!/bin/bash
set -e
if ! command -v python3 &>/dev/null; then
    echo 'python3 not found. Installing...'
    apt-get update && apt-get install -y python3 python3-pip python3-venv
fi
if ! command -v pip3 &>/dev/null; then
    echo 'pip3 not found. Installing...'
    apt-get update && apt-get install -y python3-pip
fi
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "All Python dependencies installed."

#!/bin/bash
# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate venv
if [ -f "$DIR/venv/bin/activate" ]; then
    source "$DIR/venv/bin/activate"
else
    echo "Virtual environment not found in $DIR/venv. Please create it or install dependencies."
    exit 1
fi

echo "Starting Backend API..."
# Run from the script directory so imports work
cd "$DIR"

python3 -m backend.main &
BACKEND_PID=$!

echo "Waiting for Backend to initialize..."
sleep 5

echo "Starting Streamlit Frontend..."
streamlit run app.py --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo "App running. Press Ctrl+C to stop."
wait $BACKEND_PID $FRONTEND_PID

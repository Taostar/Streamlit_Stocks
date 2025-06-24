#!/usr/bin/env bash
set -e # stop on first error

# Start the Streamlit app in the background
echo "Starting Streamlit app on port 8501..."
streamlit run app.py --server.port 8501 &
STREAMLIT_PID=$!
echo "Streamlit app PID: $STREAMLIT_PID"



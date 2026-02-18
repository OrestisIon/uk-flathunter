#!/bin/bash

# Flathunter scheduled execution script
# This script runs the flathunter application with proper environment setup

# Set the working directory to the flathunter project root
cd "$(dirname "$0")" || exit 1

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Use the correct Python interpreter (where packages are installed)
PYTHON="/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"

# Log file location
LOG_DIR="$HOME/.flathunter/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/flathunter_$(date +%Y%m%d_%H%M%S).log"

# Run flathunter and log output
echo "=== Flathunter run started at $(date) ===" >> "$LOG_FILE"
"$PYTHON" flathunt.py --config config.yaml >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
echo "=== Flathunter run completed at $(date) with exit code $EXIT_CODE ===" >> "$LOG_FILE"

# Keep only last 30 days of logs
find "$LOG_DIR" -name "flathunter_*.log" -mtime +30 -delete

exit $EXIT_CODE

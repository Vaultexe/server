#!/bin/bash

# Exit in case of error
set -e

# Set the module name to app.main
if [ -f ./app/main.py ]; then
    MODULE_NAME=app.main
elif [ -f ./main.py ]; then
    MODULE_NAME=main
else
    echo "Error: main module file not found"
    exit 1
fi

# Set the app module to module:app
export APP_MODULE="$MODULE_NAME:app"

# Set host and port
HOST=${HOST?backend host undefined}
PORT=${BACKEND_DEV_PORT?PORT undefined}
LOG_LEVEL=${LOG_LEVEL:-info}

# Start Uvicorn
exec uvicorn "$APP_MODULE" --reload --host $HOST --port $PORT --proxy-headers --log-level $LOG_LEVEL

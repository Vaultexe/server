#!/bin/bash

# Start the server
# $@ is the command line arguments passed to the script
# $@ is the command in the CMD directive in the Dockerfile
exec "$@"

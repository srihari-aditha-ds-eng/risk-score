#!/bin/bash

# Check if a document path is provided
if [ "$1" != "" ]; then
    # Run with the specified document
    docker-compose run --rm risk-analyzer --document "$1"
else
    # Run with the default document
    docker-compose run --rm risk-analyzer
fi 